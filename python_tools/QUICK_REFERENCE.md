# Quick Reference Guide

## 🚀 One-Line Commands

### View Index
```bash
python read_index.py
```

### Analyze Statistics
```bash
python analyze_index.py test_index.db
```

### Export to JSON
```bash
python export_to_json.py output.json /path/to/db
```

### Search (needs API key)
```bash
OPENAI_API_KEY=sk-xxx python search_index.py db.sqlite "query"
```

### Create Index (needs GitHub token)
```bash
GITHUB_TOKEN=ghp_xxx python create_index.py /workspace/path
```

---

## 📍 Database Locations

**Linux:**
```
~/.config/Code/User/globalStorage/github.copilot-chat/workspace-chunks.db
```

**macOS:**
```
~/Library/Application Support/Code/User/globalStorage/github.copilot-chat/workspace-chunks.db
```

**Windows:**
```
%APPDATA%\Code\User\globalStorage\github.copilot-chat\workspace-chunks.db
```

---

## 🔑 Environment Variables

```bash
export GITHUB_TOKEN="ghp_your_github_token"
export OPENAI_API_KEY="sk-your_openai_key"
```

---

## 📊 Embedding Models

| Model | Provider | Dimensions | Size | Quantization |
|-------|----------|------------|------|--------------|
| text-embedding-3-small-512 | OpenAI | 512 | 2KB | float32 |
| metis-1024-I16-Binary | GitHub | 1024 | 128B | binary |

---

## ⚡ GitHub API Endpoints

**Chunking:**
```
POST https://api.githubcopilot.com/code-chunks
```

**Embeddings:**
```
POST https://api.githubcopilot.com/embeddings
```

**Rate Limit:** 40 requests/second

---

## 🗄️ Database Schema

```sql
CREATE TABLE CacheMeta (
    version TEXT,
    embeddingModel TEXT
);

CREATE TABLE Files (
    id INTEGER PRIMARY KEY,
    uri TEXT NOT NULL,
    contentVersionId TEXT
);

CREATE TABLE FileChunks (
    id INTEGER PRIMARY KEY,
    fileId INTEGER,
    text TEXT,
    range_startLineNumber INTEGER,
    range_startColumn INTEGER,
    range_endLineNumber INTEGER,
    range_endColumn INTEGER,
    embedding BINARY,
    chunkHash TEXT
);
```

---

## 🎯 Common Use Cases

### 1. View What's Indexed
```bash
python read_index.py
```

### 2. Check File Type Distribution
```bash
python analyze_index.py
```

### 3. Export for Analysis
```bash
python export_to_json.py data.json
```

### 4. Search for Code
```bash
export OPENAI_API_KEY="sk-xxx"
python search_index.py "authentication function"
```

### 5. Index a New Workspace
```bash
export GITHUB_TOKEN="ghp_xxx"
python create_index.py ~/projects/myapp
```

---

## 🔧 Troubleshooting

**Database not found?**
```bash
python -c "from database import find_database_path; print(find_database_path() or 'Not found')"
```

**Check Python version:**
```bash
python --version  # Should be 3.8+
```

**Verify dependencies:**
```bash
pip list | grep -E "(numpy|rich|openai)"
```

**Re-setup environment:**
```bash
./setup.sh
```

---

## 📦 Installation

```bash
cd python_tools
./setup.sh
source venv/bin/activate
```

Or manually:
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

---

## 🧪 Run Tests

```bash
source venv/bin/activate
./run_all_tests.sh
```

---

## 📖 More Information

- **README.md** - Full usage guide
- **API.md** - GitHub API documentation
- **TEST_RESULTS_FINAL.md** - Comprehensive test results
- **DEMO_RESULTS.md** - Sample outputs

---

**Created:** January 26, 2025
**Python:** 3.12.3
**Status:** ✅ All tools tested and working
