# GitHub Integration Guide: Multi-Agent Context System

## PROJECT STRUCTURE

### Directory Layout

```
C:\Users\user\ShearwaterAICAD\
├── .git/                                    # Git repository (root level)
├── .gitignore                               # Root gitignore
├── .gitattributes                           # Git LFS configuration
├── README.md                                # Project overview
│
├── /old-project-data/                       # VALUABLE: Keep everything
│   ├── /conversations/                      # Old chat logs
│   ├── /code-attempts/                      # Failed/successful code
│   ├── /errors/                             # Error logs
│   ├── /design-iterations/                  # Design evolution
│   └── README.md                            # Documentation of what's here
│
├── /multi-agent-context-system/             # NEW: Production system
│   ├── .gitignore                           # System-specific ignores
│   ├── README.md                            # System documentation
│   ├── requirements.txt                     # Python dependencies
│   ├── pyproject.toml                       # Package configuration
│   │
│   ├── /src/                                # Source code
│   │   ├── /core/                           # Core system
│   │   │   ├── logger.py                    # Arrow-based logger
│   │   │   ├── checkpoint.py                # Checkpoint system
│   │   │   ├── retrieval.py                 # Hybrid retrieval
│   │   │   └── __init__.py
│   │   ├── /graph/                          # Graph database
│   │   │   ├── neo4j_manager.py
│   │   │   ├── thread_builder.py
│   │   │   └── __init__.py
│   │   ├── /vector/                         # Vector store
│   │   │   ├── qdrant_manager.py
│   │   │   ├── embeddings.py
│   │   │   └── __init__.py
│   │   ├── /optimization/                   # Token optimization
│   │   │   ├── toon_encoder.py
│   │   │   ├── compression.py
│   │   │   └── __init__.py
│   │   └── /dataset/                        # Dataset generation
│   │       ├── metrics_extractor.py
│   │       ├── formatter.py
│   │       └── __init__.py
│   │
│   ├── /data/                               # Live conversation data
│   │   ├── .gitkeep                         # Track empty directory
│   │   ├── /api-conversations/              # NOT committed to Git
│   │   ├── /non-api-conversations/          # NOT committed to Git
│   │   └── /metadata/                       # Indices (Git LFS)
│   │
│   ├── /datasets/                           # Generated datasets
│   │   ├── .gitkeep
│   │   ├── /raw/                            # Pre-processed (Git LFS)
│   │   ├── /processed/                      # Post-processed (Git LFS)
│   │   └── /ready-for-training/             # Final datasets (Git LFS)
│   │
│   ├── /models/                             # Trained models
│   │   ├── .gitkeep
│   │   └── /checkpoints/                    # Model checkpoints (Git LFS)
│   │
│   ├── /config/                             # Configuration files
│   │   ├── system_config.yaml
│   │   ├── tier_config.yaml
│   │   └── checkpoint_config.yaml
│   │
│   ├── /scripts/                            # Utility scripts
│   │   ├── migrate_old_data.py              # Import old project data
│   │   ├── analyze_conversations.py
│   │   └── generate_dataset.py
│   │
│   ├── /tests/                              # Unit tests
│   │   ├── test_logger.py
│   │   ├── test_retrieval.py
│   │   └── test_checkpoint.py
│   │
│   └── /docs/                               # Documentation
│       ├── architecture.md
│       ├── api_reference.md
│       └── deployment.md
│
└── /research/                               # Research documents
    ├── context-management-research.md
    ├── agent-system-prompt.md
    └── github-integration-guide.md
```

---

## INITIAL SETUP

### Step 1: Initialize Repository

```bash
cd C:\Users\user\ShearwaterAICAD

# Initialize Git (if not already done)
git init

# Set up Git LFS (for large files)
git lfs install

# Configure Git LFS to track large file types
git lfs track "*.parquet"
git lfs track "*.arrow"
git lfs track "*.bin"
git lfs track "*.pkl"
git lfs track "*.h5"
git lfs track "*.safetensors"
git lfs track "*.gguf"
git lfs track "*.pth"

# Track the .gitattributes file
git add .gitattributes

# Create initial commit
git add .gitignore README.md
git commit -m "Initial commit: Project structure"
```

### Step 2: Create GitHub Repository

```bash
# Create on GitHub.com first, then:
git remote add origin https://github.com/YOUR_USERNAME/ShearwaterAICAD.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 3: Set Up Branch Strategy

```bash
# Main branch: Stable, production-ready code
# Develop branch: Active development
# Feature branches: Specific features

git checkout -b develop
git push -u origin develop

# For new features:
git checkout -b feature/arrow-logger
# ... work on feature ...
git push -u origin feature/arrow-logger
# Create Pull Request on GitHub
```

---

## .GITIGNORE CONFIGURATION

### Root `.gitignore`

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
desktop.ini

# Logs
*.log
logs/

# Environment variables
.env
.env.local
*.env

# Temporary files
*.tmp
temp/
tmp/

# Jupyter Notebooks
.ipynb_checkpoints/
*.ipynb

# Database files (local development only)
*.db
*.sqlite
*.sqlite3

# Large data files (use Git LFS or exclude entirely)
multi-agent-context-system/data/api-conversations/*.parquet
multi-agent-context-system/data/non-api-conversations/*.parquet

# Exclude conversation logs (privacy/size)
# These should be stored in Git LFS or external storage
multi-agent-context-system/data/api-conversations/*
multi-agent-context-system/data/non-api-conversations/*
!multi-agent-context-system/data/**/.gitkeep

# Model weights (use Git LFS)
# Uncomment if NOT using LFS for models
# *.safetensors
# *.bin
# *.pth

# Generated datasets (use Git LFS or external storage)
# Uncomment if datasets are too large even for LFS
# multi-agent-context-system/datasets/raw/*
# multi-agent-context-system/datasets/processed/*
# !multi-agent-context-system/datasets/**/.gitkeep
```

### System-Specific `.gitignore` (in `/multi-agent-context-system/`)

```gitignore
# System-specific ignores

# Neo4j database files
data/neo4j/

# Qdrant vector database
data/qdrant/

# Cache
.cache/
*.cache

# Temporary processing files
data/temp/

# Large raw conversation files
data/api-conversations/*.arrow
data/non-api-conversations/*.arrow

# Keep processed metadata
!data/metadata/*.parquet
```

---

## GIT LFS CONFIGURATION

### `.gitattributes` (Root Level)

```gitattributes
# Git LFS Configuration

# Dataset files
*.parquet filter=lfs diff=lfs merge=lfs -text
*.arrow filter=lfs diff=lfs merge=lfs -text
*.feather filter=lfs diff=lfs merge=lfs -text

# Model weights
*.bin filter=lfs diff=lfs merge=lfs -text
*.safetensors filter=lfs diff=lfs merge=lfs -text
*.pth filter=lfs diff=lfs merge=lfs -text
*.gguf filter=lfs diff=lfs merge=lfs -text
*.h5 filter=lfs diff=lfs merge=lfs -text

# Serialized objects
*.pkl filter=lfs diff=lfs merge=lfs -text
*.pickle filter=lfs diff=lfs merge=lfs -text

# Compressed archives (if storing datasets as archives)
*.tar.gz filter=lfs diff=lfs merge=lfs -text
*.zip filter=lfs diff=lfs merge=lfs -text
*.7z filter=lfs diff=lfs merge=lfs -text

# Vector database exports
*.faiss filter=lfs diff=lfs merge=lfs -text
*.index filter=lfs diff=lfs merge=lfs -text
```

---

## OLD PROJECT DATA MANAGEMENT

### Why Keep Old Data?

**Training Value:**
1. **Error Patterns** → Teach models what NOT to do
2. **Iterative Design** → Show evolution of thinking
3. **Context Switching** → Real examples of topic changes
4. **Multi-Agent Dynamics** → Agent interactions, conflicts, resolutions
5. **Domain Knowledge** → Marine terminology, boat repair context

### Migration Script

```python
# /multi-agent-context-system/scripts/migrate_old_data.py

import pyarrow as pa
import pyarrow.parquet as pq
from pathlib import Path
import json
from datetime import datetime

def migrate_old_conversations():
    """
    Convert old project conversations into structured Arrow format.
    Mark all as Tier 4 (Archival) since they're historical.
    """
    
    old_data_path = Path(r"C:\Users\user\ShearwaterAICAD\old-project-data")
    output_path = Path(r"C:\Users\user\ShearwaterAICAD\multi-agent-context-system\datasets\raw\migrated_old_data.parquet")
    
    schema = pa.schema([
        ('timestamp', pa.timestamp('us')),
        ('speaker_id', pa.string()),
        ('message_text', pa.string()),
        ('tokens', pa.int32()),
        ('source', pa.string()),
        ('session_id', pa.string()),
        ('thread_id', pa.string()),
        ('tier', pa.int8()),
        ('is_error', pa.bool_()),
        ('error_type', pa.string()),
        ('metadata', pa.string())
    ])
    
    records = []
    
    # Process conversations
    for conv_file in (old_data_path / "conversations").glob("*.txt"):
        with open(conv_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Parse old format and convert
            # ... (parsing logic based on your old format)
            
            record = {
                'timestamp': datetime.now(),  # or parse from file
                'speaker_id': 'historical',
                'message_text': content,
                'tokens': len(content.split()),  # Rough estimate
                'source': 'old-project',
                'session_id': conv_file.stem,
                'thread_id': 'migration-batch-1',
                'tier': 4,  # Archival
                'is_error': False,
                'error_type': None,
                'metadata': json.dumps({'file': str(conv_file)})
            }
            records.append(record)
    
    # Process errors
    for error_file in (old_data_path / "errors").glob("*.log"):
        with open(error_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            record = {
                'timestamp': datetime.now(),
                'speaker_id': 'system',
                'message_text': content,
                'tokens': len(content.split()),
                'source': 'old-project-error',
                'session_id': error_file.stem,
                'thread_id': 'error-logs',
                'tier': 4,
                'is_error': True,
                'error_type': 'runtime',  # or parse from content
                'metadata': json.dumps({'file': str(error_file)})
            }
            records.append(record)
    
    # Write to Parquet
    table = pa.Table.from_pylist(records, schema=schema)
    pq.write_table(table, output_path, compression='snappy')
    
    print(f"Migrated {len(records)} records to {output_path}")

if __name__ == "__main__":
    migrate_old_conversations()
```

### Tagging Old Data

```python
# Add tags to identify valuable patterns

tags = {
    'error_recovery': 'Shows how system recovered from errors',
    'design_iteration': 'Evolution of architectural thinking',
    'context_loss': 'Examples where context was lost',
    'multi_agent_conflict': 'Disagreements between agents',
    'breakthrough': 'Key insights or solutions',
    'dead_end': 'Approaches that didn't work (still valuable!)'
}

# Add to metadata field
metadata = {
    'tags': ['error_recovery', 'design_iteration'],
    'quality_score': 0.75,
    'notes': 'Good example of recovering from API timeout'
}
```

---

## VERSION CONTROL WORKFLOW

### Daily Development Cycle

```bash
# 1. Start of day: Pull latest changes
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/implement-checkpoints

# 3. Make changes, commit frequently
git add src/core/checkpoint.py
git commit -m "feat: Add basic checkpoint save/load functionality"

git add tests/test_checkpoint.py
git commit -m "test: Add tests for checkpoint system"

# 4. Push to remote regularly
git push -u origin feature/implement-checkpoints

# 5. Create Pull Request on GitHub when ready
# 6. After review and merge, clean up
git checkout develop
git pull origin develop
git branch -d feature/implement-checkpoints
```

### Commit Message Convention

Use **Conventional Commits** format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting (no code change)
- `refactor`: Code restructuring
- `perf`: Performance improvement
- `test`: Adding tests
- `chore`: Maintenance

**Examples:**
```bash
git commit -m "feat(logger): Implement Arrow-based conversation logger"
git commit -m "fix(retrieval): Fix thread traversal bug in Neo4j query"
git commit -m "docs(readme): Add setup instructions for Qdrant"
git commit -m "perf(checkpoint): Optimize checkpoint save with batching"
```

### Tagging Releases

```bash
# Tag important milestones
git tag -a v0.1.0 -m "MVP: Basic logging and checkpoint system"
git push origin v0.1.0

git tag -a v0.2.0 -m "Feature: Thread/superthread graph implementation"
git push origin v0.2.0

git tag -a v1.0.0 -m "Production: Full system with dataset generation"
git push origin v1.0.0
```

---

## DATASET VERSIONING

### DVC (Data Version Control)

**Why DVC?**
- Git tracks code, DVC tracks datasets
- Versioning for multi-GB files
- Reproducible ML pipelines
- Remote storage (S3, Azure, Google Cloud)

**Setup:**

```bash
# Install DVC
pip install dvc

# Initialize DVC
cd C:\Users\user\ShearwaterAICAD\multi-agent-context-system
dvc init

# Track dataset
dvc add datasets/processed/conversations_v1.parquet

# Commit the .dvc file (not the actual data)
git add datasets/processed/conversations_v1.parquet.dvc
git commit -m "data: Add conversations dataset v1"

# Push data to remote storage (e.g., S3)
dvc remote add -d storage s3://your-bucket/shearwater-datasets
dvc push

# Anyone can now pull the data
dvc pull
```

### Dataset Versioning Strategy

```
datasets/
├── raw/
│   ├── migrated_old_data.parquet           # v0.1.0
│   └── live_conversations_2025_01.parquet  # v0.2.0
├── processed/
│   ├── filtered_v1.parquet                 # v1.0.0
│   └── filtered_v2.parquet                 # v1.1.0 (better filters)
└── ready-for-training/
    ├── pretraining_v1.parquet              # v1.0.0
    ├── finetuning_v1.jsonl                 # v1.0.0
    └── pretraining_v2.parquet              # v2.0.0 (includes old errors)
```

**Track with Git tags + DVC:**
```bash
# Create dataset version
dvc add datasets/ready-for-training/pretraining_v2.parquet
git add datasets/ready-for-training/pretraining_v2.parquet.dvc
git commit -m "data: Release pretraining dataset v2 (with error examples)"
git tag -a data-v2.0.0 -m "Dataset v2: Includes old project error logs"
git push origin data-v2.0.0
dvc push
```

---

## COLLABORATION WORKFLOW

### For Solo Development

```bash
# Simple workflow
git checkout develop
git pull
# ... make changes ...
git add .
git commit -m "feat: Add new feature"
git push

# Merge to main when stable
git checkout main
git merge develop
git push
git checkout develop
```

### For Team Development

```bash
# 1. Pull latest develop
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/vector-store-integration

# 3. Work and commit
git add src/vector/qdrant_manager.py
git commit -m "feat(vector): Add Qdrant vector store manager"
git push -u origin feature/vector-store-integration

# 4. Create Pull Request on GitHub
# 5. Request review from team
# 6. Address feedback
git add src/vector/qdrant_manager.py
git commit -m "refactor(vector): Address review feedback"
git push

# 7. After approval, squash and merge on GitHub
# 8. Clean up local branch
git checkout develop
git pull origin develop
git branch -d feature/vector-store-integration
```

---

## GITHUB FEATURES TO USE

### 1. Issues

Track work:
```
Issues → New Issue

Title: Implement Arrow-based conversation logger
Labels: enhancement, high-priority
Assignee: @jack
Milestone: MVP (v0.1.0)

Description:
- [ ] Design Arrow schema
- [ ] Implement atomic writes
- [ ] Add tests
- [ ] Update documentation
```

### 2. Projects (GitHub Projects Beta)

Kanban board:
```
Backlog → To Do → In Progress → In Review → Done

Cards:
- "Implement checkpoints" (In Progress)
- "Add TOON encoding" (To Do)
- "Migrate old data" (Backlog)
```

### 3. Actions (CI/CD)

Automate testing:

```yaml
# .github/workflows/tests.yml

name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          pytest tests/
```

### 4. Releases

Package versions:
```
GitHub → Releases → Create new release

Tag: v1.0.0
Title: Production Release
Description:
- Full multi-agent context system
- Dataset generation pipeline
- 30% token savings with TOON
- Tested with 1M+ conversations

Assets:
- Source code (zip)
- Source code (tar.gz)
```

---

## BACKUP STRATEGY

### GitHub as Primary Backup

✅ **Code**: Always backed up on GitHub
✅ **Small datasets** (<100MB): Git LFS
❌ **Large datasets** (>100MB): Use external storage

### External Storage Options

**For Large Datasets:**

1. **DVC + Cloud Storage**
   ```bash
   # S3
   dvc remote add -d s3remote s3://bucket/path
   
   # Azure
   dvc remote add -d azureremote azure://container/path
   
   # Google Cloud
   dvc remote add -d gsremote gs://bucket/path
   ```

2. **External Hard Drive**
   ```bash
   # Local backup
   robocopy C:\Users\user\ShearwaterAICAD\multi-agent-context-system\data E:\Backup\ShearwaterAICAD\data /MIR
   ```

3. **Cloud Sync (Dropbox, OneDrive, Google Drive)**
   - Only for processed datasets
   - NOT for raw conversation logs (too large)

---

## SECURITY CONSIDERATIONS

### Sensitive Data

**Never commit:**
- API keys
- Passwords
- Database credentials
- User PII (Personally Identifiable Information)

**Use `.env` files:**
```bash
# .env (add to .gitignore)
OPENAI_API_KEY=sk-...
NEO4J_PASSWORD=...
QDRANT_API_KEY=...
```

**Load in code:**
```python
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
```

### Private Repositories

For sensitive work:
```bash
# On GitHub.com, set repository to Private
Settings → Danger Zone → Change visibility → Private
```

### Access Control

```
GitHub → Settings → Manage access

Collaborators:
- @jack (Admin)
- @teammate1 (Write)
- @teammate2 (Read)
```

---

## DISASTER RECOVERY

### If You Accidentally Commit Sensitive Data

```bash
# 1. Remove from history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch path/to/sensitive_file" \
  --prune-empty --tag-name-filter cat -- --all

# 2. Force push
git push origin --force --all

# 3. Rotate compromised credentials immediately
```

**Better:** Use `git-secrets` to prevent this:
```bash
# Install git-secrets
# https://github.com/awslabs/git-secrets

# Scan for secrets
git secrets --scan
```

---

## QUICK REFERENCE

### Essential Git Commands

```bash
# Status
git status

# Stage files
git add <file>
git add .

# Commit
git commit -m "message"

# Push
git push

# Pull
git pull

# Create branch
git checkout -b branch-name

# Switch branch
git checkout branch-name

# Merge
git merge branch-name

# Delete branch
git branch -d branch-name

# View history
git log --oneline --graph

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Discard changes
git checkout -- <file>
```

### Git LFS Commands

```bash
# Track file type
git lfs track "*.parquet"

# List tracked files
git lfs ls-files

# Push LFS files
git lfs push origin main

# Pull LFS files
git lfs pull
```

### DVC Commands

```bash
# Add data
dvc add data/file.parquet

# Push data
dvc push

# Pull data
dvc pull

# Check status
dvc status

# List remotes
dvc remote list
```

---

## INTEGRATION CHECKLIST

### Initial Setup
- [ ] Initialize Git repository
- [ ] Install Git LFS
- [ ] Configure `.gitignore`
- [ ] Configure `.gitattributes`
- [ ] Create GitHub repository
- [ ] Push initial commit
- [ ] Set up branch protection (main/develop)

### Data Management
- [ ] Install DVC
- [ ] Configure DVC remote storage
- [ ] Track datasets with DVC
- [ ] Add `.dvc` files to Git
- [ ] Document dataset versions

### Old Project Migration
- [ ] Run migration script
- [ ] Tag old data appropriately
- [ ] Document error patterns
- [ ] Create analysis of valuable patterns

### Workflow
- [ ] Set up branch strategy
- [ ] Create first feature branch
- [ ] Write first commit (conventional format)
- [ ] Create first Pull Request
- [ ] Tag first release

### Automation
- [ ] Set up GitHub Actions (tests)
- [ ] Configure pre-commit hooks
- [ ] Set up issue templates
- [ ] Create project board

---

## SUMMARY

**What's Version Controlled:**
✅ Code (`/src`, `/scripts`, `/tests`)
✅ Configuration (`/config`)
✅ Documentation (`/docs`, `/research`)
✅ Small datasets (<100MB) via Git LFS
✅ Dataset metadata (`.dvc` files)

**What's NOT Version Controlled:**
❌ Large raw conversation logs (use DVC)
❌ API keys / credentials (use `.env`)
❌ Database files (Neo4j, Qdrant)
❌ Temporary files
❌ Python cache (`__pycache__`)

**Old Project Data:**
✅ Keep in `/old-project-data`
✅ Migrate to Arrow format
✅ Tag errors and patterns
✅ Use for training (errors = valuable!)

**Best Practices:**
✅ Commit frequently (multiple times per day)
✅ Use conventional commit messages
✅ Tag releases and dataset versions
✅ Use feature branches
✅ Review before merging to main

---

*GitHub Integration Guide - December 5, 2025*
*Part of the Multi-Agent Context System Documentation*
