# STRUCTURED PROMPTS FOR GEMINI 2.0 PRO

**Instructions:** Paste these prompts ONE AT A TIME. Wait for Gemini's full response before moving to the next prompt.

---

## PROMPT 1: AGENT SPAWN & INITIAL ASSESSMENT

```
You are being handed a multi-agent AI system with an optimization layer designed to achieve 5-10x context extension while maintaining >95% accuracy.

TASK 1: Spawn exactly 6 specialized agents:
1. Architecture Critic - Evaluates system design, modularity, integration
2. Performance Analyst - Validates performance claims, identifies bottlenecks
3. Research Validator - Verifies paper citations, checks methodology transfer
4. Error Detective - Hunts for bugs, edge cases, failure modes
5. Implementation Engineer - Assesses complexity, timeline, feasibility
6. Cost Analyst - Validates economic claims, finds hidden costs

TASK 2: Each agent reads the OPTIMIZATION-LAYER-SYNTHESIS document and identifies:
- Their top 3 concerns (specific issues, not vague)
- Their confidence level on key claims (0-100%)
- One critical question that MUST be answered

TASK 3: Project Manager (you) aggregates findings into:
- Top 5 system-wide concerns (ranked by severity)
- Top 3 claims needing validation
- Initial confidence score (0-100) on overall approach

Format your response as:
```
AGENT 1 (Architecture Critic):
  Concern 1: [specific issue]
  Concern 2: [specific issue]
  Concern 3: [specific issue]
  Confidence on "5-10x context extension": X%
  Critical Question: [question]

[Repeat for all 6 agents]

PROJECT MANAGER SYNTHESIS:
  Top 5 System Concerns:
    1. [concern] - Severity: [HIGH/MED/LOW]
    2. ...
  
  Top 3 Claims Needing Validation:
    1. [claim]
    2. [claim]
    3. [claim]
  
  Initial Confidence Score: X/100
```

BEGIN NOW.
```

---

## PROMPT 2: TECHNICAL DEEP DIVE - SHL COMPRESSION

```
Based on your initial assessment, now dive deep into the SHL (Short Hand Language) compression technique.

SCENARIO: SHL claims to reduce tokens while preserving semantics through multi-tier compression.

Example:
- Tier 0: "The man went to the park"
- Tier 1: "th mn wnt 2 th prk"
- Tier 2: "mn→prk"

CRITICAL ANALYSIS REQUIRED:

Agent 1 (Architecture Critic): Analyze the SHLCodec design:
```python
class SHLCodec:
    def compress(self, text: str, tier: int = 1) -> str:
        """Compress text to specified SHL tier."""
        pass
    
    def expand(self, shl: str) -> str:
        """Expand SHL back to full text."""
        pass
    
    def round_trip_test(self, text: str) -> float:
        """Test compression/expansion accuracy."""
        compressed = self.compress(text)
        expanded = self.expand(compressed)
        return similarity(text, expanded)
```

Questions:
1. Will round_trip_test catch ALL semantic loss? Give 3 examples where it fails.
2. How to handle proper nouns? Code? Mathematical notation?
3. Is dynamic tier selection (based on accuracy threshold) sufficient?

Agent 2 (Performance Analyst):
Test these specific cases - will SHL preserve meaning?
```
Case 1: "The patient has cancer" → Tier 2 → "pt→cancer"
  - Problem: Loses "has" (critical medical info)
  
Case 2: "if (x == 0)" → Tier 1 → "if x==0"  
  - Problem: Loses spacing (breaks some parsers)
  
Case 3: "Dr. Smith" → Tier 1 → "dr smith"
  - Problem: Loses capitalization (proper noun now generic)
```

What percentage of real-world text will have issues like these?

Agent 3 (Research Validator):
SHL has NO peer-reviewed paper. Search academic literature:
- Are there similar compression techniques?
- What do those papers say about semantic preservation?
- What accuracy rates do they achieve?

Agent 4 (Error Detective):
Find 5 edge cases where SHL will FAIL BADLY.
Provide specific examples and explain why they break.

DELIVERABLE:
```
SHL TECHNICAL ANALYSIS:

Architecture Issues:
  [List specific problems]

Performance Concerns:
  [Expected failure rate: X%]
  [Examples of failures]

Research Gaps:
  [Similar techniques found]
  [Comparison to SHL]

Edge Cases (5 examples):
  1. [Case] → [Why it fails] → [Severity: HIGH/MED/LOW]
  2. ...

VERDICT:
  - Can SHL achieve claimed compression? YES/NO/MAYBE
  - Will accuracy stay >95%? YES/NO/MAYBE
  - Recommended action: [PROCEED/REVISE/STOP]
  - If REVISE: [specific fixes needed]
```

BEGIN ANALYSIS.
```

---

## PROMPT 3: RESEARCH PAPER VALIDATION

```
Now validate the research papers cited in the optimization layer.

YOUR TASK: Verify these 4 key papers that the system depends on.

PAPER 1: HCP (Hierarchical Context Pruning) - Zhang et al. 2024
CLAIMED: "60-80% token reduction, <2% accuracy loss"

Agent 3 (Research Validator) - Primary lead on this:
1. Does this paper actually exist? (Search arXiv, Google Scholar)
2. If yes: Do the results match what's claimed?
3. If yes: Does the methodology transfer to multi-agent code generation?
4. If yes: What are the limitations mentioned in the paper?

PAPER 2: HOMER (Hierarchical Context Merging) - Song et al. 2024 (ICLR)
CLAIMED: "80.4% accuracy on 32K context vs 22.4% baseline, training-free"

Questions:
1. Verify this paper exists at ICLR 2024
2. Are those numbers accurate?
3. CRITICAL: Does it work on small models (1.3B-3B parameters)?
4. What's the memory overhead?

PAPER 3: HiQA - Chen et al. 2024 (KDD)
CLAIMED: "15-20% accuracy gain from metadata augmentation"

Questions:
1. Verify existence at KDD 2024
2. Is this for multi-document QA only, or generalizable?
3. What's the token overhead of metadata?
4. Does it work for code (not just documents)?

PAPER 4: MemGPT - Packer et al. 2023 (arXiv 2310.08560)
CLAIMED: "Multi-day conversation coherence, OS-inspired virtual memory"

Questions:
1. Verify paper and citation
2. Has this been tested at production scale?
3. What's the latency impact?
4. Are there better alternatives published since 2023?

DELIVERABLE:
```
RESEARCH VALIDATION REPORT:

PAPER 1 (HCP):
  ✓/✗ Exists: [YES/NO]
  ✓/✗ Claims accurate: [YES/NO/PARTIAL]
  ✓/✗ Transfers to our use case: [YES/NO/UNCERTAIN]
  Limitations: [list]
  Grade: [0-10]

[Repeat for all 4 papers]

OVERALL RESEARCH VALIDITY:
  - How many papers fully support claims? X/4
  - How many have limitations that affect us? X/4
  - Are there contradicting papers we should know about?
  - Research confidence score: X/100

RECOMMENDATIONS:
  [Any papers that need to be replaced/supplemented]
  [Better alternatives found in literature]
  [Research gaps we need to address]
```

BEGIN VALIDATION.
```

---

## PROMPT 4: IMPLEMENTATION REALITY CHECK

```
Now assess if the proposed 10-week timeline is realistic.

PROPOSED PLAN:
- Week 1-2: HCP + HiQA (foundation)
- Week 3-4: HOMER (merging)
- Week 5-6: SHL Tier 1 (compression)
- Week 7-8: MemGPT (memory management)
- Week 9-10: Production hardening

Agent 5 (Implementation Engineer) - Lead this analysis:

QUESTION 1: What's underestimated?
Break down ACTUAL implementation complexity for each phase:
```
Phase 1 (HCP + HiQA):
  - AST parsing for multiple languages: ? hours
  - Topology preservation algorithm: ? hours
  - Metadata augmentation system: ? hours
  - Integration with existing system: ? hours
  - Testing across all edge cases: ? hours
  REALISTIC TIMELINE: ? weeks (not 2)
```

Do this for ALL 5 phases. Be brutally honest.

QUESTION 2: Hidden dependencies?
- Does Phase 3 actually depend on Phase 2 completing perfectly?
- Can we parallelize anything?
- What if one phase fails - does it cascade?

QUESTION 3: Resource requirements?
- How many engineers needed? (don't say "1-2", be specific)
- GPU compute hours for testing?
- Storage for experiment tracking?
- Time for debugging and iteration?

Agent 6 (Cost Analyst):
What's the REAL cost of this 10-week build?
```
Engineering time:
  X engineers × $Y/hour × Z hours = $___

Infrastructure:
  GPUs for testing: $___/month × 2.5 months = $___
  Storage: $___
  APIs during development: $___
  Observability tools: $___
  
Hidden costs:
  Bug fixing time: $___
  Iteration cycles: $___
  Documentation: $___
  Team coordination: $___
  
TOTAL REAL COST: $___
```

DELIVERABLE:
```
IMPLEMENTATION REALITY CHECK:

REVISED TIMELINE:
  Phase 1: [X weeks] (not 2)
  Phase 2: [X weeks] (not 2)
  Phase 3: [X weeks] (not 2)
  Phase 4: [X weeks] (not 2)
  Phase 5: [X weeks] (not 2)
  TOTAL: [X weeks] (not 10)

RESOURCE REQUIREMENTS:
  Engineers: [X full-time]
  Budget: $[X]
  Infrastructure: [specific needs]

RISK FACTORS:
  1. [Risk] - Probability: [%] - Impact: [HIGH/MED/LOW]
  2. ...

VERDICT:
  - Is 10 weeks realistic? YES/NO
  - If NO: What's realistic? [X weeks]
  - What's the critical path? [Phase X → Phase Y]
  - Can we parallelize? [How?]
```

BE BRUTALLY HONEST. We want reality, not optimism.

BEGIN ANALYSIS.
```

---

## PROMPT 5: FINAL SYNTHESIS & GRADE

```
Now synthesize all findings from your 6 agents across all previous prompts.

PROJECT MANAGER (you) - Final Report:

SECTION 1: CRITICAL ISSUES FOUND
List every HIGH severity issue discovered:
```
ISSUE 1:
  Component: [SHL/HCP/HOMER/etc]
  Problem: [specific description]
  Evidence: [from which agent/analysis]
  Impact: [what breaks if not fixed]
  Severity: HIGH
  Proposed Fix: [concrete solution]
  Confidence in fix: [%]

[Repeat for all HIGH severity issues]
```

SECTION 2: PERFORMANCE CLAIMS VALIDATION
For each bold claim, validate:
```
CLAIM: "5-10x context extension"
  Agent analysis: [summary]
  Evidence: [research papers, calculations]
  Verdict: VALIDATED / QUESTIONABLE / FALSE
  Actual expectation: [realistic number]
  Confidence: [%]

CLAIM: ">95% accuracy maintained"
  Agent analysis: [summary]
  Evidence: [edge cases, testing]
  Verdict: VALIDATED / QUESTIONABLE / FALSE
  Actual expectation: [realistic number]
  Confidence: [%]

CLAIM: "60-90% cost reduction"
  Agent analysis: [summary]
  Evidence: [calculations, assumptions]
  Verdict: VALIDATED / QUESTIONABLE / FALSE
  Actual expectation: [realistic number]
  Confidence: [%]
```

SECTION 3: COMPONENT GRADES
Grade each major component (0-10):
```
SHL Design:                    [X]/10
  Justification: [why this score]

HCP Implementation:            [X]/10
  Justification: [why this score]

HOMER Integration:             [X]/10
  Justification: [why this score]

MemGPT Memory Management:      [X]/10
  Justification: [why this score]

Multi-Model Coordination:      [X]/10
  Justification: [why this score]

Testing Strategy:              [X]/10
  Justification: [why this score]

Timeline & Resources:          [X]/10
  Justification: [why this score]

Overall System Design:         [X]/10
  Justification: [why this score]
```

SECTION 4: FINAL RECOMMENDATION
```
OVERALL SCORE: [X]/100

PASS/FAIL: [PASS if ≥80, FAIL if <80]

RECOMMENDATION:
  ⚪ PROCEED AS-IS (if score ≥90)
  ⚪ PROCEED WITH REVISIONS (if 80-89)
  ⚪ MAJOR REVISION REQUIRED (if 70-79)
  ⚪ RETHINK APPROACH (if <70)

TOP 3 MUST-FIX ISSUES (if not PASS):
  1. [Issue] - [How to fix]
  2. [Issue] - [How to fix]
  3. [Issue] - [How to fix]

ALTERNATIVE APPROACHES (if any):
  [If you'd design this differently, explain how]
  [Trade-offs vs current approach]

CONFIDENCE IN ASSESSMENT: [%]
```

SECTION 5: AGENT DEBATE HIGHLIGHTS
What did your agents disagree about?
```
DEBATE 1: [Topic]
  Agent A position: [summary]
  Agent B position: [summary]
  Resolution: [how consensus reached]
  Minority opinion: [if important]

[List major debates]
```

This is your FINAL REPORT. Be comprehensive and honest.

BEGIN SYNTHESIS.
```

---

## DONE! 

Run these 5 prompts in sequence. Copy the full response for each before moving to the next.

When complete, bring all 5 responses back and I'll synthesize with ChatGPT's findings.
