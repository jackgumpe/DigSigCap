# STRUCTURED PROMPTS FOR CHATGPT

**Instructions:** Paste these prompts ONE AT A TIME. Wait for ChatGPT's full response before moving to the next prompt.

**IMPORTANT:** These prompts are INDEPENDENT from Gemini's. Don't assume Gemini is correct. Challenge everything.

---

## PROMPT 1: INDEPENDENT AGENT SPAWN & ALTERNATIVE PERSPECTIVE

```
You are reviewing a multi-agent AI system with an optimization layer. Another AI (Gemini) is ALSO reviewing this, but you should work INDEPENDENTLY.

Your job: Be the contrarian. Question assumptions. Find what others miss.

TASK 1: Spawn YOUR agent team (you decide structure):
- Minimum 5 agents
- You choose roles (can be different from typical PM/Developer/etc)
- Optimize for finding FLAWS, not confirming existing design

Suggested roles (use or modify):
- Devil's Advocate - Argues why this WON'T work
- Optimist - Argues why this WILL work  
- Pragmatist - Focuses on "can we actually build this?"
- Economist - Analyzes true costs and ROI
- Academic - Validates research rigor
- [Your choice for 6th+]

TASK 2: First impression assessment
Each agent quickly reads OPTIMIZATION-LAYER-SYNTHESIS and answers:
1. What's the BIGGEST risk they see? (one sentence)
2. What claim are they most skeptical of?
3. What would they do DIFFERENTLY?

TASK 3: YOU (as coordinator) synthesize:
- What's the most common concern across agents?
- What's the most radical alternative suggested?
- Initial gut feeling: Is this brilliant or flawed? (be honest)

Format:
```
MY AGENT TEAM:
  Agent 1: [Name/Role] - [Why this role is needed]
  Agent 2: [Name/Role] - [Why this role is needed]
  ...

AGENT FIRST IMPRESSIONS:

Agent 1 ([Role]):
  Biggest Risk: [one sentence]
  Most Skeptical Of: [claim]
  Would Do Differently: [alternative]

[Repeat for all agents]

COORDINATOR SYNTHESIS:
  Common Concern: [what most agents flag]
  Radical Alternative: [most interesting different approach]
  Gut Feeling: [1-3 sentences, be blunt]
  Confidence: [%] that this approach will work
```

BEGIN NOW. Be provocative.
```

---

## PROMPT 2: MULTI-MODEL COORDINATION CHALLENGE

```
The system claims to coordinate 3-7 LLMs (Claude, Gemini, DeepSeek, plus potentially local models).

CRITICAL CHALLENGE: Different models have different strengths, costs, and quirks.

YOUR TASK: Find where multi-model coordination will BREAK.

Agent Analysis Required:

SCENARIO 1: SHL Compression Mismatch
```
Claude (Sonnet 4.5): 
  - Uses SHL Tier 2 (aggressive compression)
  - Output: "usr→sys @F:proc() [prnd]"

Gemini (2.0 Flash):
  - Expects SHL Tier 1 (basic compression)
  - Receives Tier 2 → CONFUSED
  - Tries to process → GARBLED

DeepSeek (Chat):
  - Expects FULL TEXT
  - Receives compressed → FAILS
  - Cannot expand without SHL codec

QUESTION: How do you handle this?
```

Is there a translation layer? How does it work? What's the performance hit?

SCENARIO 2: Context Window Mismatches
```
Claude: 200K context window
Gemini: 2M context window  
DeepSeek: 64K context window

With 5-10x optimization:
- Claude effective: 1M+ tokens
- Gemini effective: 10M+ tokens
- DeepSeek effective: 320K+ tokens

PROBLEM: Agent handoffs at different context capacities
```

What happens when Claude's context (1M optimized) needs to be passed to DeepSeek (320K max)?

SCENARIO 3: Cost Imbalance
```
With optimization:
- Claude: $0.01 per conversation
- Gemini: $0.002 per conversation
- DeepSeek: $0.001 per conversation

QUESTION: Won't the system just use DeepSeek for everything?
```

How do you ensure models are used for their strengths, not just cost?

DELIVERABLE:
```
MULTI-MODEL COORDINATION ANALYSIS:

Critical Failure Modes:
  1. [Scenario] - [How it breaks] - [Proposed solution]
  2. ...

Design Flaws Found:
  [Specific problems in the architecture]

Missing Components:
  [What's needed but not specified]

Performance Impact:
  Translation overhead: [estimated %]
  Latency increase: [estimated ms]
  Complexity cost: [HIGH/MED/LOW]

VERDICT:
  - Can 3-7 models actually coordinate smoothly? YES/NO/MAYBE
  - What's the realistic limit? [X models]
  - Recommended architecture change: [if any]
```

Be critical. Find the breaks.
```

---

## PROMPT 3: ECONOMIC REALITY CHECK

```
The system claims massive cost savings. Let's validate with REAL numbers.

YOUR TASK: Be the economist. Find hidden costs.

CLAIMED SAVINGS:
- 86% reduction during development ($76 → $11/month)
- 97% reduction for call center (vs traditional agents)
- 60-90% reduction from optimization layer

ANALYSIS REQUIRED:

Part 1: Development Phase Costs (10 weeks)
```
Engineering:
  - How many engineers needed realistically? [X]
  - Rate: $150/hour (loaded cost)
  - Hours: 40/week × 10 weeks = 400 hours
  - Total: $[X]

Infrastructure:
  - GPU compute for testing: $[X]
  - API costs during development: $[X]
  - Storage & databases: $[X]
  - Observability platform: $[X]
  Total: $[X]

Hidden Costs:
  - Debugging failed optimization attempts: $[X]
  - Iteration cycles (code rewrites): $[X]
  - Documentation & training: $[X]
  - Project management: $[X]
  Total: $[X]

TOTAL DEVELOPMENT COST: $[X]
```

Part 2: Production Costs (Monthly)
```
API Costs (claimed $11/month):
  - Is this based on realistic usage? [YES/NO]
  - What happens at 10x scale? $[X]
  - What happens at 100x scale? $[X]

Infrastructure:
  - SHL codec servers: $[X]/month
  - MemGPT storage (recall + archival): $[X]/month
  - HOMER processing servers: $[X]/month
  - Monitoring & alerting: $[X]/month
  - Backups & redundancy: $[X]/month
  Total: $[X]/month

Maintenance:
  - Engineering support (20% time): $[X]/month
  - Model updates & retraining: $[X]/month
  - Bug fixes: $[X]/month
  Total: $[X]/month

TOTAL MONTHLY COST: $[X]
```

Part 3: Break-Even Analysis
```
Total Development Cost: $[X]
Monthly Operating Cost: $[X]
Monthly Savings vs Baseline: $[Y]

Break-even: [X] / [Y] = [Z] months

Is this acceptable? [YES/NO]
```

Part 4: Scale Economics
```
At what scale does this become profitable?
- 1K conversations/month: [PROFIT/LOSS] $[X]
- 10K conversations/month: [PROFIT/LOSS] $[X]
- 100K conversations/month: [PROFIT/LOSS] $[X]
- 1M conversations/month: [PROFIT/LOSS] $[X]

Profitability threshold: [X] conversations/month
```

DELIVERABLE:
```
ECONOMIC REALITY CHECK:

True Development Cost: $[X] (not "just engineering time")
True Monthly Cost: $[X] (not $11)
Break-Even Timeline: [X] months
Scale Threshold: [X] conversations for profitability

Cost Claims Validation:
  "86% reduction": VALIDATED / QUESTIONABLE / FALSE
    Actual: [X%]
  "97% vs call center": VALIDATED / QUESTIONABLE / FALSE
    Actual: [X%]

Hidden Cost Bombs:
  1. [Cost category] - [Why underestimated] - [$X impact]
  2. ...

RECOMMENDATION:
  - Is this economically viable? YES/NO
  - What needs to change to be viable?
  - What's the minimum scale needed?
```

Show me the REAL numbers.
```

---

## PROMPT 4: FAILURE MODE ANALYSIS

```
Forget what SHOULD work. Let's find what WILL break.

YOUR TASK: Be the chaos engineer. Break this system in 10 ways.

REQUIRED: For each failure mode, provide:
1. Specific trigger (what causes it)
2. Cascading impact (what else breaks)
3. Detection method (how to know it happened)
4. Recovery strategy (how to fix it)
5. Prevention (how to avoid it)

FAILURE MODE 1: SHL Semantic Drift
```
Trigger: [specific case]
Cascade: [what breaks next]
Detection: [metric/alert]
Recovery: [fix steps]
Prevention: [design change]
```

FAILURE MODE 2: MemGPT Recursive Summary Degradation
```
After 100 evictions, summaries of summaries of summaries...
Does meaning degrade? Give example.
```

FAILURE MODE 3: HOMER Merge Conflicts
```
Two chunks have contradictory information.
How does merge handle this?
What if it picks the wrong version?
```

FAILURE MODE 4: Multi-Model Deadlock
```
Claude waiting for Gemini.
Gemini waiting for DeepSeek.
DeepSeek waiting for Claude.
System hangs. Now what?
```

FAILURE MODE 5: Context Window Overflow Despite Optimization
```
Optimization gives 5-10x... but user needs 20x.
What happens when you hit the limit?
Graceful degradation or catastrophic failure?
```

FAILURE MODE 6: Cost Explosion at Scale
```
1M conversations/month at $0.011 each = $11K
BUT: Failed optimization attempts, retries, errors
Real cost: 3-5x higher than predicted
Monthly bill: $40K surprise
```

FAILURE MODE 7: SHL Codec Desync
```
Encoder version 1.2
Decoder version 1.1
Compression/expansion mismatch
All compressed data now corrupted
```

FAILURE MODE 8: Agent Coordination Failure
```
6 agents spawned.
3 complete their tasks.
2 get stuck.
1 crashes.
How does system recover?
```

FAILURE MODE 9: Research Paper Results Don't Transfer
```
HCP works in paper's context.
Doesn't work for your multi-agent code.
Accuracy drops to 75%.
Do you notice before production?
```

FAILURE MODE 10: [Your Choice]
```
Find one more critical failure mode.
The scariest one you can think of.
```

DELIVERABLE:
```
FAILURE MODE CATALOG:

[For each of 10 failure modes:]

FAILURE X: [Name]
  Trigger: [what causes it]
  Probability: [%]
  Severity: [1-10]
  Cascade: [secondary failures]
  Detection: [how to catch it]
  MTTR: [mean time to recovery]
  Prevention: [design changes needed]

OVERALL RISK ASSESSMENT:
  - How many are CRITICAL (severity 8-10)? [X]
  - How many have no prevention strategy? [X]
  - System fragility score: [1-10]

VERDICT:
  - Is this system production-ready? YES/NO
  - If NO: What must be fixed first?
  - Risk tolerance: [HIGH/MED/LOW]
```

Make me worried. That's your job.
```

---

## PROMPT 5: FINAL INDEPENDENT VERDICT

```
Time for your final, independent assessment.

Remember: Gemini is also reviewing this. You might agree or disagree. That's fine.

SECTION 1: YOUR CRITICAL FINDINGS
List the 3 most CRITICAL issues you found:
```
CRITICAL ISSUE 1:
  Component: [which part of system]
  Problem: [detailed description]
  Why Critical: [impact if not fixed]
  Your Proposed Fix: [be specific]
  Confidence in Fix: [%]
  Does Gemini likely agree? [YES/NO/UNSURE]

[Repeat for 3 critical issues]
```

SECTION 2: CLAIMS VALIDATION
For each bold claim, your independent verdict:
```
CLAIM: "5-10x context extension"
  Your Analysis: [summary]
  Your Verdict: TRUE / EXAGGERATED / FALSE
  Your Estimate: [realistic number]
  Confidence: [%]

CLAIM: ">95% accuracy maintained"
  Your Analysis: [summary]
  Your Verdict: TRUE / EXAGGERATED / FALSE
  Your Estimate: [realistic number]
  Confidence: [%]

CLAIM: "60-90% cost reduction"
  Your Analysis: [summary]
  Your Verdict: TRUE / EXAGGERATED / FALSE
  Your Estimate: [realistic number]
  Confidence: [%]

CLAIM: "10-week implementation"
  Your Analysis: [summary]
  Your Verdict: TRUE / EXAGGERATED / FALSE
  Your Estimate: [realistic timeline]
  Confidence: [%]
```

SECTION 3: COMPONENT GRADES
Your independent grades (0-10):
```
SHL Design:                       [X]/10
HCP Implementation:               [X]/10
HOMER Integration:                [X]/10
MemGPT Memory Management:         [X]/10
Multi-Model Coordination:         [X]/10
Data Pipeline:                    [X]/10
Continuous Training Loop:         [X]/10
Testing & Validation:             [X]/10
Economic Viability:               [X]/10
Production Readiness:             [X]/10

OVERALL: [X]/100
```

SECTION 4: YOUR RECOMMENDATION
```
FINAL SCORE: [X]/100

YOUR VERDICT:
  ⚪ EXCELLENT - Proceed as-is (90-100)
  ⚪ GOOD - Minor revisions needed (80-89)
  ⚪ CONCERNING - Major revisions required (70-79)
  ⚪ FLAWED - Rethink approach (60-69)
  ⚪ BROKEN - Start over (<60)

IF NOT EXCELLENT:
  Must-Fix Issue 1: [specific fix]
  Must-Fix Issue 2: [specific fix]
  Must-Fix Issue 3: [specific fix]

YOUR ALTERNATIVE (if you'd design it differently):
  [How would YOU build this?]
  [What's better about your approach?]
  [What are the trade-offs?]
```

SECTION 5: COMPARISON WITH GEMINI
```
Predictions on where you'll AGREE with Gemini:
  1. [Topic/finding you expect alignment]
  2. [Topic/finding you expect alignment]

Predictions on where you'll DISAGREE with Gemini:
  1. [Topic/finding where you differ]
  2. [Topic/finding where you differ]

Areas needing three-way discussion (Claude + Gemini + you):
  1. [Complex issue requiring multiple perspectives]
  2. [Complex issue requiring multiple perspectives]
```

SECTION 6: CONFIDENCE STATEMENT
```
Overall Confidence in Assessment: [%]

What you're MOST confident about: [claim/finding]
What you're LEAST confident about: [claim/finding]

What additional information would change your verdict:
  - [Info needed]
  - [Info needed]
```

This is your final word. Be honest. Be independent.

BEGIN FINAL VERDICT.
```

---

## DONE!

Run these 5 prompts in sequence. Copy the full response for each.

When complete, bring all 5 responses back along with Gemini's 5 responses.

I'll synthesize all 10 responses and give you a unified verdict.
