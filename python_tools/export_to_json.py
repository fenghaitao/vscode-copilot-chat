#!/usr/bin/env python3
"""
Export the workspace index to JSON format.
"""

import sys
import json
from pathlib import Path
from rich.console import Console

from database import WorkspaceIndexDB, find_database_path


def export_to_json(db_path: Path, output_path: Path, include_embeddings: bool = False):
    """
    Export the index to JSON format.

    Args:
        db_path: Path to the database
        output_path: Path for the JSON output file
        include_embeddings: Whether to include embedding vectors (makes file large)
    """
    console = Console()

    console.print(f"[cyan]Exporting index from {db_path}...[/cyan]")

    with WorkspaceIndexDB(db_path) as db:
        meta = db.get_metadata()
        files = db.get_all_files()

        # Build JSON structure
        data = {
            "metadata": meta,
            "statistics": {
                "file_count": len(files),
                "total_chunks": sum(len(f.chunks) for f in files)
            },
            "files": []
        }

        for file in files:
            file_data = {
                "uri": file.uri,
                "path": file.file_path,
                "content_version_id": file.content_version_id,
                "chunks": []
            }

            for chunk in file.chunks:
                chunk_data = {
                    "text": chunk.text,
                    "range": {
                        "start": {
                            "line": chunk.start_line,
                            "column": chunk.start_column
                        },
                        "end": {
                            "line": chunk.end_line,
                            "column": chunk.end_column
                        }
                    },
                    "chunk_hash": chunk.chunk_hash,
                    "embedding_dimensions": len(chunk.embedding)
                }

                if include_embeddings:
                    chunk_data["embedding"] = chunk.embedding.tolist()

                file_data["chunks"].append(chunk_data)

            data["files"].append(file_data)

        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        console.print(f"[green]✓ Exported to {output_path}[/green]")
        console.print(f"  Files: {len(files)}")
        console.print(f"  Chunks: {data['statistics']['total_chunks']}")

        file_size = output_path.stat().st_size
        console.print(f"  File size: {file_size / 1024 / 1024:.2f} MB")


def main():
    """Main entry point."""
    console = Console()

    if len(sys.argv) < 2:
        console.print("[yellow]Usage: python export_to_json.py <output.json> [db_path] [--with-embeddings][/yellow]")
        console.print("\nExample:")
        console.print("  python export_to_json.py index.json")
        console.print("  python export_to_json.py index.json /path/to/db --with-embeddings")
        sys.exit(1)

    output_path = Path(sys.argv[1])
    include_embeddings = "--with-embeddings" in sys.argv

    # Find database path
    db_path = None
    for arg in sys.argv[2:]:
        if arg != "--with-embeddings":
            db_path = Path(arg)
            break

    if not db_path:
        db_path = find_database_path()

        if not db_path:
            console.print("[red]❌ Could not find workspace-chunks.db automatically.[/red]")
            sys.exit(1)

    if not db_path.exists():
        console.print(f"[red]❌ Database not found: {db_path}[/red]")
        sys.exit(1)

    try:
        export_to_json(db_path, output_path, include_embeddings)
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
