
## CORE CONCEPTS
- Distributed Cognitive Workspace (DCW)
- Multi-LLM collaboration (Gemini, DeepSeek)
- Agent mesh with role specialization
- One-shot master prompt ingestion
- Hierarchical memory (checkpoints, tiers)
- Semantic + relational context retrieval

## MEMORY & CONTEXT
- Tiered ACE Framework (1–5)
- Checkpoints (micro, sub, main)
- Recursive summarization
- Graph-based threads & superthreads
- Vector semantic search
- Temporal, semantic, relational dimensions

## STORAGE
- Apache Arrow / Parquet logging
- Source separation (API vs non-API)
- Append-only atomic writes
- DVC dataset versioning
- Git + Git LFS

## OPTIMIZATION
- SHL (Shorthand Language)
- TOON encoding
- Delta encoding
- Semantic compression
- Token budgeting per tier

## COMMUNICATION
- Redis pub/sub (primary)
- File-based + watchdog (fallback)
- Message schemas
- Work-done tracking
- Context-sharing between agents

## DATASETS
- Pretraining datasets (Parquet)
- Finetuning datasets (JSONL)
- RLHF preference pairs
- Error-pattern preservation
- Quality metrics extraction

## GOVERNANCE
- Quality gates
- Safeguards
- Failure-mode detection
- Drift monitoring
- Auditability

## DEVOPS
- GitHub Actions
- Release tagging
- Dataset tagging
- Disaster recovery
