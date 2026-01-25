#!/usr/bin/env python3
"""
Search the Copilot Chat workspace index for similar code chunks.
"""

import sys
import os
from pathlib import Path
from typing import List, Tuple
import numpy as np
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from database import WorkspaceIndexDB, find_database_path, CodeChunk, IndexedFile
from embedding_utils import cosine_similarity

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


def get_query_embedding(query: str, dimensions: int = 512) -> np.ndarray:
    """
    Get embedding for a search query using OpenAI API.

    Args:
        query: Search query text
        dimensions: Embedding dimensions (512 for text-embedding-3-small)

    Returns:
        NumPy array of embedding values
    """
    if not OPENAI_AVAILABLE:
        raise ImportError("openai package not installed. Run: pip install openai")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    client = openai.OpenAI(api_key=api_key)

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=query,
        dimensions=dimensions
    )

    return np.array(response.data[0].embedding, dtype=np.float32)


def search_chunks(
    db_path: Path,
    query: str,
    top_k: int = 10,
    min_similarity: float = 0.0
) -> List[Tuple[IndexedFile, CodeChunk, float]]:
    """
    Search for the most similar code chunks.

    Args:
        db_path: Path to the database
        query: Search query text
        top_k: Number of results to return
        min_similarity: Minimum similarity threshold

    Returns:
        List of (file, chunk, similarity_score) tuples
    """
    console = Console()

    with WorkspaceIndexDB(db_path) as db:
        meta = db.get_metadata()

        console.print(f"[cyan]Computing query embedding...[/cyan]")

        # Get query embedding
        try:
            query_embedding = get_query_embedding(query)
        except Exception as e:
            console.print(f"[red]Error getting query embedding: {e}[/red]")
            console.print("[yellow]Tip: Set OPENAI_API_KEY environment variable[/yellow]")
            return []

        console.print(f"[cyan]Searching {db.get_chunk_count()} chunks...[/cyan]\n")

        # Search all chunks
        results = []
        files = db.get_all_files()

        for file in files:
            for chunk in file.chunks:
                similarity = cosine_similarity(query_embedding, chunk.embedding)

                if similarity >= min_similarity:
                    results.append((file, chunk, similarity))

        # Sort by similarity (descending)
        results.sort(key=lambda x: x[2], reverse=True)

        return results[:top_k]


def display_results(query: str, results: List[Tuple[IndexedFile, CodeChunk, float]]):
    """Display search results in a nice format."""
    console = Console()

    console.print(Panel(
        f"[bold]Query:[/bold] {query}\n"
        f"[bold]Results:[/bold] {len(results)}",
        title="🔍 Search Results",
        border_style="green"
    ))

    for i, (file, chunk, score) in enumerate(results, 1):
        # Format score with color
        if score >= 0.8:
            score_color = "green"
        elif score >= 0.6:
            score_color = "yellow"
        else:
            score_color = "red"

        console.print(f"\n[bold cyan]Result {i}:[/bold cyan] [{score_color}]{score:.4f}[/{score_color}]")
        console.print(f"[dim]File:[/dim] {file.file_path}")
        console.print(f"[dim]Range:[/dim] {chunk.range_str}")

        # Display chunk text
        text_preview = chunk.text[:300] + "..." if len(chunk.text) > 300 else chunk.text
        console.print(Panel(text_preview, border_style="blue", padding=(0, 1)))


def main():
    """Main entry point."""
    console = Console()

    if len(sys.argv) < 2:
        console.print("[red]Usage: python search_index.py <query> [db_path][/red]")
        console.print("\nExample:")
        console.print("  python search_index.py \"authentication function\"")
        console.print("  python search_index.py \"error handling\" /path/to/workspace-chunks.db")
        sys.exit(1)

    query = sys.argv[1]

    if len(sys.argv) > 2:
        db_path = Path(sys.argv[2])
    else:
        db_path = find_database_path()

        if not db_path:
            console.print("[red]❌ Could not find workspace-chunks.db automatically.[/red]")
            console.print("   Please provide the path as a second argument:")
            console.print("   python search_index.py \"query\" /path/to/workspace-chunks.db")
            sys.exit(1)

    if not db_path.exists():
        console.print(f"[red]❌ Database not found: {db_path}[/red]")
        sys.exit(1)

    console.print(f"[dim]Using database: {db_path}[/dim]\n")

    try:
        results = search_chunks(db_path, query, top_k=10, min_similarity=0.5)
        display_results(query, results)

        if not results:
            console.print("\n[yellow]No results found. Try a different query or lower the similarity threshold.[/yellow]")

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
