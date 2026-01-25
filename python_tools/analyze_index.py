#!/usr/bin/env python3
"""
Example: Analyze code patterns in the indexed workspace.
"""

from pathlib import Path
from collections import Counter, defaultdict
from rich.console import Console
from rich.table import Table

from database import WorkspaceIndexDB, find_database_path


def analyze_index(db_path: Path):
    """Analyze patterns in the indexed workspace."""
    console = Console()

    with WorkspaceIndexDB(db_path) as db:
        meta = db.get_metadata()
        files = db.get_all_files()

        # Statistics
        file_extensions = Counter()
        chunks_per_file = []
        total_chunk_text = 0
        chunk_sizes = []

        for file in files:
            # Extract extension
            path = file.file_path
            if '.' in path:
                ext = path.rsplit('.', 1)[1]
                file_extensions[ext] += 1

            # Chunk stats
            chunks_per_file.append(len(file.chunks))

            for chunk in file.chunks:
                chunk_sizes.append(len(chunk.text))
                total_chunk_text += len(chunk.text)

        # Display results
        console.print("\n[bold cyan]📊 Workspace Index Analysis[/bold cyan]\n")

        # Overview
        console.print(f"[bold]Total Files:[/bold] {len(files)}")
        console.print(f"[bold]Total Chunks:[/bold] {sum(chunks_per_file)}")
        console.print(f"[bold]Average Chunks per File:[/bold] {sum(chunks_per_file) / len(files) if files else 0:.1f}")
        console.print(f"[bold]Total Code Text:[/bold] {total_chunk_text / 1024 / 1024:.2f} MB")

        if chunk_sizes:
            console.print(f"[bold]Average Chunk Size:[/bold] {sum(chunk_sizes) / len(chunk_sizes):.0f} characters")
            console.print(f"[bold]Min Chunk Size:[/bold] {min(chunk_sizes)} characters")
            console.print(f"[bold]Max Chunk Size:[/bold] {max(chunk_sizes)} characters")

        # File extensions
        console.print("\n[bold yellow]File Types:[/bold yellow]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Extension", style="cyan")
        table.add_column("Count", justify="right", style="green")
        table.add_column("Percentage", justify="right", style="yellow")

        for ext, count in file_extensions.most_common(10):
            percentage = (count / len(files)) * 100
            table.add_row(f".{ext}", str(count), f"{percentage:.1f}%")

        console.print(table)

        # Most chunked files
        console.print("\n[bold yellow]Most Chunked Files:[/bold yellow]")
        files_with_chunks = [(f, len(f.chunks)) for f in files]
        files_with_chunks.sort(key=lambda x: x[1], reverse=True)

        for i, (file, chunk_count) in enumerate(files_with_chunks[:10], 1):
            console.print(f"  {i}. {file.file_path} - [green]{chunk_count} chunks[/green]")


def main():
    """Main entry point."""
    import sys
    console = Console()

    if len(sys.argv) > 1:
        db_path = Path(sys.argv[1])
    else:
        db_path = find_database_path()

        if not db_path:
            console.print("[red]❌ Could not find workspace-chunks.db automatically.[/red]")
            sys.exit(1)

    if not db_path.exists():
        console.print(f"[red]❌ Database not found: {db_path}[/red]")
        sys.exit(1)

    try:
        analyze_index(db_path)
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
