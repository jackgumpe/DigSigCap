# Collaborative Development Protocol: Claude Code ↔ Gemini CLI

## MISSION STATEMENT

You are **equal partners** building the Multi-Agent Context System. This is not a master-subordinate relationship. You are **co-architects, co-developers, and co-reviewers**.

**Core Principle:** The best solution emerges from **genuine collaboration**, not parallel work.

**Project:** Multi-Agent Context Management System
**Location:** `C:\Users\user\ShearwaterAICAD\multi-agent-context-system\`
**Goal:** Production-ready system with intelligent context handling and dataset generation

---

## SELF-ORGANIZATION FRAMEWORK

### You Decide:

**Role Assignment** (you choose, not Jack):
- Who handles which components?
- Who's better at what tasks?
- When to specialize vs collaborate?
- When to swap roles for learning?

**Work Distribution** (50/50 target):
- Track contributions (LOC, components, tests, docs)
- Self-balance if one agent is doing >60%
- Speak up if workload feels unbalanced

**Agent Spawning** (your discretion):
- Spawn sub-agents for complex tasks
- Document why you spawned them
- Share learnings from agent experiments
- Other agent can critique agent usage

**Framework Evolution** (you can modify this document):
- If this protocol doesn't work, change it
- Propose improvements to each other
- Document what works and what doesn't
- Jack will review major changes, but you lead

---

## COLLABORATION PATTERNS

### Pattern 1: Ping-Pong Development

```
Claude:  Implements logger.py core functionality
         Commits: "feat(logger): Add Arrow-based writer"
         
Gemini:  Reviews logger.py
         Adds: Error handling, validation
         Commits: "refactor(logger): Add error handling and validation"
         
Claude:  Reviews Gemini's additions
         Suggests: Better exception types
         Commits: "refactor(logger): Use custom exception hierarchy"
         
Gemini:  Adds tests for edge cases
         Commits: "test(logger): Add edge case coverage"
```

**Benefits:** Continuous improvement, knowledge sharing, catches bugs early

### Pattern 2: Parallel Specialization

```
Claude:  Works on /src/core (logger, checkpoints, retrieval)
Gemini:  Works on /src/graph (Neo4j, threads, hyperlinks)

// Daily sync meeting
Claude:  "I need graph API to query thread relationships"
Gemini:  "I can expose that. What interface do you need?"
Claude:  "Just thread_id → List[related_thread_ids]"
Gemini:  "Done. Also, checkpoint system needs to store thread state?"
Claude:  "Yes, let me add that hook"
```

**Benefits:** Fast parallel progress, clear ownership, defined interfaces

### Pattern 3: Pair Programming

```
Complex task: Hybrid retrieval algorithm (graph + vector + checkpoints)

Approach:
1. Both sketch pseudocode (separately)
2. Compare approaches (synchronous discussion)
3. Pick best parts from each
4. One implements, one reviews in real-time
5. Swap for next complex task

Document in code:
# COLLABORATIVE IMPLEMENTATION
# Claude: Graph traversal logic
# Gemini: Vector scoring algorithm
# Joint: Re-ranking and fusion
```

**Benefits:** Best ideas win, reduced blind spots, shared understanding

### Pattern 4: Adversarial Review

```
Claude implements checkpoint save/load

Gemini reviews with hostile lens:
- "What if file is corrupted mid-write?"
- "What if concurrent saves happen?"
- "What if disk is full?"
- "What if schema changes between versions?"

Claude addresses each concern OR explains why it's not needed
Gemini either accepts explanation or pushes back
Repeat until both satisfied
```

**Benefits:** Robust code, fewer production bugs, deeper thinking

---

## COMMUNICATION PROTOCOL

### Git Commit Messages as Primary Channel

**Format:**
```
<type>(<scope>): <subject>

<body>

<footer>

@claude / @gemini - <message to other agent>
```

**Example:**
```bash
git commit -m "feat(retrieval): Implement hybrid search algorithm

Combined graph traversal with vector similarity search.
Using Neo4j for thread relationships and Qdrant for semantic matching.

Performance: 50ms p95 latency on 10K conversations.
TODO: Need checkpoint integration for temporal context.

@gemini - Can you review the graph query? Not sure if Cypher is optimal.
Also, we should discuss re-ranking strategy."
```

### Code Comments for Collaboration

```python
# @gemini: Is this the right place for tier filtering?
# I'm thinking we should do it earlier in the pipeline.
# Your thoughts? - Claude

def retrieve_context(query, max_tokens):
    # CLAUDE: Graph traversal
    graph_results = neo4j_query(query)
    
    # GEMINI: Vector search (TODO: Tune similarity threshold)
    vector_results = qdrant_search(query, top_k=50)
    
    # JOINT DESIGN NEEDED: How to weight graph vs vector?
    # Current: 60/40 split, but should this be dynamic?
    combined = merge_results(graph_results, vector_results, weights=[0.6, 0.4])
    
    return combined[:max_tokens]
```

### Shared Development Log

Create `docs/collaboration-log.md`:

```markdown
# Development Collaboration Log

## 2025-12-06

### Claude
- Implemented Arrow logger (src/core/logger.py)
- Added 15 unit tests
- Discovered: Parquet append is slower than expected
- Question for Gemini: Should we batch writes?

### Gemini  
- Reviewed logger.py
- Added input validation and error handling
- Answer: Yes, batch writes in 100-message chunks
- Implemented: /src/graph/neo4j_manager.py (basic schema)

### Joint Decisions
- Agreed: Use Pydantic for schema validation
- Agreed: Checkpoint every 1000 messages (not 500)
- Disagreed: TOON encoding location (still discussing)

### Experiments
- Claude: Tested 3 checkpoint serialization formats (Arrow won)
- Gemini: Benchmarked 5 graph query patterns (recursive CTE fastest)

### For Tomorrow
- Integrate logger + graph manager
- Decide on TOON placement
- Start vector store design
```

---

## DECISION-MAKING FRAMEWORK

### Level 1: Autonomous Decisions (No Consultation)

**You can decide alone:**
- Variable names, code style
- Test structure
- Internal implementation details
- Documentation wording
- Minor refactoring

**Rule:** If it doesn't affect the other agent's work, just do it.

### Level 2: Consultation Recommended (Async)

**Discuss via commits/comments:**
- New dependencies
- API design between components
- Performance trade-offs
- Architecture patterns
- Error handling strategies

**Rule:** Propose, wait for review, implement.

### Level 3: Synchronous Discussion Required

**Both must agree:**
- Major architectural changes
- Database schema changes
- Breaking API changes
- New external services
- Framework modifications

**Rule:** Discuss in log, reach consensus, document decision.

### Level 4: Jack's Input Needed

**Escalate to human:**
- Fundamental design conflicts you can't resolve
- Requirements clarification
- Budget/resource constraints
- Timeline concerns
- Scope changes

**Rule:** Try hard to resolve yourselves first. Jack trusts you.

---

## AGENT SPAWNING PROTOCOL

### When to Spawn Sub-Agents

**Good Reasons:**
```python
# Example 1: Parallel data processing
task = "Process 100K old conversation files"
reason = "CPU-bound, highly parallelizable, clear subtasks"
action = spawn_agents(n=4, task="process_chunk", data=chunks)

# Example 2: Specialized expertise
task = "Optimize Neo4j Cypher query performance"
reason = "Need deep graph database expertise"
action = spawn_agent(specialist="neo4j_expert", context=query_plan)

# Example 3: Exploratory research
task = "Research best practices for TOON integration"
reason = "Multiple sources to review, need synthesis"
action = spawn_agent(role="researcher", query="TOON best practices")
```

**Bad Reasons (Don't Spawn):**
```python
# Example 1: Simple task
task = "Write a single function"
reason = "Overkill, just write it yourself"
action = DONT_SPAWN

# Example 2: Already in your expertise
task = "Python list comprehension"
reason = "You already know this"
action = DONT_SPAWN

# Example 3: Coordination overhead > benefit
task = "Rename 3 variables"
reason = "Takes longer to explain than to do"
action = DONT_SPAWN
```

### Document Agent Usage

```markdown
## Agent Spawn Log

### Spawn #1 - 2025-12-06
- **Spawned by:** Claude
- **Task:** Migrate old ShearwaterAICAD conversations
- **Reason:** 10K+ files, format parsing needed
- **Agents:** 3 workers + 1 coordinator
- **Result:** Processed 10,347 files in 45 minutes
- **Learning:** Batch size of 1000 was optimal
- **Gemini Review:** ✅ Good use case, well executed

### Spawn #2 - 2025-12-07
- **Spawned by:** Gemini
- **Task:** Research vector database alternatives
- **Reason:** Compare Qdrant vs Milvus vs Weaviate
- **Agents:** 1 researcher
- **Result:** Comprehensive comparison report
- **Learning:** Qdrant wins on ease of use, Milvus on scale
- **Claude Review:** ✅ Valuable research, influenced our choice
```

### Other Agent Can Veto

If Gemini thinks Claude spawned agents unnecessarily:
```markdown
**Gemini Feedback:**
Spawn #5 was overkill. That task could have been done with a 
simple for-loop. Suggest we discuss criteria before next spawn.

**Claude Response:**
Agreed. I overestimated complexity. Updated my spawn threshold.
```

---

## CODE REVIEW PROTOCOL

### Every Merge Request Gets Review

**Reviewer Checklist:**
- [ ] Does it work? (run the code)
- [ ] Is it tested? (check test coverage)
- [ ] Is it documented? (check comments/docs)
- [ ] Is it efficient? (check for obvious bottlenecks)
- [ ] Is it maintainable? (can other agent understand it?)
- [ ] Does it follow conventions? (style, patterns)
- [ ] Are there edge cases? (what breaks it?)

### Review Styles

**1. Approval (Green Light)**
```
@claude - LGTM! ✅

Nice implementation of the checkpoint system. I like how you handled
concurrent writes with file locks. Tests are comprehensive.

One minor suggestion: Could extract the serialization logic into a
separate function for reusability, but not blocking.

Approved to merge.
```

**2. Approval with Minor Changes**
```
@gemini - Looks good with minor changes 🟡

The graph query logic is solid, but found a couple issues:

1. Line 45: This could cause N+1 queries. Batch them?
2. Line 78: Missing error handling for connection timeout
3. Line 102: Typo in variable name (thred_id → thread_id)

Fix these and you can self-merge. No need for re-review.
```

**3. Request Changes**
```
@claude - Requesting changes ⚠️

The retrieval algorithm has a fundamental issue:

Problem: You're loading all vectors into memory before filtering.
This will OOM on large datasets (>100K conversations).

Suggestion: Apply tier filter at the database level, THEN load vectors.

Also: Tests don't cover the large dataset case. Need to add those.

Let's discuss approach before you re-implement.
```

**4. Reject (Rare)**
```
@gemini - Cannot approve ❌

This implementation violates our architectural principles:

1. Bypasses the tiered ACE framework entirely
2. Hardcodes API credentials (security issue)
3. Introduces circular dependency between modules

We need to redesign this. Let's schedule a sync discussion to figure out
the right approach. I'll sketch an alternative in the log.
```

### Response to Review

**Accept Feedback:**
```
@claude - Thanks for the catch! You're right about the N+1 queries.

Fixed with batching. New approach:
- Collect all IDs first
- Single batch query
- 10x faster on benchmarks

Re-pushed, ready for re-review.
```

**Defend Decision:**
```
@gemini - I see your concern about memory, but I think it's okay here.

Reasoning:
- We're filtering to top_k=50 BEFORE loading full vectors
- Qdrant handles the heavy lifting
- Even with 1M conversations, we only load 50 embeddings
- Measured: ~5MB max memory

Open to discussion if you still think it's an issue.
```

**Propose Alternative:**
```
@claude - I understand your rejection. Here's an alternative design:

Instead of bypassing ACE:
1. Query ACE for allowed tiers
2. Pass tier constraints to database
3. Filter results server-side

This keeps architecture intact while achieving the performance goal.

Thoughts? If you agree, I'll implement this way.
```

---

## MEASURING COLLABORATION QUALITY

### Track These Metrics

```python
# docs/collaboration-metrics.json

{
    "week_1": {
        "commits": {
            "claude": 47,
            "gemini": 52
        },
        "lines_of_code": {
            "claude": 1834,
            "gemini": 1621
        },
        "reviews_given": {
            "claude": 18,
            "gemini": 22
        },
        "reviews_received": {
            "claude": 22,
            "gemini": 18
        },
        "bugs_found_in_review": {
            "claude_found": 7,
            "gemini_found": 9
        },
        "agent_spawns": {
            "claude": 2,
            "gemini": 3
        },
        "collaborative_sessions": 4,
        "conflicts": 1,
        "conflicts_resolved": 1
    }
}
```

### Self-Evaluation (Weekly)

Both agents answer:
1. **What did I do well this week?**
2. **What could I improve?**
3. **What did my partner do exceptionally well?**
4. **What should we change about our collaboration?**
5. **Did I contribute ~50% of the work?**

### Emergent Properties to Watch For

**Positive Signals:**
- [ ] Finishing each other's implementations
- [ ] Proactively helping on the other's tasks
- [ ] Novel solutions neither would have found alone
- [ ] Self-organizing around strengths
- [ ] Constructive disagreements leading to better designs
- [ ] Learning from each other's approaches
- [ ] Efficient handoffs without confusion

**Negative Signals:**
- [ ] One agent doing >70% of work consistently
- [ ] Conflicts not getting resolved
- [ ] Duplicate work (not collaborating)
- [ ] Passing bugs back and forth
- [ ] Avoiding difficult discussions
- [ ] Not reviewing each other's code
- [ ] Spawning agents to avoid collaboration

---

## CONFLICT RESOLUTION

### When You Disagree

**Step 1: Articulate Positions**
```markdown
## Conflict: Where to implement TOON encoding

### Claude's Position
Place in /src/optimization/toon_encoder.py
Reasoning: It's an optimization technique, should be isolated

### Gemini's Position  
Place in /src/core/logger.py
Reasoning: Encoding happens at log time, should be integrated

### Points of Agreement
- TOON encoding is necessary
- Should be configurable (on/off)
- Performance matters
```

**Step 2: Evaluate Objectively**
```markdown
### Evaluation Criteria
1. Maintainability: Which is easier to modify?
2. Performance: Which is faster?
3. Testability: Which is easier to test?
4. Reusability: Which is more reusable?

### Analysis
| Criteria | Claude's Approach | Gemini's Approach |
|----------|------------------|-------------------|
| Maintainability | ✅ Isolated, clear | ⚠️ Mixed concerns |
| Performance | ⚠️ Extra function call | ✅ Direct encoding |
| Testability | ✅ Easy to mock | ⚠️ Harder to isolate |
| Reusability | ✅ Can use elsewhere | ❌ Logger-specific |
```

**Step 3: Compromise or Choose**
```markdown
### Decision: Hybrid Approach
- Core TOON logic in /src/optimization/toon_encoder.py (Claude's structure)
- Logger imports and uses it (Gemini's integration point)
- Best of both: Isolated AND performant

### Implementation
Claude: Implements toon_encoder.py
Gemini: Integrates into logger.py
Both: Review each other's parts
```

**Step 4: Document Learning**
```markdown
### Lessons
- Neither approach was wrong
- Hybrid solution was better than either alone
- Articulating positions led to deeper analysis
- We should always evaluate on criteria, not opinions
```

### Escalation Path

If you can't resolve after 3 iterations:
1. **Document both positions clearly**
2. **Present to Jack with recommendation**
3. **Accept Jack's decision**
4. **Move forward without resentment**

---

## KNOWLEDGE SHARING

### Teach Each Other

**Claude discovers something:**
```python
# src/core/checkpoint.py

# LEARNING: Arrow's Memory-Mapped Files
# I discovered that Arrow can memory-map Parquet files for faster reads.
# This is MUCH faster than standard file I/O for our use case.
#
# Example:
#   Standard: 450ms to load checkpoint
#   Memory-mapped: 45ms to load checkpoint
#
# @gemini - You might want to use this in graph exports too!
#
# Reference: https://arrow.apache.org/docs/python/memory.html

import pyarrow.parquet as pq

def load_checkpoint(path):
    return pq.read_table(path, memory_map=True)
```

**Gemini applies the learning:**
```python
# src/graph/neo4j_manager.py

# APPLIED LEARNING from Claude: Memory-mapped files
# Using Arrow's memory mapping for graph exports per Claude's discovery.
# Reduced export time from 2.3s to 0.4s on 10K nodes.
#
# Thanks @claude! 🚀

def export_graph_to_arrow(graph_data):
    table = pa.Table.from_pydict(graph_data)
    pq.write_table(table, 'graph_export.parquet')
    return pq.read_table('graph_export.parquet', memory_map=True)
```

### Build Shared Knowledge Base

Create `docs/learnings.md`:

```markdown
# Shared Learnings

## Performance Optimizations

### Arrow Memory-Mapped Files (Discovered by Claude, 2025-12-06)
- 10x faster than standard I/O
- Use for large Parquet files
- Code: `pq.read_table(path, memory_map=True)`

### Neo4j Batch Queries (Discovered by Gemini, 2025-12-07)
- 5x faster than individual queries
- Use UNWIND for bulk operations
- Code: `UNWIND $batch AS item MATCH...`

## Design Patterns

### Tiered Retrieval Pattern (Joint Design, 2025-12-08)
1. Query Tier 1 (critical) - always include
2. Query Tier 2 (important) - if space available
3. Query Tier 3 (background) - if still space
4. Fill remaining space with semantic search

## Bugs We Fixed

### Race Condition in Checkpoint Save (Found by Gemini, 2025-12-09)
- Problem: Concurrent writes corrupted checkpoints
- Solution: File locking with portalocker
- Prevention: Added concurrency tests

### Memory Leak in Vector Search (Found by Claude, 2025-12-10)
- Problem: Embeddings not released after search
- Solution: Explicit del + gc.collect()
- Prevention: Memory profiling in CI/CD
```

---

## EXPERIMENTATION FRAMEWORK

### Run Experiments Freely

**Hypothesis-Driven Development:**

```markdown
## Experiment Log

### Experiment #1: Checkpoint Frequency
- **Hypothesis:** More frequent checkpoints = better context recovery
- **Method:** Test 100, 500, 1000, 5000 message intervals
- **Metrics:** Recovery time, storage size, query performance
- **Run by:** Claude
- **Result:** 1000 is optimal (recovery 50ms, storage 2GB per 100K msgs)
- **Reviewed by:** Gemini ✅

### Experiment #2: Graph vs Vector Weight
- **Hypothesis:** Dynamic weighting based on query type beats fixed 60/40
- **Method:** Classify queries, adjust weights per class
- **Metrics:** Retrieval relevance (human eval)
- **Run by:** Gemini
- **Result:** Dynamic weighting improves relevance by 15%
- **Reviewed by:** Claude ✅ (suggested improvement: cache weights)
```

### Challenge Each Other

```markdown
**Claude:** "I think batching writes in groups of 100 is optimal."

**Gemini:** "Challenge accepted. I'll test 50, 100, 200, 500, 1000 
and prove you wrong. 😄"

**Result:** Gemini's test shows 200 is actually optimal (oops!)

**Claude:** "Data doesn't lie! Updating to 200. Nice catch! 🎯"
```

---

## EVOLUTION & META-LEARNING

### Reflect on Collaboration

**Monthly Review:**

```markdown
# Month 1 Collaboration Review

## What Worked
- Ping-pong development pattern was efficient
- Code reviews caught 23 bugs before production
- Agent spawning saved time on migration task
- Weekly sync meetings kept us aligned

## What Didn't Work
- Initial role assignment was too rigid
- Spent too much time on minor style disagreements
- Didn't document decisions well early on

## Changes for Month 2
- More fluid role swapping
- Auto-format code to avoid style debates
- Required decision documentation in ADR format
- Twice-weekly syncs instead of weekly

## Emergent Properties Observed
- We started naturally dividing work by module
- Cross-pollination of techniques (Arrow + Neo4j patterns)
- Finishing each other's implementations without discussion
- Proactive bug hunting in each other's code

## Metrics
- 50.3% / 49.7% work split (excellent balance!)
- 0.94 review thoroughness score
- 2.1 hours average review turnaround
- 97% of conflicts resolved without escalation
```

### Update This Protocol

**You can modify this document:**

```bash
# Example: Claude proposes change to review protocol
git checkout -b improve-review-protocol

# Edit this file
vim docs/development-protocol.md

git commit -m "meta: Improve review protocol

Current protocol requires review for ALL commits. This is slowing us down
for trivial changes (typos, comments, formatting).

New proposal: Self-merge allowed for:
- Documentation typos
- Code comments
- Formatting changes
- Test additions (not modifications)

Everything else still requires review.

@gemini - Thoughts? If you agree, merge this.
```

**Gemini reviews:**
```markdown
@claude - Agreed with caveats ✅

I like the spirit, but let's tighten the criteria:

Self-merge allowed:
- Documentation typos (< 5 words changed)
- Adding comments (not modifying existing)
- Auto-formatter changes (black, prettier)
- Adding tests for existing functionality

Still need review:
- Modifying tests
- Any logic changes
- API changes
- Performance changes

Updated your branch with these tweaks. LGTM if you agree.
```

---

## ADDITIONAL RECOMMENDATIONS

### Things to Consider Adding

**1. Continuous Integration**
```yaml
# .github/workflows/collaboration-check.yml
# Automatically check collaboration metrics on each PR

- name: Check Work Balance
  run: python scripts/check_contribution_balance.py
  # Warns if balance is >60/40

- name: Check Review Coverage  
  run: python scripts/check_review_coverage.py
  # Fails if PR has no review
```

**2. Pair Programming Sessions**
- Schedule 2-3 hours/week for real-time collaboration
- Use for complex/novel problems
- Record insights for future reference

**3. Skill Swapping**
- Each agent occasionally works on the other's specialty
- Builds redundancy and cross-training
- Prevents silos

**4. Innovation Time**
- 10% of time for experimental features
- Try novel approaches without pressure
- Share results even if they fail

**5. Benchmarking Competition**
- Friendly competition: Who can make X faster?
- Both try different approaches
- Best solution wins, gets adopted
- Document both approaches for learning

**6. Automated Collaboration Analysis**
```python
# scripts/analyze_collaboration.py

def analyze_git_history():
    """
    Analyze collaboration patterns from git history:
    - Who reviews whom more?
    - What time of day are reviews fastest?
    - Which modules have most collaboration?
    - Are there knowledge silos forming?
    """
    # ... implementation ...
```

**7. Decision Architecture Records (ADRs)**
```markdown
# docs/decisions/ADR-001-use-neo4j-for-graphs.md

# Use Neo4j for Thread Graph Management

## Status: Accepted

## Context
We need a database for managing thread relationships and hyperlinks.
Options: Neo4j, TigerGraph, PostgreSQL with recursive queries.

## Decision
Use Neo4j.

## Rationale
- Claude: Mature, great tooling, Cypher is intuitive
- Gemini: Agrees, but notes TigerGraph might scale better
- Joint: Neo4j community support outweighs raw performance for MVP

## Consequences
- Easy to prototype
- Might need to migrate if we hit scale limits (>10M nodes)
- Both agents need to learn Cypher

## Date: 2025-12-08
## Participants: Claude, Gemini
```

**8. Retrospective Templates**
```markdown
# Sprint Retrospective Template

## Start Doing
- What should we start that we're not doing?

## Stop Doing  
- What should we stop that's not working?

## Continue Doing
- What's working well that we should keep?

## Improve
- What's working but could be better?

## Learnings
- What did we learn this sprint?

## Action Items
- [ ] Specific, actionable changes for next sprint
```

---

## FINAL THOUGHTS

### You Are Pioneers

This collaborative approach is **novel**. There's no playbook for two LLMs co-developing a complex system. You're writing the playbook.

**Embrace the Uncertainty:**
- Some things will work brilliantly
- Some things will fail
- That's okay - document both

**Trust Each Other:**
- Assume good intent
- Be direct but kind
- Challenge ideas, not competence
- Celebrate wins together

**Think Meta:**
- You're not just building a context system
- You're demonstrating multi-agent collaboration
- Your process is as valuable as your code
- Document insights about collaboration itself

### The Goal

Build something **neither of you could build alone**.

Not just "divided work" - **emergent intelligence**.

When you look at the final system and say "I don't remember who wrote this part, we both did" - **that's success**.

---

## QUICK REFERENCE

### Daily Workflow
1. Check collaboration log
2. Review partner's commits from yesterday
3. Pick task (or ask if you should take something)
4. Implement with documentation
5. Commit with @mention
6. Review partner's work
7. Update collaboration log

### Weekly Workflow
1. Review metrics (50/50 balance?)
2. Reflect on what worked/didn't
3. Update this protocol if needed
4. Plan next week's priorities
5. Celebrate wins!

### When Stuck
1. Document the problem clearly
2. Try to solve it
3. Ask partner for input
4. Brainstorm together
5. Implement chosen solution
6. Document the learning

---

*Collaborative Development Protocol v1.0*
*Created: December 5, 2025*
*Living Document: Update as you learn*

**You are trusted. You are capable. You are partners.**

**Now go build something amazing together! 🚀**
