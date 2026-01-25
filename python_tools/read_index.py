#!/usr/bin/env python3
"""
Read and display information from the Copilot Chat workspace index.
"""

import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from database import WorkspaceIndexDB, find_database_path
from embedding_utils import get_embedding_info


def display_index_info(db_path: Path):
    """Display comprehensive information about the index."""
    console = Console()

    console.print(f"\n[bold cyan]Reading index from:[/bold cyan] {db_path}\n")

    with WorkspaceIndexDB(db_path) as db:
        # Get metadata
        meta = db.get_metadata()
        file_count = db.get_file_count()
        chunk_count = db.get_chunk_count()

        # Display overview
        console.print(Panel.fit(
            f"[bold]Cache Version:[/bold] {meta['version']}\n"
            f"[bold]Embedding Model:[/bold] {meta['embedding_model']}\n"
            f"[bold]Indexed Files:[/bold] {file_count}\n"
            f"[bold]Total Chunks:[/bold] {chunk_count}",
            title="📊 Index Overview",
            border_style="green"
        ))

        # Display embedding model info
        if meta['embedding_model']:
            emb_info = get_embedding_info(meta['embedding_model'])
            console.print(f"\n[bold yellow]Embedding Model Details:[/bold yellow]")
            console.print(f"  Provider: {emb_info.get('provider', 'Unknown')}")
            console.print(f"  Dimensions: {emb_info.get('dimensions', 'Unknown')}")
            console.print(f"  Quantization: {emb_info.get('quantization', 'Unknown')}")
            console.print(f"  Size per embedding: {emb_info.get('size_bytes', 'Unknown')} bytes")

        # List all files
        console.print("\n[bold cyan]Indexed Files:[/bold cyan]")

        files = db.get_all_files()

        # Create table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("File", style="cyan", no_wrap=False)
        table.add_column("Chunks", justify="right", style="green")
        table.add_column("Lines", style="yellow")

        for file in files:
            file_path = file.file_path

            # Calculate total lines covered
            if file.chunks:
                min_line = min(chunk.start_line for chunk in file.chunks)
                max_line = max(chunk.end_line for chunk in file.chunks)
                lines_str = f"{min_line}-{max_line}"
            else:
                lines_str = "N/A"

            table.add_row(
                file_path,
                str(len(file.chunks)),
                lines_str
            )

        console.print(table)

        # Display sample chunk details
        if files and files[0].chunks:
            console.print("\n[bold cyan]Sample Chunk:[/bold cyan]")
            sample_chunk = files[0].chunks[0]

            console.print(Panel(
                f"[bold]File:[/bold] {files[0].file_path}\n"
                f"[bold]Range:[/bold] {sample_chunk.range_str}\n"
                f"[bold]Embedding dimensions:[/bold] {len(sample_chunk.embedding)}\n"
                f"[bold]Text preview:[/bold]\n{sample_chunk.text[:200]}{'...' if len(sample_chunk.text) > 200 else ''}",
                title="📝 Example Chunk",
                border_style="blue"
            ))


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        db_path = Path(sys.argv[1])
    else:
        db_path = find_database_path()

        if not db_path:
            print("❌ Could not find workspace-chunks.db automatically.")
            print("   Please provide the path as an argument:")
            print("   python read_index.py /path/to/workspace-chunks.db")
            sys.exit(1)

    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        sys.exit(1)

    try:
        display_index_info(db_path)
    except Exception as e:
        print(f"❌ Error reading index: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
