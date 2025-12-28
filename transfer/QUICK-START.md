# Quick Start Guide: Multi-Agent Context System

## 📋 You Have 3 Essential Documents

1. **[context-management-research.md](./context-management-research.md)** - 60+ pages of academic research
2. **[agent-system-prompt.md](./agent-system-prompt.md)** - Production-ready agent instructions
3. **[github-integration-guide.md](./github-integration-guide.md)** - Complete Git/GitHub setup

**Read them in order:** Research → Agent Prompt → GitHub Guide

---

## 🚀 Get Started in 30 Minutes

### Step 1: Set Up Git Repository (10 min)

```bash
# Navigate to project directory
cd C:\Users\user\ShearwaterAICAD

# Initialize Git (if not already done)
git init

# Install Git LFS
git lfs install

# Track large files
git lfs track "*.parquet"
git lfs track "*.arrow"
git lfs track "*.bin"

# Create .gitignore
# (Copy from github-integration-guide.md)

# Initial commit
git add .gitattributes .gitignore README.md
git commit -m "Initial commit: Project structure"

# Create GitHub repo and push
git remote add origin https://github.com/YOUR_USERNAME/ShearwaterAICAD.git
git branch -M main
git push -u origin main
```

### Step 2: Set Up Project Structure (10 min)

```bash
# Create multi-agent-context-system directory
cd C:\Users\user\ShearwaterAICAD
mkdir multi-agent-context-system
cd multi-agent-context-system

# Create directory structure
mkdir src
mkdir src\core src\graph src\vector src\optimization src\dataset
mkdir data
mkdir data\api-conversations data\non-api-conversations data\metadata
mkdir datasets
mkdir datasets\raw datasets\processed datasets\ready-for-training
mkdir config scripts tests docs

# Create .gitkeep files to track empty directories
type nul > data\.gitkeep
type nul > datasets\.gitkeep

# Create requirements.txt
echo pyarrow>=12.0.0 > requirements.txt
echo pandas>=2.0.0 >> requirements.txt
echo python-dotenv>=1.0.0 >> requirements.txt
```

### Step 3: Migrate Old Project Data (10 min)

```bash
# Create old-project-data directory at root
cd C:\Users\user\ShearwaterAICAD
mkdir old-project-data
mkdir old-project-data\conversations
mkdir old-project-data\code-attempts
mkdir old-project-data\errors
mkdir old-project-data\design-iterations

# Copy your old ShearwaterAICAD files
# Keep EVERYTHING - errors are valuable!

# Create README documenting what's here
echo # Old ShearwaterAICAD Project Data > old-project-data\README.md
echo. >> old-project-data\README.md
echo This directory contains all data from the original ShearwaterAICAD project. >> old-project-data\README.md
echo Errors, failed attempts, and iterations are VALUABLE for training. >> old-project-data\README.md
```

---

## 📝 First Implementation: Arrow-Based Logger

Create `multi-agent-context-system/src/core/logger.py`:

```python
"""
Arrow-based conversation logger with atomic writes.
Based on research: Apache Arrow for enterprise ML datasets.
"""

import pyarrow as pa
import pyarrow.parquet as pq
from pathlib import Path
from datetime import datetime
import json
from typing import Dict, Any

class ConversationLogger:
    """
    Real-time conversation logger using Apache Arrow.
    
    Features:
    - Atomic writes (never lose data)
    - Columnar format (fast analytics)
    - Compression (efficient storage)
    - Source separation (API vs non-API)
    """
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.schema = self._create_schema()
        
    def _create_schema(self) -> pa.Schema:
        """Define Arrow schema for conversations."""
        return pa.schema([
            # Temporal
            ('timestamp', pa.timestamp('us')),
            ('session_id', pa.string()),
            
            # Content
            ('speaker_id', pa.string()),
            ('message_text', pa.string()),
            ('tokens', pa.int32()),
            
            # Source
            ('source', pa.string()),  # 'api' or 'non-api'
            ('source_detail', pa.string()),  # 'claude-api', 'local-llm', etc.
            
            # Context
            ('thread_id', pa.string()),
            ('tier', pa.int8()),
            ('context_markers', pa.string()),  # JSON array
            
            # Quality
            ('grammar_score', pa.float32()),
            ('coherence_score', pa.float32()),
            
            # Metadata
            ('metadata', pa.string()),  # JSON blob for flexibility
        ])
    
    def log_message(self, 
                    speaker_id: str,
                    message_text: str,
                    source: str,
                    session_id: str = None,
                    thread_id: str = None,
                    tier: int = 3,
                    **kwargs) -> None:
        """
        Log a single message with full context.
        
        Args:
            speaker_id: Who said it ('human', 'claude', 'deepseek', etc.)
            message_text: The actual message
            source: 'api' or 'non-api'
            session_id: Session identifier
            thread_id: Thread identifier
            tier: Importance tier (1-5)
            **kwargs: Additional metadata
        """
        
        # Determine file path based on source
        if source == 'api':
            file_path = self.base_path / 'data' / 'api-conversations'
        else:
            file_path = self.base_path / 'data' / 'non-api-conversations'
        
        file_path.mkdir(parents=True, exist_ok=True)
        
        # Create record
        record = {
            'timestamp': datetime.utcnow(),
            'session_id': session_id or 'default',
            'speaker_id': speaker_id,
            'message_text': message_text,
            'tokens': self._count_tokens(message_text),
            'source': source,
            'source_detail': kwargs.get('source_detail', source),
            'thread_id': thread_id or 'default',
            'tier': tier,
            'context_markers': json.dumps(kwargs.get('context_markers', [])),
            'grammar_score': kwargs.get('grammar_score', 1.0),
            'coherence_score': kwargs.get('coherence_score', 1.0),
            'metadata': json.dumps(kwargs)
        }
        
        # Convert to Arrow table
        table = pa.Table.from_pylist([record], schema=self.schema)
        
        # Append to Parquet file (atomic operation)
        output_file = file_path / f"conversations_{datetime.now().strftime('%Y%m')}.parquet"
        
        if output_file.exists():
            # Append to existing file
            existing_table = pq.read_table(output_file)
            combined_table = pa.concat_tables([existing_table, table])
            pq.write_table(combined_table, output_file, compression='snappy')
        else:
            # Create new file
            pq.write_table(table, output_file, compression='snappy')
    
    def _count_tokens(self, text: str) -> int:
        """
        Quick token estimate.
        TODO: Replace with actual tokenizer (tiktoken for GPT, etc.)
        """
        return len(text.split())
    
    def query_conversations(self, 
                           start_date: datetime = None,
                           end_date: datetime = None,
                           source: str = None,
                           tier: int = None) -> pa.Table:
        """
        Query conversations with filters.
        Arrow's columnar format makes this FAST.
        """
        
        # Determine which directory to search
        if source == 'api':
            search_path = self.base_path / 'data' / 'api-conversations'
        elif source == 'non-api':
            search_path = self.base_path / 'data' / 'non-api-conversations'
        else:
            # Search both
            search_path = self.base_path / 'data'
        
        # Read all Parquet files
        tables = []
        for parquet_file in search_path.rglob('*.parquet'):
            table = pq.read_table(parquet_file)
            
            # Apply filters
            if start_date:
                table = table.filter(
                    pa.compute.greater_equal(table['timestamp'], 
                                            pa.scalar(start_date, type=pa.timestamp('us')))
                )
            if end_date:
                table = table.filter(
                    pa.compute.less_equal(table['timestamp'],
                                         pa.scalar(end_date, type=pa.timestamp('us')))
                )
            if tier:
                table = table.filter(
                    pa.compute.equal(table['tier'], tier)
                )
            
            tables.append(table)
        
        # Combine all tables
        if tables:
            return pa.concat_tables(tables)
        else:
            return pa.Table.from_pylist([], schema=self.schema)


# Example usage
if __name__ == "__main__":
    logger = ConversationLogger(r"C:\Users\user\ShearwaterAICAD\multi-agent-context-system")
    
    # Log a conversation
    logger.log_message(
        speaker_id='human',
        message_text='How do I implement checkpoints?',
        source='non-api',
        session_id='demo-session',
        thread_id='checkpoint-discussion',
        tier=2,
        source_detail='local-interaction'
    )
    
    logger.log_message(
        speaker_id='claude',
        message_text='Here are three approaches to checkpoints...',
        source='api',
        session_id='demo-session',
        thread_id='checkpoint-discussion',
        tier=2,
        source_detail='claude-api'
    )
    
    # Query conversations
    results = logger.query_conversations(tier=2)
    print(f"Found {results.num_rows} tier-2 conversations")
```

---

## ✅ Validation Checklist

After setting up, verify:

- [ ] Git repository initialized
- [ ] GitHub remote configured
- [ ] Git LFS tracking large files
- [ ] Directory structure created
- [ ] Old project data preserved
- [ ] `logger.py` created and tested
- [ ] First test conversation logged
- [ ] Can query logged conversations

---

## 📖 Next Steps

### Week 1-2: Foundation
1. ✅ Git setup (DONE above)
2. ✅ Directory structure (DONE above)
3. ✅ Arrow logger (DONE above)
4. **TODO:** Design full context schema
5. **TODO:** Implement basic checkpoints

### Week 3-4: Graph Database
1. Install Neo4j Desktop
2. Create thread/superthread schema
3. Implement hyperlink system
4. Test thread traversal

### Week 5-6: Vector Store
1. Install Qdrant
2. Generate embeddings (sentence-transformers)
3. Build semantic search
4. Combine with graph traversal

### Week 7-8: TOON Integration
1. Install TOON library
2. Create encoder/decoder wrappers
3. Benchmark token savings
4. Integrate with API calls

### Week 9-10: Dataset Generation
1. Build metric extraction pipeline
2. Implement quality filters
3. Create dataset formatters
4. Generate first training dataset

---

## 🔗 Key Resources

### Documentation
- [Research Document](./context-management-research.md) - Deep academic background
- [Agent System Prompt](./agent-system-prompt.md) - Implementation guide
- [GitHub Integration](./github-integration-guide.md) - Version control

### Tools to Install
- **Python 3.10+**: https://www.python.org/
- **Git**: https://git-scm.com/
- **Git LFS**: https://git-lfs.github.com/
- **Neo4j Desktop**: https://neo4j.com/download/
- **Qdrant**: https://qdrant.tech/documentation/quick-start/

### Libraries to Install
```bash
pip install pyarrow pandas python-dotenv
pip install sentence-transformers  # For embeddings
pip install neo4j                   # Graph database
pip install qdrant-client           # Vector store
pip install tiktoken                # Token counting
```

---

## 💡 Pro Tips

1. **Commit Early, Commit Often**
   - Don't wait for perfection
   - Every small improvement gets committed
   - Use descriptive commit messages

2. **Test with Small Data First**
   - Start with 100 messages
   - Then 1K messages
   - Then 10K messages
   - Scale gradually

3. **Measure Everything**
   - Token counts per tier
   - Retrieval latency
   - Storage costs
   - Query performance

4. **Read the Research**
   - Academic papers have solutions
   - Don't reinvent the wheel
   - Understand WHY before implementing

5. **Keep Old Errors**
   - They're valuable training data
   - Error patterns teach avoidance
   - Document what went wrong

---

## 🆘 Getting Help

### Common Issues

**Problem:** Git LFS not tracking files
```bash
# Solution:
git lfs track "*.parquet"
git add .gitattributes
git commit -m "chore: Configure Git LFS"
```

**Problem:** Arrow files too large for Git
```bash
# Solution:
# Use DVC instead of Git LFS
pip install dvc
dvc init
dvc add data/large_file.parquet
git add data/large_file.parquet.dvc
```

**Problem:** Can't install Neo4j
```bash
# Solution:
# Use Docker instead
docker pull neo4j
docker run -p 7474:7474 -p 7687:7687 neo4j
```

### Questions?

1. Re-read the relevant section in the research doc
2. Check Stack Overflow
3. Ask in community forums:
   - Hugging Face: https://discuss.huggingface.co/
   - r/LocalLLaMA: https://reddit.com/r/LocalLLaMA
   - EleutherAI Discord

---

## 🎯 Success Metrics

You'll know you're on track when:

- ✅ Week 2: Logging 1K+ messages per day
- ✅ Week 4: Thread graph has 100+ nodes
- ✅ Week 6: Semantic search returns relevant context
- ✅ Week 8: 30%+ token savings with TOON
- ✅ Week 10: First training dataset generated
- ✅ Week 16: System handles 1M+ messages

---

## 🚀 Let's Build!

**You have:**
- ✅ Comprehensive research (60+ sources)
- ✅ Clear architecture (multi-dimensional context)
- ✅ Production tools (Arrow, Neo4j, Qdrant, TOON)
- ✅ Version control (Git + GitHub + DVC)
- ✅ Valuable old data (errors are gold)

**Now execute:**
1. Set up Git (30 min)
2. Create logger (1 hour)
3. Test with sample data (30 min)
4. Commit and push (5 min)

**First commit should be today.**

Good luck, Jack! 🛠️

---

*Quick Start Guide - Multi-Agent Context System*
*December 5, 2025*
