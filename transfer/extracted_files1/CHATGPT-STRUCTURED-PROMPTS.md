# STRUCTURED PROMPTS FOR CHATGPT

**Instructions for Jack:** Copy each prompt below and paste into ChatGPT ONE AT A TIME. Wait for full response before moving to next prompt. Bring all responses back to Claude for synthesis.

**IMPORTANT:** Your analysis should be INDEPENDENT from Gemini's. Don't assume they're right. Challenge everything.

---

## 🎯 PROMPT 1: AGENT SPAWN & RESEARCH-FIRST APPROACH

```
You are leading an INDEPENDENT technical critique of a multi-agent AI system.

YOUR TASK:
1. Spawn exactly 5 specialized agents (different from Gemini's 6):
   - Agent 1 (Research Validator): Verify ALL papers, citations, claims
   - Agent 2 (Cost Analyst): Deep dive on economics, TCO, scale
   - Agent 3 (Implementation Realist): Challenge timelines, complexity
   - Agent 4 (Alternative Architect): Propose better approaches
   - Agent 5 (Devil's Advocate): Find reasons this WON'T work

2. Read this SYSTEM SUMMARY:

OPTIMIZATION LAYER (5 stacked techniques):
- Layer 1: HCP (code pruning) - 60-80% reduction
- Layer 2: HOMER (hierarchical merge) - 50% per merge
- Layer 3: MemGPT (virtual memory) - OS-inspired
- Layer 4: SHL Tier 1 (compression) - "the" → "th"
- Layer 5: SHL Tier 2 (ultra) - selective use

BOLD CLAIMS:
- 5-10x context extension
- >95% accuracy
- 60-90% cost reduction
- 10-week implementation

3. Each agent provides INITIAL SKEPTICISM:
   - One claim you doubt most
   - One assumption that seems wrong
   - One paper you want to verify first

OUTPUT FORMAT:
Agent 1 (Research):
  Doubt: [which claim seems exaggerated]
  Wrong Assumption: [flawed premise]
  Verify First: [which paper to check]

[Continue for all 5 agents]

TEAM CONSENSUS:
- Initial impression: Too Optimistic / Reasonable / Conservative
- Biggest red flag
- What needs immediate verification
```

---

## 🎯 PROMPT 2: RESEARCH DEEP DIVE - PAPER VERIFICATION

```
AGENT 1 (RESEARCH VALIDATOR): Your PRIMARY task

You must verify EVERY cited paper. This is CRITICAL.

PAPERS TO CHECK:

1. **HCP (Hierarchical Context Pruning)**
   Citation: "Zhang et al. 2024, arXiv"
   Claimed result: "60-80% token reduction, <2% accuracy loss"
   
   SEARCH TERMS:
   - "hierarchical context pruning"
   - "code summarization pruning 2024"
   - "function body removal context"
   
   VERIFY:
   a) Does this paper exist?
   b) Authors correct?
   c) Results match claims?
   d) Any contradicting papers?
   
2. **HOMER (Hierarchical Context Merging)**  
   Citation: "Song et al. 2024, ICLR"
   Claimed result: "Training-free, 80.4% vs 22.4% baseline"
   
   SEARCH TERMS:
   - "HOMER ICLR 2024"
   - "hierarchical context merging"
   - "Song hierarchical merging"
   
   VERIFY:
   a) Accepted to ICLR 2024?
   b) Training-free confirmed?
   c) Works on small models (1.3B-3B)?
   d) Token reduction rate specified?

3. **HiQA (Metadata Augmentation)**
   Citation: "Chen et al. 2024, KDD"  
   Claimed result: "15-20% accuracy gain"
   
   SEARCH TERMS:
   - "HiQA KDD 2024"
   - "hierarchical question answering"
   - "metadata augmentation"
   
   VERIFY:
   a) Published in KDD 2024?
   b) Multi-document QA focus?
   c) Code tasks mentioned?
   d) Metadata overhead specified?

4. **MemGPT (Virtual Memory for LLMs)**
   Citation: "Packer et al. 2023, arXiv 2310.08560"
   Claimed result: "Multi-day conversation coherence"
   
   SEARCH TERMS:
   - "MemGPT arXiv"
   - "LLM operating system"
   - "Packer 2310.08560"
   
   VERIFY:
   a) Paper exists at that arXiv number?
   b) OS-inspired design confirmed?
   c) Production-tested?
   d) Scalability data?

5. **SHL (Short Hand Language)**
   Citation: NONE (novel, not peer-reviewed)
   Claimed result: "Token compression, preserves semantics"
   
   SEARCH TERMS:
   - "text compression LLM"
   - "abbreviation semantic preservation"
   - "lossy text compression"
   
   VERIFY:
   a) Any similar academic work?
   b) Abbreviation techniques in NLP?
   c) Known failure modes?
   d) Why isn't this published?

---

FOR EACH PAPER, PROVIDE:

| Paper | Exists? | Citation Accurate? | Claims Match? | Generalize? | Grade (A-F) |
|-------|---------|-------------------|---------------|-------------|-------------|
| HCP   | Y/N     | Y/N               | Y/N/Partial   | Y/N/Maybe   | X           |
| ...   | ...     | ...               | ...           | ...         | ...         |

CRITICAL FINDINGS:
- Papers that DON'T exist: [list]
- Misrepresented claims: [list with corrections]
- Missing disclaimers: [list]

OVERALL RESEARCH GRADE: X/100

If grade <80, this is a RED FLAG for the entire project.
```

---

## 🎯 PROMPT 3: COST REALITY CHECK & SCALE ANALYSIS

```
AGENT 2 (COST ANALYST): Calculate TRUE costs at scale

CLAIMED: "60-90% cost reduction"

Let's verify with REAL numbers:

SCENARIO 1: Development Phase (100K calls/month)

WITHOUT optimization:
- Claude input: 7M tokens × $3/M = $21
- Claude output: 3M tokens × $15/M = $45
- Gemini input: 7M × $0.075/M = $0.52
- Gemini output: 3M × $0.30/M = $0.90
- DeepSeek input: 7M × $0.56/M = $3.92
- DeepSeek output: 3M × $1.68/M = $5.04
TOTAL: $76.38/month

WITH optimization (claimed 85% reduction):
- Input: 1M tokens (all models)
- Output: 450K tokens (all models)
TOTAL: $11.03/month

SAVINGS: $65/month (85% reduction) ✓ Matches claim

BUT WAIT - hidden costs:

HOMER merging overhead:
- 50 chunks per document
- 6 merge levels (log2(50))
- 2 LLM calls per merge
- 600 extra LLM calls per document!
- Cost: $0.60/document (at $0.001/call)

At 100K documents/month:
- HOMER overhead: $60K/month
- Original savings: $65/month
- NET COST: -$59,935/month! 🚨

IS THIS MATH RIGHT? OR ARE ASSUMPTIONS WRONG?

---

SCENARIO 2: Production Scale (10M calls/month)

Traditional call center: $3.5M/month (labor)
AI system (claimed): $17K/month

ACTUAL costs to verify:
1. API costs: ~$10K
2. GPU servers: $2K
3. Storage: $500
4. Voice TTS: $1K
5. Voice STT: $2K
6. Engineers: $10K
7. **HOMER overhead: $6M/month** 🚨

If HOMER actually costs this much, system is MORE expensive than humans!

YOUR TASK:
- Find the error in my math
- OR confirm HOMER is a cost disaster
- OR explain why documents won't have 50 chunks
- Provide realistic cost estimate

---

SCENARIO 3: Self-Hosted (avoiding API costs)

Claim: "Self-host DeepSeek, pay only GPU/power"

Reality check:
- DeepSeek 671B model (sparse, 37B active)
- Needs: 8× A100 GPUs minimum
- Hardware: $80K (one-time)
- Power: 5kW × $0.12/kWh × 24h × 30d = $4,320/month
- Cooling: $2K/month
- Bandwidth: $1K/month
- Maintenance: $3K/month

TOTAL: $10,320/month (just to run hardware)

vs. DeepSeek API: $1.07/month for 100K calls

Self-hosting is 10,000× MORE EXPENSIVE at this scale!

When does self-hosting break even?
- Need 10M+ calls/month
- $100K+ in API costs
- Only then does $10K hardware cost make sense

YOUR TASK:
- Validate break-even math
- Recommend: API or self-host?
- What scale does self-host make sense?

---

FINAL COST ANALYSIS:

TRUE monthly cost at 100K calls: $X
TRUE monthly cost at 1M calls: $X
TRUE monthly cost at 10M calls: $X

Break-even vs traditional call center: X calls/month

REALISTIC savings claim: X% (vs claimed 60-90%)

GRADE COST ANALYSIS: X/100
```

---

## 🎯 PROMPT 4: IMPLEMENTATION REALITY & TIMELINE CHALLENGE

```
AGENT 3 (IMPLEMENTATION REALIST): Challenge the 10-week timeline

PROPOSED TIMELINE:
- Weeks 1-2: HCP + HiQA
- Weeks 3-4: HOMER
- Weeks 5-6: SHL Tier 1
- Weeks 7-8: MemGPT
- Weeks 9-10: Production

Let's break down ACTUAL work for EACH phase:

---

WEEKS 1-2: HCP + HiQA

HCP Implementation:
- [ ] Research HCP paper (if exists)
- [ ] Choose AST parser (Python: 1 day, multi-language: 1 week)
- [ ] Implement pruning logic (3-5 days)
- [ ] Test on 10+ languages (1 week)
- [ ] Handle edge cases (closures, decorators, etc) (1 week)
- [ ] Integration with existing system (3 days)
- [ ] Testing (3 days)

HiQA Metadata:
- [ ] Design metadata schema (2 days)
- [ ] Implement cascading logic (3 days)
- [ ] Integration (2 days)
- [ ] Testing (2 days)

ACTUAL TIME: 4-5 weeks (vs proposed 2)

---

WEEKS 3-4: HOMER

If HOMER paper exists:
- [ ] Read and understand paper (3 days)
- [ ] Implement chunking algorithm (2 days)
- [ ] Implement merging logic (1 week)
- [ ] Token reduction algorithm (needs research: 1 week)
- [ ] Multi-level recursion (3 days)
- [ ] Testing on long documents (1 week)
- [ ] Optimize performance (1 week)
- [ ] Integration (3 days)

If HOMER paper doesn't exist:
- [ ] Design from scratch (2 weeks)
- [ ] Prototype (2 weeks)  
- [ ] Validate (2 weeks)
- [ ] etc...

ACTUAL TIME: 5-8 weeks (vs proposed 2)

---

WEEKS 5-6: SHL

SHL has NO peer review, so MORE risk:
- [ ] Design tier system (1 week)
- [ ] Build canonical meaning table (2 weeks - needs 1000s of entries)
- [ ] Implement encoder/decoder (1 week)
- [ ] Round-trip testing framework (1 week)
- [ ] Synthetic data generation (1 week)
- [ ] Accuracy validation (2 weeks)
- [ ] Dynamic tier selection (1 week)
- [ ] Edge case handling (2 weeks)

ACTUAL TIME: 8-10 weeks (vs proposed 2)

---

WEEKS 7-8: MemGPT

- [ ] Study MemGPT paper (3 days)
- [ ] Implement FIFO queue (2 days)
- [ ] Implement recall storage (1 week)
- [ ] Implement archival storage (1 week)
- [ ] Queue manager with eviction (1 week)
- [ ] Recursive summarization (1 week)
- [ ] Function executor (1 week)
- [ ] Testing long conversations (2 weeks)
- [ ] Memory leak prevention (1 week)

ACTUAL TIME: 6-8 weeks (vs proposed 2)

---

WEEKS 9-10: Production

"Production hardening" is NOT 2 weeks:
- [ ] Load testing (2 weeks)
- [ ] Stress testing (1 week)
- [ ] Security audit (1 week)
- [ ] Performance optimization (2 weeks)
- [ ] Monitoring setup (1 week)
- [ ] Alerting (1 week)
- [ ] Documentation (2 weeks)
- [ ] Team training (1 week)
- [ ] Gradual rollout (2 weeks)
- [ ] Bug fixes from rollout (2-4 weeks)

ACTUAL TIME: 10-15 weeks (vs proposed 2)

---

YOUR TASK:
1. Add up ACTUAL time: X weeks
2. Compare to proposed: 10 weeks
3. Calculate underestimation: X%
4. Identify critical path (longest dependency chain)
5. Propose REALISTIC timeline

REALISTIC TIMELINE:
- Phase 1: X weeks
- Phase 2: X weeks
- Phase 3: X weeks
- Phase 4: X weeks
- Phase 5: X weeks
TOTAL: X weeks (vs claimed 10)

GRADE TIMELINE: X/100 (based on realism)
```

---

## 🎯 PROMPT 5: ALTERNATIVE APPROACHES & FINAL VERDICT

```
AGENT 4 (ALTERNATIVE ARCHITECT): Propose BETTER approaches

CURRENT APPROACH: 5-layer stack (HCP → HOMER → MemGPT → SHL → SHL)

Issues identified:
- Complex (5 layers)
- Unproven (SHL not peer-reviewed)
- Expensive (HOMER overhead?)
- Risky (10-week timeline unrealistic)

YOUR TASK: Design 3 ALTERNATIVE approaches that are SIMPLER and MORE RELIABLE

---

ALTERNATIVE 1: RAG + Sparse Attention

Instead of compression, use retrieval:
- Index all code/docs with embeddings
- Retrieve top-K relevant chunks (K=10-20)
- Use Longformer/BigBird for extended context
- Simple, proven, no semantic loss

ARCHITECTURE:
```
User Query → Embedding → Vector Search (top-K) → 
Sparse Attention Model → Response
```

PROS:
- No compression = no semantic loss
- Well-understood (RAG is proven)
- Sparse attention models exist (Longformer)
- Easy to debug

CONS:
- Retrieval latency (~100ms)
- Relevance issues (might miss context)
- Still limited by model context (4K-16K)

COMPLEXITY: 3/10 (vs 9/10 for 5-layer)
TIMELINE: 4 weeks (vs 23+ weeks real)
COST: Similar or lower
RELIABILITY: 9/10 (vs 6/10 for unproven)

---

ALTERNATIVE 2: Simple Chunking + Iterative Refinement

Don't try to fit everything in context:
- Chunk document into sections
- Process each section independently
- Iteratively refine with previous results
- Final synthesis pass

ARCHITECTURE:
```
Long Document → Chunks → Process in Parallel → 
Aggregate Results → Refine → Final Output
```

PROS:
- Dead simple (no novel techniques)
- Parallelizable (fast)
- Works with ANY model
- Easy to implement

CONS:
- May miss cross-chunk dependencies
- Multiple API calls (cost)
- Synthesis quality depends on refinement

COMPLEXITY: 2/10
TIMELINE: 2 weeks
COST: 2-3× original (multiple calls per chunk)
RELIABILITY: 8/10

---

ALTERNATIVE 3: Hybrid (Proven Techniques Only)

Use ONLY peer-reviewed, proven methods:
- MemGPT for memory (proven in paper)
- HCP for code pruning (if paper exists)
- RAG for retrieval
- Skip HOMER (unverified overhead)
- Skip SHL (not peer-reviewed)

ARCHITECTURE:
```
MemGPT (memory management) + 
HCP (code pruning) +
RAG (retrieval for missing context)
```

PROS:
- All techniques validated
- Lower risk
- Simpler (3 components vs 5)
- Realistic timeline (6-8 weeks)

CONS:
- Lower context extension (3-5x vs 5-10x)
- Still some complexity

COMPLEXITY: 5/10
TIMELINE: 6-8 weeks
COST: Similar
RELIABILITY: 8/10

---

YOUR COMPARISON TABLE:

| Approach | Complexity | Timeline | Cost | Reliability | Context Extension | Grade |
|----------|------------|----------|------|-------------|-------------------|-------|
| Current (5-layer) | 9/10 | 23+ weeks | $ | 6/10 | 5-10x | ? |
| Alt 1 (RAG) | 3/10 | 4 weeks | $$ | 9/10 | 2-3x | ? |
| Alt 2 (Chunking) | 2/10 | 2 weeks | $$$ | 8/10 | 1-2x | ? |
| Alt 3 (Hybrid) | 5/10 | 6-8 weeks | $ | 8/10 | 3-5x | ? |

YOUR RECOMMENDATION:
- Best overall: [X]
- Why: [justification]
- Trade-offs accepted: [list]

---

AGENT 5 (DEVIL'S ADVOCATE): Final argument AGAINST current approach

List 10 reasons this project will FAIL:
1. [Specific reason with evidence]
2. [Specific reason with evidence]
...
10. [Specific reason with evidence]

Most damning issue: [X]

---

FINAL TEAM VERDICT:

OVERALL GRADE: X/100

VERDICT:
- [ ] APPROVE CURRENT PLAN (grade ≥85)
- [ ] APPROVE WITH MODIFICATIONS (grade 70-84)
- [ ] RECOMMEND ALTERNATIVE (grade 60-69)
- [ ] REJECT, REDESIGN (grade <60)

EXECUTIVE SUMMARY:
[2-3 paragraphs: What works, what doesn't, what to do]

TOP 3 CHANGES NEEDED:
1. [Specific change]
2. [Specific change]
3. [Specific change]

COMPARISON WITH GEMINI (predict their findings):
- We probably agree on: [X, Y, Z]
- We probably disagree on: [A, B, C]
- Our unique insights: [D, E, F]
```

---

**END OF CHATGPT PROMPTS**

**INSTRUCTIONS FOR JACK:**
1. Run these AFTER Gemini (or in parallel if you want)
2. Paste each prompt one at a time
3. Wait for full responses
4. Save everything
5. Bring back to Claude for three-way synthesis

**Total time: ~40-50 minutes**

**KEY DIFFERENCE:** ChatGPT will be more skeptical, focus on costs/timeline, and propose alternatives. This gives us BALANCE against Gemini's analysis.
