"""
Database access layer for Copilot Chat workspace index.
"""

import sqlite3
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from embedding_utils import unpack_embedding


@dataclass
class CodeChunk:
    """Represents a code chunk with its embedding."""
    text: str
    start_line: int
    start_column: int
    end_line: int
    end_column: int
    embedding: 'np.ndarray'
    chunk_hash: str

    @property
    def range_str(self) -> str:
        """Human-readable range string."""
        return f"L{self.start_line}:{self.start_column}-L{self.end_line}:{self.end_column}"


@dataclass
class IndexedFile:
    """Represents an indexed file with its chunks."""
    uri: str
    content_version_id: Optional[str]
    chunks: List[CodeChunk]

    @property
    def file_path(self) -> str:
        """Extract file path from URI."""
        if self.uri.startswith("file://"):
            return self.uri[7:]  # Remove "file://" prefix
        return self.uri


class WorkspaceIndexDB:
    """Database connection and query interface for the workspace index."""

    def __init__(self, db_path: Path):
        """
        Initialize database connection.

        Args:
            db_path: Path to workspace-chunks.db
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(str(db_path))
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

    def get_metadata(self) -> Dict[str, str]:
        """
        Get index metadata (version and embedding model).

        Returns:
            Dictionary with 'version' and 'embedding_model' keys
        """
        self.cursor.execute("SELECT version, embeddingModel FROM CacheMeta LIMIT 1")
        row = self.cursor.fetchone()

        if row:
            return {
                'version': row[0],
                'embedding_model': row[1]
            }
        return {'version': None, 'embedding_model': None}

    def get_file_count(self) -> int:
        """Get total number of indexed files."""
        self.cursor.execute("SELECT COUNT(*) FROM Files")
        return self.cursor.fetchone()[0]

    def get_chunk_count(self) -> int:
        """Get total number of code chunks."""
        self.cursor.execute("SELECT COUNT(*) FROM FileChunks")
        return self.cursor.fetchone()[0]

    def get_all_files(self) -> List[IndexedFile]:
        """
        Get all indexed files with their chunks.

        Returns:
            List of IndexedFile objects
        """
        meta = self.get_metadata()
        embedding_model = meta['embedding_model']

        self.cursor.execute("""
            SELECT id, uri, contentVersionId
            FROM Files
            ORDER BY uri
        """)

        files = []
        for file_id, uri, version_id in self.cursor.fetchall():
            chunks = self._get_chunks_for_file(file_id, embedding_model)
            files.append(IndexedFile(
                uri=uri,
                content_version_id=version_id,
                chunks=chunks
            ))

        return files

    def get_file_by_uri(self, uri: str) -> Optional[IndexedFile]:
        """
        Get a specific file by its URI.

        Args:
            uri: File URI (e.g., "file:///path/to/file.ts")

        Returns:
            IndexedFile object or None if not found
        """
        meta = self.get_metadata()
        embedding_model = meta['embedding_model']

        self.cursor.execute("""
            SELECT id, contentVersionId
            FROM Files
            WHERE uri = ?
        """, (uri,))

        row = self.cursor.fetchone()
        if not row:
            return None

        file_id, version_id = row
        chunks = self._get_chunks_for_file(file_id, embedding_model)

        return IndexedFile(
            uri=uri,
            content_version_id=version_id,
            chunks=chunks
        )

    def _get_chunks_for_file(self, file_id: int, embedding_model: str) -> List[CodeChunk]:
        """Get all chunks for a given file ID."""
        self.cursor.execute("""
            SELECT
                text,
                range_startLineNumber,
                range_startColumn,
                range_endLineNumber,
                range_endColumn,
                embedding,
                chunkHash
            FROM FileChunks
            WHERE fileId = ?
            ORDER BY range_startLineNumber, range_startColumn
        """, (file_id,))

        chunks = []
        for row in self.cursor.fetchall():
            text, start_line, start_col, end_line, end_col, emb_data, chunk_hash = row

            embedding = unpack_embedding(emb_data, embedding_model)

            chunks.append(CodeChunk(
                text=text,
                start_line=start_line,
                start_column=start_col,
                end_line=end_line,
                end_column=end_col,
                embedding=embedding,
                chunk_hash=chunk_hash
            ))

        return chunks

    def search_files_by_pattern(self, pattern: str) -> List[IndexedFile]:
        """
        Search for files matching a URI pattern.

        Args:
            pattern: SQL LIKE pattern (e.g., "%authentication%")

        Returns:
            List of matching IndexedFile objects
        """
        meta = self.get_metadata()
        embedding_model = meta['embedding_model']

        self.cursor.execute("""
            SELECT id, uri, contentVersionId
            FROM Files
            WHERE uri LIKE ?
            ORDER BY uri
        """, (pattern,))

        files = []
        for file_id, uri, version_id in self.cursor.fetchall():
            chunks = self._get_chunks_for_file(file_id, embedding_model)
            files.append(IndexedFile(
                uri=uri,
                content_version_id=version_id,
                chunks=chunks
            ))

        return files


def find_database_path() -> Optional[Path]:
    """
    Attempt to find the workspace-chunks.db automatically.

    Returns:
        Path to the database or None if not found
    """
    import os
    import platform

    system = platform.system()

    # Determine VS Code storage base path
    if system == "Linux":
        base = Path.home() / ".config" / "Code" / "User" / "workspaceStorage"
    elif system == "Darwin":  # macOS
        base = Path.home() / "Library" / "Application Support" / "Code" / "User" / "workspaceStorage"
    elif system == "Windows":
        base = Path(os.getenv("APPDATA", "")) / "Code" / "User" / "workspaceStorage"
    else:
        return None

    if not base.exists():
        return None

    # Search for workspace-chunks.db in any workspace folder
    for workspace_folder in base.iterdir():
        if not workspace_folder.is_dir():
            continue

        db_path = workspace_folder / "GitHub.copilot-chat" / "workspace-chunks.db"
        if db_path.exists():
            return db_path

    return None
