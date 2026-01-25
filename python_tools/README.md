# Copilot Chat Index Python Tools

Python utilities to read and query the Copilot Chat workspace index.

## Installation

```bash
cd python_tools

# Run the setup script (creates virtual environment)
bash setup.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

### Read the Index

```bash
python read_index.py
```

### Search for Similar Code

```bash
python search_index.py "authentication function"
```

## API Documentation

See [API.md](API.md) for details on:
- GitHub's chunking and embedding APIs
- How Copilot Chat creates indices
- Python implementation using the same API
- Creating your own indices

## Scripts

### `create_index.py`
Create a new workspace index using GitHub's API (same as Copilot Chat).

```bash
export GITHUB_TOKEN="ghp_xxxx"
python create_index.py /path/to/workspace output.db
```

### `read_index.py`
Read and display all indexed files and chunks from the database.

```bash
source venv/bin/activate
python read_index.py [db_path]
```

### `search_index.py`
Search for similar code chunks using semantic search (requires OpenAI API key).

```bash
export OPENAI_API_KEY="your-api-key"
python search_index.py "authentication function" [db_path]
```

### `analyze_index.py`
Analyze patterns and statistics in the indexed workspace.

```bash
python analyze_index.py [db_path]
```

### `export_to_json.py`
Export the entire index to JSON format.

```bash
python export_to_json.py output.json [db_path] [--with-embeddings]
```

## Module Structure

- `database.py` - Database access layer with SQLite queries
- `embedding_utils.py` - Utilities for unpacking and comparing embeddings
- `setup.sh` - Automated setup script

## Finding Your Database

The database is typically located at:
- **Linux**: `~/.config/Code/User/workspaceStorage/{workspace-id}/GitHub.copilot-chat/workspace-chunks.db`
- **macOS**: `~/Library/Application Support/Code/User/workspaceStorage/{workspace-id}/GitHub.copilot-chat/workspace-chunks.db`
- **Windows**: `%APPDATA%\Code\User\workspaceStorage\{workspace-id}\GitHub.copilot-chat\workspace-chunks.db`

The scripts will auto-detect the database if you don't specify a path.
