#!/usr/bin/env python3
"""
Test the search functionality without requiring OpenAI API.
"""
import numpy as np
from database import WorkspaceIndexDB
from embedding_utils import unpack_embedding, cosine_similarity
from pathlib import Path
from rich.console import Console
from rich.table import Table

console = Console()

# Simulate a query embedding (in reality this would come from OpenAI)
query_text = "authentication function"
console.print(f"\n[cyan]Searching for: '{query_text}'[/cyan]\n")
console.print("[yellow]Note: Using random query embedding for demo (normally would use OpenAI)[/yellow]\n")

# Create a random query embedding (512 dimensions)
query_embedding = np.random.randn(512).astype(np.float32)

# Search the database
db_path = Path("test_index.db")
with WorkspaceIndexDB(db_path) as db:
    files = db.get_all_files()
    
    results = []
    for file in files:
        for chunk in file.chunks:
            chunk_emb = unpack_embedding(chunk.embedding)
            similarity = cosine_similarity(query_embedding, chunk_emb)
            results.append((similarity, file.path, chunk))
    
    # Sort by similarity
    results.sort(reverse=True, key=lambda x: x[0])
    
    # Display results
    table = Table(title="Search Results")
    table.add_column("Rank", style="cyan")
    table.add_column("File", style="green")
    table.add_column("Similarity", style="magenta")
    table.add_column("Preview", style="white", max_width=60)
    
    for i, (similarity, file_path, chunk) in enumerate(results[:5], 1):
        preview = chunk.text[:80].replace("\n", " ")
        table.add_row(
            str(i),
            file_path.split("/")[-1],
            f"{similarity:.4f}",
            preview
        )
    
    console.print(table)
    console.print(f"\n[green]✓ Found {len(results)} chunks total[/green]")

