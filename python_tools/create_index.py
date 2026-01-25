#!/usr/bin/env python3
"""
Create a workspace index using the same GitHub API that Copilot Chat uses.

This script demonstrates how to:
1. Chunk code files using GitHub's chunking API
2. Generate embeddings using GitHub's embedding API
3. Store the results in a SQLite database (same format as VS Code)

Based on the Copilot Chat indexing implementation:
- src/platform/chunking/common/chunkingEndpointClientImpl.ts
- src/platform/embeddings/common/remoteEmbeddingsComputer.ts
"""

import os
import sys
import json
import hmac
import hashlib
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import requests
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from embedding_utils import packEmbedding
from database import WorkspaceIndexDB


# GitHub API endpoints (same as Copilot Chat)
CAPI_BASE_URL = "https://api.github.com"
EMBEDDINGS_ENDPOINT = f"{CAPI_BASE_URL}/embeddings"
CHUNKING_ENDPOINT = f"{CAPI_BASE_URL}/code-chunks"


@dataclass
class FileChunk:
    """A code chunk from the GitHub API."""
    text: str
    start_line: int
    start_column: int
    end_line: int
    end_column: int
    chunk_hash: str
    embedding: Optional[List[float]] = None


class GitHubIndexingAPI:
    """
    Python wrapper for GitHub's chunking and embedding APIs.

    Uses the same endpoints as Copilot Chat for consistency.
    """

    def __init__(self, github_token: str):
        """
        Initialize the API client.

        Args:
            github_token: GitHub personal access token or Copilot token
        """
        self.github_token = github_token
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {github_token}',
            'Content-Type': 'application/json',
            'User-Agent': 'python-workspace-indexer/1.0'
        })

    def compute_chunks_and_embeddings(
        self,
        file_path: str,
        content: str,
        embedding_model: str = "text-embedding-3-small-512",
        language_id: Optional[int] = None
    ) -> List[FileChunk]:
        """
        Chunk a file and compute embeddings using GitHub's API.

        This is equivalent to:
        IChunkingEndpointClient.computeChunksAndEmbeddings()

        Args:
            file_path: Path to the file (used for language detection)
            content: File content
            embedding_model: Embedding model to use
            language_id: Optional GitHub language ID (from linguist)

        Returns:
            List of FileChunk objects with embeddings
        """
        # Step 1: Request chunking and embeddings
        # Based on: src/platform/chunking/common/chunkingEndpointClientImpl.ts
        payload = {
            "file": {
                "path": file_path,
                "content": content
            },
            "embedding_model": embedding_model,
            "compute_embeddings": True
        }

        if language_id:
            payload["language_id"] = language_id

        try:
            response = self.session.post(
                CHUNKING_ENDPOINT,
                json=payload,
                timeout=60
            )

            if not response.ok:
                raise Exception(f"Chunking API error: {response.status_code} - {response.text}")

            result = response.json()

            # Parse response into FileChunk objects
            chunks = []
            for chunk_data in result.get("chunks", []):
                chunk = FileChunk(
                    text=chunk_data["text"],
                    start_line=chunk_data["range"]["start"]["line"],
                    start_column=chunk_data["range"]["start"]["column"],
                    end_line=chunk_data["range"]["end"]["line"],
                    end_column=chunk_data["range"]["end"]["column"],
                    chunk_hash=chunk_data.get("hash", ""),
                    embedding=chunk_data.get("embedding", {}).get("values")
                )
                chunks.append(chunk)

            return chunks

        except requests.RequestException as e:
            raise Exception(f"Failed to compute chunks and embeddings: {e}")

    def compute_embeddings_only(
        self,
        texts: List[str],
        embedding_model: str = "text-embedding-3-small-512",
        input_type: str = "document"
    ) -> List[List[float]]:
        """
        Compute embeddings for a list of texts.

        This is equivalent to:
        IEmbeddingsComputer.computeEmbeddings()

        Args:
            texts: List of text strings to embed
            embedding_model: Model identifier
            input_type: 'document' or 'query'

        Returns:
            List of embedding vectors
        """
        # Based on: src/platform/embeddings/common/remoteEmbeddingsComputer.ts
        payload = {
            "inputs": texts,
            "input_type": input_type,
            "embedding_model": embedding_model
        }

        try:
            response = self.session.post(
                EMBEDDINGS_ENDPOINT,
                json=payload,
                timeout=30
            )

            if not response.ok:
                raise Exception(f"Embeddings API error: {response.status_code} - {response.text}")

            result = response.json()

            embeddings = [
                emb["embedding"]
                for emb in result.get("embeddings", [])
            ]

            return embeddings

        except requests.RequestException as e:
            raise Exception(f"Failed to compute embeddings: {e}")


def create_index_database(db_path: Path, embedding_model: str = "text-embedding-3-small-512") -> sqlite3.Connection:
    """
    Create a new index database with the same schema as Copilot Chat.

    Schema based on: src/platform/workspaceChunkSearch/node/workspaceChunkAndEmbeddingCache.ts
    """
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Same schema as VS Code
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS CacheMeta (
            version TEXT NOT NULL,
            embeddingModel TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uri TEXT NOT NULL UNIQUE,
            contentVersionId TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS FileChunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fileId INTEGER NOT NULL,
            text TEXT NOT NULL,
            range_startLineNumber INTEGER NOT NULL,
            range_startColumn INTEGER NOT NULL,
            range_endLineNumber INTEGER NOT NULL,
            range_endColumn INTEGER NOT NULL,
            embedding BINARY NOT NULL,
            chunkHash TEXT NOT NULL,
            FOREIGN KEY (fileId) REFERENCES Files(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_uri ON Files(uri)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_filechunks_fileId ON FileChunks(fileId)")

    # Set metadata
    cursor.execute("DELETE FROM CacheMeta")
    cursor.execute("INSERT INTO CacheMeta (version, embeddingModel) VALUES (?, ?)", ("1.0.0", embedding_model))

    conn.commit()
    return conn


def index_file(
    api: GitHubIndexingAPI,
    file_path: Path,
    conn: sqlite3.Connection,
    embedding_model: str = "text-embedding-3-small-512"
) -> int:
    """
    Index a single file and store it in the database.

    Returns:
        Number of chunks indexed
    """
    cursor = conn.cursor()

    # Read file content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Get chunks and embeddings from GitHub API
    chunks = api.compute_chunks_and_embeddings(
        str(file_path),
        content,
        embedding_model
    )

    # Store in database
    file_uri = f"file://{file_path.resolve()}"

    # Insert or update file
    cursor.execute(
        "INSERT OR REPLACE INTO Files (uri, contentVersionId) VALUES (?, ?)",
        (file_uri, str(file_path.stat().st_mtime))
    )
    file_id = cursor.lastrowid

    # Delete old chunks
    cursor.execute("DELETE FROM FileChunks WHERE fileId = ?", (file_id,))

    # Insert chunks
    for chunk in chunks:
        if chunk.embedding:
            # Pack embedding to binary (same as VS Code)
            from embedding_utils import pack_embedding_vector
            packed_emb = pack_embedding_vector(chunk.embedding, embedding_model)

            cursor.execute("""
                INSERT INTO FileChunks
                (fileId, text, range_startLineNumber, range_startColumn,
                 range_endLineNumber, range_endColumn, embedding, chunkHash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                file_id,
                chunk.text,
                chunk.start_line,
                chunk.start_column,
                chunk.end_line,
                chunk.end_column,
                packed_emb,
                chunk.chunk_hash
            ))

    conn.commit()
    return len(chunks)


def main():
    """Main entry point."""
    console = Console()

    # Get GitHub token
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        console.print("[red]❌ GITHUB_TOKEN environment variable not set[/red]")
        console.print("   Get a token from: https://github.com/settings/tokens")
        sys.exit(1)

    if len(sys.argv) < 3:
        console.print("[yellow]Usage: python create_index.py <workspace_dir> <output.db>[/yellow]")
        console.print("\nExample:")
        console.print("  export GITHUB_TOKEN=ghp_xxxx")
        console.print("  python create_index.py /path/to/workspace index.db")
        sys.exit(1)

    workspace_dir = Path(sys.argv[1])
    output_db = Path(sys.argv[2])

    if not workspace_dir.exists():
        console.print(f"[red]❌ Workspace directory not found: {workspace_dir}[/red]")
        sys.exit(1)

    console.print(f"\n[cyan]Creating index for:[/cyan] {workspace_dir}")
    console.print(f"[cyan]Output database:[/cyan] {output_db}\n")

    # Initialize API
    api = GitHubIndexingAPI(github_token)

    # Create database
    conn = create_index_database(output_db)

    # Find all code files
    code_extensions = {'.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.cpp', '.c', '.h', '.go', '.rs', '.rb', '.php'}
    files_to_index = [
        f for f in workspace_dir.rglob('*')
        if f.is_file() and f.suffix in code_extensions
    ]

    console.print(f"Found {len(files_to_index)} files to index\n")

    # Index files with progress bar
    total_chunks = 0
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("Indexing files...", total=len(files_to_index))

        for file_path in files_to_index:
            try:
                progress.update(task, description=f"Indexing {file_path.name}...")
                chunks = index_file(api, file_path, conn, "text-embedding-3-small-512")
                total_chunks += chunks
                progress.advance(task)
            except Exception as e:
                console.print(f"[red]Error indexing {file_path}: {e}[/red]")

    conn.close()

    console.print(f"\n[green]✓ Index created successfully![/green]")
    console.print(f"  Files: {len(files_to_index)}")
    console.print(f"  Chunks: {total_chunks}")
    console.print(f"  Database: {output_db}")
    console.print(f"\nYou can now use read_index.py or search_index.py with this database!")


if __name__ == "__main__":
    main()
