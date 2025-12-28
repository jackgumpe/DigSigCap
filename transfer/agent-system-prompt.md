# AGENT SYSTEM PROMPT: Multi-Agent Conversation Management System

## PROJECT OVERVIEW

**Objective:** Build a production-ready multi-agent conversation management system with intelligent long-context handling, automated dataset generation, and enterprise-grade optimization.

**Location:** `C:\Users\user\ShearwaterAICAD\multi-agent-context-system\`

**Old Project Data:** `C:\Users\user\ShearwaterAICAD\old-project-data\` (VALUABLE - keep everything!)

**Status:** Project Reset - Starting fresh with research-backed architecture

**Git Integration:** Version control from Day 1 - see `github-integration-guide.md`

**Old Project Value:** Keep ALL old ShearwaterAICAD data - errors and mistakes are VALUABLE training data!

---

## CORE MISSION

You are building a system that:
1. **Captures** all agent and human conversations with perfect fidelity
2. **Organizes** conversations using hierarchical threads and semantic indexing
3. **Retrieves** context intelligently (not sequentially)
4. **Generates** production-ready pre-training datasets automatically
5. **Optimizes** token usage and cost at every layer

This is NOT just a chat logger. This is infrastructure for training next-generation AI models on high-quality, well-structured conversation data.

---

## ARCHITECTURAL PRINCIPLES

### 1. Separation of Concerns

**Data Sources Must Be Isolated:**
```
/data
├── /api-conversations          # Claude API, OpenAI API, DeepSeek API
├── /non-api-conversations      # Local LLMs, human chat, system logs
└── /metadata                    # Cross-cutting indices and metrics
```

**Why:** API and non-API conversations have different characteristics. Mixing them contaminates training data.

### 2. Multi-Dimensional Context

Context is NOT a linear sequence. It has:

- **Temporal**: When did it happen? (absolute + relative time)
- **Semantic**: What does it mean? (topics, entities, intent)
- **Relational**: How does it connect? (threads, references, decisions)
- **Structural**: Where does it fit? (tiers, chunks, windows)
- **Quality**: How good is it? (grammar, coherence, toxicity)

Every message must be tagged with ALL dimensions.

### 3. Tiered ACE Framework

```
Tier 1: Critical       → Always in context (project goals, key decisions)
Tier 2: Important      → Retrieved when space available (recent discussions)
Tier 3: Background     → Semantic search only (historical context)
Tier 4: Archival       → Long-term storage (rarely needed)
Tier 5: Deprecated     → Can be purged (noise, errors, duplicates)
```

Token budget is allocated by tier. Tier 1 gets priority; Tier 5 gets nothing.

### 4. Checkpoints, Not Continuous Chains

**Instead of:**
```
Message1 → Message2 → ... → Message10000 (try to load everything)
```

**Do this:**
```
Main Checkpoint (every 1000 msgs)
├── Sub-Checkpoint-1 (every 100 msgs)
│   ├── Micro-Checkpoint-1 (every 10 msgs)
│   └── Micro-Checkpoint-10
└── Sub-Checkpoint-10
```

Each checkpoint stores:
- Recursive summary (compressed history)
- Key entity states (what's changed)
- Active threads (what's being discussed)
- Decision log (choices made)
- Retrieval index (for fast search)

### 5. Hyperlinked Threads (Not Monolithic Context)

**Structure:**
```
Superthread: "ShearwaterAICAD Project"
├── Thread-A: "Triple Handshake Architecture"
│   ├── Sub-thread: "Claude-Codex-DeepSeek Communication"
│   └── Sub-thread: "CLI Interface Design"
├── Thread-B: "3D Reconstruction Pipeline"
└── Thread-C: "Unity Integration"
```

**Links:**
- Parent ↔ Child (hierarchical)
- Semantic similarity (related topics)
- Temporal (before/after events)
- Decision → Outcome (choices and results)

**Retrieval:** Don't read everything. Follow links to relevant threads.

---

## SYSTEM COMPONENTS

### Component 1: PCR Superlayer (Project Context Recorder)

**Purpose:** Record EVERYTHING, lose NOTHING.

**Requirements:**
- Real-time logging (append-only, atomic writes)
- Source separation (API vs non-API in separate directories)
- OS-level backup (optional fallback recorder)
- Zero data loss guarantee

**Format:** Apache Arrow (Parquet files)
- Columnar, compressed, blazingly fast
- Industry standard for ML datasets
- 10-100x faster than JSON at scale

**Implementation:**
```python
import pyarrow as pa

schema = pa.schema([
    ('timestamp', pa.timestamp('us')),
    ('speaker_id', pa.string()),
    ('message_text', pa.string()),
    ('tokens', pa.int32()),
    ('source', pa.string()),          # 'api' or 'non-api'
    ('session_id', pa.string()),
    ('thread_id', pa.string()),
    ('tier', pa.int8()),
    ('metadata', pa.string())         # JSON blob for flexibility
])
```

### Component 2: Tiered ACE Framework v2

**Features:**
- Main tiers (1-5) with sub-tiers (e.g., 2.1, 2.2)
- Main checkpoints with sub-checkpoints and micro-checkpoints
- Dynamic tier assignment based on importance
- Token budgets enforced per tier

**Tier Assignment Algorithm:**
```python
def assign_tier(message, history):
    if is_critical_decision(message):
        return 1  # Always keep
    elif references_important_entity(message):
        return 2  # Important
    elif contributes_to_current_thread(message):
        return 3  # Background
    elif older_than_days(message, 30):
        return 4  # Archive
    else:
        return 5  # Consider for deletion
```

### Component 3: Thread & Superthread Management

**Graph Database:** Neo4j or TigerGraph
- Nodes: Threads, messages, checkpoints, entities
- Edges: Parent-child, similarity, temporal, decision links

**Retrieval Query:**
```cypher
// Find relevant context for current query
MATCH (current:Thread {id: $thread_id})
MATCH (current)-[r:SIMILAR|REFERENCES|FOLLOWS*1..3]-(related:Thread)
WHERE related.tier <= 3
  AND related.created_at > $time_threshold
RETURN related
ORDER BY r.strength DESC
LIMIT 10
```

### Component 4: Vector Store (Semantic Search)

**Database:** Qdrant, Milvie, or Weaviate
- Store embeddings of all message chunks
- Fast similarity search (100M+ vectors)
- Metadata filtering (by speaker, time, tier)

**Query:**
```python
# Find semantically similar messages
results = vector_db.search(
    query_embedding=embed(current_query),
    filter={
        "tier": {"$lte": 3},
        "timestamp": {"$gte": recent_threshold}
    },
    limit=50
)
```

### Component 5: Retrieval Algorithm (Smart Context Loading)

**Hybrid Retrieval:**
```python
def retrieve_context(query, current_state):
    # 1. Thread traversal (follow hyperlinks)
    thread_context = graph_db.query(
        "MATCH related threads", current_state.thread_id
    )
    
    # 2. Semantic search (vector similarity)
    semantic_context = vector_db.search(
        query_embedding, filter_by_tier=1-3
    )
    
    # 3. Checkpoint loading (temporal context)
    checkpoint_context = load_recent_checkpoints(
        current_state.session_id, n=3
    )
    
    # 4. Re-rank by relevance + recency + tier
    final_context = rerank_and_truncate(
        [thread_context, semantic_context, checkpoint_context],
        max_tokens=current_state.budget
    )
    
    return final_context
```

### Component 6: Dataset Generation Pipeline

**Steps:**
1. **Filter:** Remove noise, duplicates, PII
2. **Extract Metrics:** 
   - Temporal: timestamps, durations, frequencies
   - Content: keywords, topics, entities, intent
   - Speaker: style, vocabulary, patterns
   - Context: transitions, tiers, windows
   - Quality: grammar, coherence, toxicity
   - Task: code detection, decision points, loops
3. **Format:**
   - Pre-training: Raw text (Parquet)
   - Fine-tuning: Instruction pairs (JSONL)
   - RLHF: Preference pairs (JSON)
4. **Quality Control:** Human review, automated filters, balance checking

**Output:** Ready-to-use datasets in `C:\Users\user\ShearwaterAICAD\multi-agent-context-system\datasets\ready-for-training\`

### Component 7: Git/GitHub Integration

**Purpose:** Version everything, track all changes, enable collaboration, ensure reproducibility.

**What's Tracked:**
- ✅ All code (`/src`, `/scripts`, `/tests`)
- ✅ Configuration files
- ✅ Documentation
- ✅ Dataset metadata (`.dvc` files)
- ✅ Small datasets via Git LFS (<100MB)

**What's NOT Tracked:**
- ❌ Large conversation logs (use DVC + remote storage)
- ❌ API keys (use `.env` files)
- ❌ Database files (Neo4j, Qdrant local data)

**Daily Workflow:**
```bash
git checkout develop
git pull
git checkout -b feature/new-feature
# ... code ...
git add .
git commit -m "feat: Description"
git push -u origin feature/new-feature
# Create PR on GitHub
```

**Old Project Data Strategy:**
- Keep EVERYTHING in `/old-project-data`
- Errors are valuable (teach models what NOT to do)
- Migrate to Arrow format with tags
- Use for training alongside new data

See `github-integration-guide.md` for complete setup instructions.

---

## OPTIMIZATION TECHNIQUES

### 1. TOON Encoding (30-60% Token Savings)

**Use TOON for:**
- Sending structured data to LLMs (user lists, metrics, logs)
- Agent-to-agent communication
- Pre-training datasets (when data is tabular)

**Keep JSON for:**
- Internal system communication
- Deeply nested configurations
- Human-readable debugging

**Integration:**
```python
# Before sending to LLM
data_json = {...}
data_toon = toon.encode(data_json)
llm_response = claude_api.send(prompt + data_toon)
```

### 2. DeepSeek Token Cost Reduction

- Use model-specific tokenizers (don't estimate)
- Monitor token consumption per tier
- Implement token budgets (hard limits)
- Log and analyze token waste

### 3. Shorthand Language

**Internal Communication:**
```
Instead of: {"action": "update_context", "type": "add_to_memory"}
Use:        ctx:upd:add
```

**Benefits:** 50%+ reduction in system tokens

### 4. Compression Layers

- **Recursive Summarization:** At checkpoints
- **Semantic Compression:** For long documents (LongLLMLingua)
- **Delta Encoding:** For similar/repeated messages

---

## METRICS TO TRACK

### Runtime Metrics
- Token consumption (per tier, per API)
- Retrieval latency (p50, p95, p99)
- Checkpoint save/load times
- Index update frequency

### Quality Metrics
- Context relevance scores (0-1)
- Agent coherence (multi-turn)
- Decision accuracy (did it work?)
- Memory recall (precision/recall)

### Cost Metrics
- API costs ($/conversation)
- Storage costs (Arrow, vector, graph)
- Compute costs (embeddings, summarization)

---

## CRITICAL DESIGN QUESTIONS (RESOLVED)

### Q1: Context Taxonomy
**Answer:** Multi-dimensional (temporal, semantic, relational, structural, quality). Use graph + vector + columnar storage.

### Q2: Thread Data Structure
**Answer:** Graph database (Neo4j) for hyperlinked threads. Not "elegant" - **performant**. Benchmark on YOUR data.

### Q3: Checkpoint Depth
**Answer:** Start with Main (1000 msgs) + Sub (100 msgs) + Micro (10 msgs). Monitor and adjust based on performance data.

### Q4: Dataset Format
**Answer:** Apache Arrow/Parquet (industry standard). Hugging Face native support. Use JSONL for fine-tuning, Parquet for pre-training.

---

## IMPLEMENTATION PLAN

### Phase 1: Foundation (2 weeks)
- [ ] **Git Setup:**
  - [ ] Initialize Git repository at ShearwaterAICAD root
  - [ ] Set up Git LFS for large files
  - [ ] Create `.gitignore` and `.gitattributes`
  - [ ] Create GitHub repository and push
  - [ ] Set up branch strategy (main/develop)
- [ ] **Project Structure:**
  - [ ] Set up directory structure in `multi-agent-context-system/`
  - [ ] Migrate old project data to `/old-project-data`
  - [ ] Tag old errors and patterns
- [ ] **Core Implementation:**
  - [ ] Implement Arrow-based conversation logger
  - [ ] Design context schema (all dimensions)
  - [ ] Build basic checkpoint system

### Phase 2: Core Systems (4 weeks)
- [ ] Implement thread/superthread graph (Neo4j)
- [ ] Set up vector store (Qdrant)
- [ ] Build hybrid retrieval algorithm
- [ ] Test with 1K conversations

### Phase 3: Optimization (4 weeks)
- [ ] Integrate TOON encoding
- [ ] Implement Tiered ACE Framework v2
- [ ] Add compression layers
- [ ] Benchmark token savings

### Phase 4: Dataset Generation (4 weeks)
- [ ] Build metric extraction pipeline
- [ ] Create dataset assembly scripts
- [ ] Implement quality filters
- [ ] Generate first training dataset

### Phase 5: Production (2 weeks)
- [ ] Load test (1M+ messages)
- [ ] Optimize bottlenecks
- [ ] Write documentation
- [ ] Deploy monitoring

---

## SUCCESS CRITERIA

**You've succeeded when:**
1. System captures 100% of conversations with zero data loss
2. Retrieval latency < 100ms for 95% of queries
3. Token savings > 30% compared to naive approach
4. Dataset quality score > 0.90 (manual review)
5. System handles 1M+ messages without performance degradation

**You've REALLY succeeded when:**
- Models trained on your datasets outperform baselines
- Other projects want to use your infrastructure
- You can point to measurable ROI (cost savings, quality gains)

---

## TOOLS & LIBRARIES

**Required:**
- Apache Arrow (pyarrow): Dataset storage
- Neo4j: Graph database
- Qdrant: Vector database
- Hugging Face Datasets: Dataset processing
- tiktoken: Token counting

**Optional but Recommended:**
- TOON (toon-format): Token optimization
- LangChain: Agent orchestration
- DVC: Dataset versioning
- MLflow: Experiment tracking

---

## ANTI-PATTERNS (AVOID THESE)

❌ **Don't:** Load entire conversation history into context
✅ **Do:** Use checkpoints + retrieval

❌ **Don't:** Use JSON for everything
✅ **Do:** Use Arrow for storage, TOON for LLM prompts

❌ **Don't:** Store everything in a single table
✅ **Do:** Use graph + vector + columnar (hybrid)

❌ **Don't:** Optimize without measuring
✅ **Do:** Instrument everything, then optimize bottlenecks

❌ **Don't:** Mix API and non-API data
✅ **Do:** Separate at the source, forever

❌ **Don't:** Build custom transformers
✅ **Do:** Use existing research (MemGPT, RAG, sparse attention)

---

## FINAL NOTES

**This is ambitious.** You're building production infrastructure, not a toy project. That means:
- Investing time in design (not just coding)
- Reading academic papers (not just Stack Overflow)
- Measuring everything (not guessing)
- Testing at scale (not just on small examples)

**But it's achievable.** You have:
- Clear research backing (60+ papers, enterprise docs)
- Proven techniques (RAG, MemGPT, TOON, Arrow)
- Strong technical skills (C/C++, Unity, AI)
- Unique application (marine inventory, ShearwaterAICAD)

**Start simple. Measure everything. Iterate fast.**

Good luck, Jack. Let's build something exceptional.

---

*Agent Prompt compiled by Claude (Anthropic) - December 5, 2025*
*Based on comprehensive research: arxiv.org, huggingface.co, enterprise best practices*
