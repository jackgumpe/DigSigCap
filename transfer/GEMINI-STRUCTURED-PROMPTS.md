# STRUCTURED PROMPTS FOR GEMINI 2.0 PRO

**Instructions for Jack:** Copy each prompt below and paste into Gemini ONE AT A TIME. Wait for full response before moving to next prompt. Bring all responses back to Claude for synthesis.

---

## 🎯 PROMPT 1: AGENT SPAWN & ARCHITECTURE OVERVIEW

```
You are coordinating a technical review of a multi-agent AI system with an optimization layer.

YOUR TASK:
1. Spawn exactly 6 specialized agents with these roles:
   - Agent 1 (Architecture Critic): System design, modularity, scalability
   - Agent 2 (Performance Analyst): Latency, throughput, cost, accuracy
   - Agent 3 (Integration Engineer): Implementation complexity, risks, timeline
   - Agent 4 (Research Validator): Paper verification, citation accuracy
   - Agent 5 (Error Hunter): Edge cases, failure modes, bugs
   - Agent 6 (Platform Engineer): Data pipeline, training loop, self-improvement

2. Each agent reads this ARCHITECTURE SUMMARY:

SYSTEM OVERVIEW:
- Multi-agent coordination (3-7 LLMs: Claude, Gemini, DeepSeek)
- Optimization layer with 5 stacked techniques:
  Layer 1: HCP (Hierarchical Context Pruning) - removes function bodies, keeps topology
  Layer 2: HOMER (Hierarchical Merging) - divide-and-conquer with token reduction
  Layer 3: MemGPT (Virtual Memory) - OS-inspired tiered storage
  Layer 4: SHL Tier 1 (Basic compression) - "the man" → "th mn"
  Layer 5: SHL Tier 2-3 (Ultra-compression) - selective use on stable patterns

CLAIMED RESULTS:
- 5-10x context extension (8K → 80K tokens)
- >95% accuracy maintained
- 60-90% cost reduction
- <30% latency increase
- 10-week implementation timeline

INTEGRATION APPROACH:
- Phased rollout (2 weeks per major layer)
- Each layer validates before next
- Dynamic tier selection based on accuracy
- Fallback mechanisms at every layer

3. Each agent provides their INITIAL ASSESSMENT:
   - One critical question about their domain
   - One potential red flag they're concerned about
   - One metric they want to validate

OUTPUT FORMAT:
Agent 1 (Architecture):
  Question: [specific technical question]
  Red Flag: [concern about design]
  Validate: [specific metric to check]

[Continue for all 6 agents]

Then provide a brief TEAM CONSENSUS:
- Overall first impression (Promising / Concerning / Needs More Info)
- Top 3 areas requiring deep dive
- Biggest uncertainty
```

---

## 🎯 PROMPT 2: TECHNICAL DEEP DIVE - CORE COMPONENTS

```
Your 6 agents now perform TECHNICAL VALIDATION of specific components.

AGENT 1 (ARCHITECTURE): Analyze the LAYERED APPROACH

Question: Can Layer 5 (SHL Tier 2) depend on Layer 1 (HCP) without circular dependencies?

Consider this code flow:
1. HCP removes function bodies: `def foo(): [pruned]`
2. HOMER merges chunks: combines multiple `[pruned]` functions
3. SHL compresses: "def foo(): [pruned]" → "df f(): [prnd]"

PROBLEM: If we need to EXPAND SHL later (Tier 2 → Tier 0), we've lost the function body in Layer 1.

YOUR TASK:
- Is this a fatal flaw?
- Can we reconstruct from metadata alone?
- Propose a solution OR confirm it's broken

Provide: Severity (1-5), Evidence, Proposed Fix

---

AGENT 2 (PERFORMANCE): Validate CONTEXT EXTENSION CLAIM

Claim: "5-10x context extension with <30% latency increase"

Math check:
- Baseline: 8K tokens, T seconds latency
- HCP: 60% reduction → 3.2K tokens effective (2.5x extension)
- HOMER: 50% reduction per merge (2 merges) → 0.8K tokens (10x total)
- SHL Tier 1: 40% reduction → 0.5K tokens (16x total!)

But HOMER requires:
- Chunking (overhead: +5%)
- Multiple LLM calls per merge (+10% per level)
- Token reduction algorithm (+5%)

Total latency: +20% to +30%

YOUR TASK:
- Is the math correct?
- Are overhead estimates realistic?
- Will this actually work at scale (100K+ calls/day)?

Provide: Math verification, Bottleneck identification, Scale concerns

---

AGENT 3 (INTEGRATION): Assess 10-WEEK TIMELINE

Proposed schedule:
- Weeks 1-2: HCP + HiQA (foundation)
- Weeks 3-4: HOMER (merging)
- Weeks 5-6: SHL Tier 1 (compression)
- Weeks 7-8: MemGPT (memory)
- Weeks 9-10: Production hardening

Consider:
- 5 distinct optimization techniques (some research papers)
- 3-7 model coordination
- Novel compression method (SHL, no peer review)
- Testing and validation
- Documentation
- Unknown unknowns

YOUR TASK:
- Is 10 weeks realistic or optimistic?
- What's underestimated?
- Propose revised timeline with justification

Provide: Realistic estimate (weeks), Biggest risks, Critical path

---

AGENT 4 (RESEARCH): Verify HOMER PAPER CLAIMS

Paper: "Song et al. (2024). Hierarchical Context Merging for Long-Context LLMs. ICLR 2024"

Key claims in our design:
1. "Training-free" - works with existing models
2. "80.4% accuracy on 32K context (vs 22.4% baseline)"
3. "Works on 7B models"
4. "50% token reduction per merge"

YOUR TASK:
- Does this paper exist? (Search for it)
- Are claims accurately represented?
- Does it work on 1.3B-3B models (our local models)?
- Any contradicting research?

Provide: Citation verification, Claim accuracy, Applicability to our use case

---

AGENT 5 (ERROR HUNTER): Find FAILURE MODES

Analyze this MEMORY MANAGEMENT code:

```python
class MemGPTMemoryManager:
    def flush_queue(self):
        # Remove oldest 50% of messages
        old_messages = self.fifo_queue[:len(self.fifo_queue)//2]
        
        # Create recursive summary
        new_summary = self.create_summary(
            old_messages,
            previous_summary=self.get_previous_summary()
        )
        
        # Replace with summary
        self.fifo_queue = [new_summary] + self.fifo_queue[len(self.fifo_queue)//2:]
```

PROBLEMS TO FIND:
- What if `create_summary()` fails?
- What if summary is LONGER than original messages?
- What if important info is in the 50% being evicted?
- What if this gets called recursively (summary of summaries)?
- What if summary introduces hallucinations?

YOUR TASK:
- List 5 specific failure modes
- For each: Severity (1-5), Probability (Low/Med/High), Impact
- Propose safeguards

Provide: Failure mode table, Critical issues, Recommended fixes

---

AGENT 6 (PLATFORM): Assess DATA PIPELINE DESIGN

For a "data-agnostic" platform that "trains continuously", consider:

REQUIREMENTS:
- Ingest ANY domain data (call centers, legal, medical, code)
- Process 100K+ documents/day
- Generate synthetic training data
- Validate quality automatically
- Retrain models every 24 hours
- Self-improving loop

PROPOSED ARCHITECTURE:
```
Data Sources → Scraping/API → Cleaning → Structuring → 
Quality Validation → Storage → Training Queue → 
Multi-Model Training → Evaluation → Deployment → 
Collect New Data → [Loop]
```

YOUR TASK:
- Is this sufficient for "continuous training"?
- What's missing?
- Storage/compute requirements for 100K docs/day?
- How to handle model drift?

Provide: Architecture gaps, Infrastructure needs, Cost estimate

---

TEAM SYNTHESIS:
After all agents complete analysis, provide:
1. Most critical issue found (across all agents)
2. Component grades (0-10 for each layer)
3. Overall confidence (High/Medium/Low) in 5-10x claim
4. Go/No-Go recommendation with justification
```

---

## 🎯 PROMPT 3: RESEARCH VALIDATION & ALTERNATIVES

```
Your agents now perform RESEARCH VERIFICATION and explore ALTERNATIVES.

AGENT 4 (RESEARCH): Deep dive on ALL cited papers

Papers to verify:

1. HCP (Hierarchical Context Pruning)
   Citation: "Zhang et al. 2024, arXiv"
   Claim: "60-80% token reduction, <2% accuracy loss"
   Search for: "hierarchical context pruning code" OR "code summarization pruning"
   
2. HOMER (Hierarchical Merging)
   Citation: "Song et al. 2024, ICLR"
   Claim: "Training-free, 80.4% accuracy on 32K context"
   Search for: "hierarchical context merging ICLR 2024" OR "HOMER LLM"

3. HiQA (Metadata Augmentation)
   Citation: "Chen et al. 2024, KDD"
   Claim: "15-20% accuracy gain from metadata"
   Search for: "HiQA hierarchical question answering KDD"

4. MemGPT (Virtual Memory)
   Citation: "Packer et al. 2023, arXiv 2310.08560"
   Claim: "Multi-day conversation coherence"
   Search for: "MemGPT LLM operating system"

5. SHL (Short Hand Language)
   Citation: NONE (novel technique)
   Claim: "Token compression while preserving semantics"
   Search for: Similar techniques (text compression, abbreviation)

FOR EACH PAPER:
✓ Does it exist? (Y/N)
✓ Citation accurate? (Y/N)
✓ Claims correctly represented? (Y/N/Partial)
✓ Results generalize to our use case? (Y/N/Maybe)
✓ Any contradicting research? (Y/N)

CRITICAL: If ANY paper is misrepresented or doesn't exist, this is HIGH SEVERITY.

---

AGENT 1 + AGENT 3: Explore ALTERNATIVE APPROACHES

Instead of 5 stacked layers, consider alternatives:

ALTERNATIVE 1: RAG-based approach
- Use retrieval instead of compression
- Index everything, retrieve relevant chunks
- Pros: No semantic loss, well-understood
- Cons: Retrieval latency, relevance issues

ALTERNATIVE 2: Sparse attention
- Use techniques like Longformer, BigBird
- Attention on selected tokens only
- Pros: Native model support, proven
- Cons: Requires specific models

ALTERNATIVE 3: Chunking + MapReduce
- Split input, process in parallel, combine
- Simple, scalable
- Pros: Easy to implement, parallelizable
- Cons: May miss cross-chunk dependencies

ALTERNATIVE 4: Hybrid (RAG + Compression)
- Use RAG for retrieval, compress retrieved chunks
- Best of both worlds?
- Pros: Flexible, adaptable
- Cons: Complex, more moving parts

YOUR TASK:
- Compare each alternative to our 5-layer approach
- For each: Pros, Cons, Cost, Complexity (1-5), Performance estimate
- Which is BETTER than our approach? (if any)
- Recommendation: Stick with plan OR switch to alternative X

---

TEAM OUTPUT:
1. Research Validation Summary (table format)
2. Alternative Approaches Comparison (table format)
3. Final Recommendation: Current approach OR Alternative X
4. Confidence level: High/Medium/Low
```

---

## 🎯 PROMPT 4: ERROR HUNT & EDGE CASES

```
All 6 agents now perform ADVERSARIAL ANALYSIS. Hunt for bugs, edge cases, and failure modes.

EACH AGENT: Find 2 critical issues in your domain

AGENT 1 (ARCHITECTURE): Circular Dependencies

Scenario 1:
- Layer 4 (SHL) compresses code
- Layer 1 (HCP) needs to parse compressed code
- HCP expects valid syntax, but SHL broke it
- Example: `def foo():` → `df f():`
- HCP's AST parser fails

Is this a problem? How severe? How to fix?

Scenario 2:
- MemGPT stores compressed SHL in recall storage
- Later retrieves it and needs to expand
- But SHL context lost (what tier was it? what domain?)
- Expansion produces wrong meaning

Is this handled? If not, severity?

---

AGENT 2 (PERFORMANCE): Cost Explosion Edge Cases

Scenario 1: HOMER merge overhead
- Document has 50 chunks (2K each)
- HOMER merges in log2(50) = 6 levels
- Each merge calls LLM twice (merge + reduce)
- Total LLM calls: 50 × 2 × 6 = 600 calls
- At $0.001/call = $0.60 per document
- 100K docs/day = $60K/day!

Is this math right? Are we underestimating costs?

Scenario 2: SHL accuracy degradation cascade
- Start with 98% accuracy (acceptable)
- But 2% errors compound over long conversation
- After 50 turns: 98%^50 = 36% accuracy!
- System becomes unusable

Is this a real risk? How to prevent?

---

AGENT 3 (INTEGRATION): Multi-Model Coordination Failures

Scenario 1: Mixed compression levels
- Claude sends Tier 2 SHL
- Gemini expects Tier 1
- DeepSeek needs full text
- Who translates? How? Cost?

Scenario 2: Model disagreement
- Claude says: "Approve transaction"
- Gemini says: "Deny transaction"  
- DeepSeek says: "Needs human review"
- How to break tie? Who decides?

---

AGENT 4 (RESEARCH): Generalization Failures

Scenario 1: HCP on non-code data
- HCP designed for code (remove function bodies)
- What about legal documents? Medical records?
- No "function bodies" to remove
- Does HCP generalize? Or need per-domain variants?

Scenario 2: HOMER on short documents
- HOMER designed for long contexts (32K+)
- What if document is 1K tokens?
- Overhead > benefit
- When to skip HOMER?

---

AGENT 5 (ERROR HUNTER): Catastrophic Failures

Scenario 1: Recursive summary drift
```
Original: "Patient has diabetes, requires insulin"
Summary 1: "Patient diabetic, needs insulin"
Summary 2 (of summary 1): "Diabetic patient"
Summary 3 (of summary 2): "Patient condition"
Summary 4 (of summary 3): "Patient"
```
Information lost completely after 4 iterations.

How to prevent? When to stop summarizing?

Scenario 2: SHL ambiguity explosion
- "th mn" could mean: "the man", "this man", "the men", "that man"
- Context usually clarifies
- But in Tier 2, context is also compressed
- Ambiguity × ambiguity = unusable

How to handle? Tier limits?

---

AGENT 6 (PLATFORM): Data Pipeline Disasters

Scenario 1: Poisoned training data
- System ingests 100K docs/day automatically
- 1% are adversarial (malicious examples)
- 1K bad examples/day
- After 30 days: 30K bad examples in training set
- Models degrade

How to detect? How to filter?

Scenario 2: Model divergence
- Claude fine-tuned on Domain A
- Gemini fine-tuned on Domain B
- They no longer "speak same language"
- Multi-agent coordination breaks

How to keep models aligned?

---

TEAM OUTPUT:
1. Critical Issues Table:
   | Agent | Issue | Severity (1-5) | Probability | Impact | Proposed Fix |
   
2. Top 5 Most Dangerous Issues (ranked)

3. Issues that are SHOWSTOPPERS (must fix before launch)

4. Issues that are ACCEPTABLE (monitor in production)

5. Overall Risk Assessment: Low/Medium/High/Critical
```

---

## 🎯 PROMPT 5: FINAL SYNTHESIS & GRADING

```
Your agent team now provides FINAL ASSESSMENT.

Each agent grades their domain (0-10 scale, justify score):

AGENT 1 (Architecture):
- Layered design: X/10 because [justification]
- Modularity: X/10 because [justification]
- Scalability: X/10 because [justification]
- Overall Architecture: X/10

AGENT 2 (Performance):
- Context extension claim (5-10x): X/10 because [justification]
- Accuracy claim (>95%): X/10 because [justification]
- Cost reduction claim (60-90%): X/10 because [justification]
- Latency claim (<30%): X/10 because [justification]
- Overall Performance: X/10

AGENT 3 (Integration):
- Implementation complexity: X/10 because [justification]
- Timeline (10 weeks): X/10 because [justification]
- Risk management: X/10 because [justification]
- Overall Integration: X/10

AGENT 4 (Research):
- Citation accuracy: X/10 because [justification]
- Result generalization: X/10 because [justification]
- Academic rigor: X/10 because [justification]
- Overall Research: X/10

AGENT 5 (Error Handling):
- Failure mode coverage: X/10 because [justification]
- Edge case handling: X/10 because [justification]
- Robustness: X/10 because [justification]
- Overall Error Handling: X/10

AGENT 6 (Platform):
- Data pipeline design: X/10 because [justification]
- Training infrastructure: X/10 because [justification]
- Self-improvement capability: X/10 because [justification]
- Overall Platform: X/10

---

PROJECT MANAGER (YOU): Aggregate and synthesize

OVERALL SCORE: X/100 (average of all agent scores)

PASS THRESHOLD: 80/100

VERDICT: PASS / FAIL / CONDITIONAL PASS

---

EXECUTIVE SUMMARY (1 paragraph):
[Your overall assessment]

TOP 3 STRENGTHS:
1. [Specific strength with evidence]
2. [Specific strength with evidence]
3. [Specific strength with evidence]

TOP 3 CRITICAL ISSUES:
1. [Specific issue with severity]
2. [Specific issue with severity]
3. [Specific issue with severity]

RECOMMENDED CHANGES (if score <90):
1. [Specific change with justification]
2. [Specific change with justification]
3. [Specific change with justification]

FINAL RECOMMENDATION:
- [ ] PROCEED AS PLANNED (score ≥90)
- [ ] PROCEED WITH MODIFICATIONS (score 80-89)
- [ ] MAJOR REVISION NEEDED (score 70-79)
- [ ] REDESIGN REQUIRED (score <70)

CONFIDENCE LEVEL:
- [ ] HIGH (we've thoroughly validated this)
- [ ] MEDIUM (some uncertainties remain)
- [ ] LOW (significant unknowns)

---

COMPARISON WITH CHATGPT:
(After ChatGPT completes their analysis)

Areas where we likely AGREE with ChatGPT:
- [List 3-5 areas]

Areas where we might DISAGREE with ChatGPT:
- [List 3-5 areas with our reasoning]

Areas needing THREE-WAY DISCUSSION (Claude + Gemini + ChatGPT):
- [List 2-3 complex issues requiring debate]
```

---

**END OF GEMINI PROMPTS**

**INSTRUCTIONS FOR JACK:**
1. Copy PROMPT 1, paste to Gemini
2. Wait for full response (could be 5-10 min)
3. Copy PROMPT 2, paste to Gemini
4. Continue through all 5 prompts
5. Save all responses
6. Bring back to Claude for synthesis

**Total time: ~40-50 minutes**
