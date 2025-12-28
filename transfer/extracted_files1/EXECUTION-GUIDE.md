# MULTI-MODEL CRITIQUE - EXECUTION GUIDE

**Created:** 2024-12-11  
**For:** Jack  
**Purpose:** Run structured prompts through Gemini and ChatGPT, collect responses for synthesis

---

## 🎯 WHAT YOU'VE GOT

**Two files of structured prompts:**

1. **GEMINI-STRUCTURED-PROMPTS.md**
   - 5 prompts focusing on: Architecture, Performance, Integration, Research, Errors
   - Forces Gemini to spawn 6 specialized agents
   - Technical deep dives with specific scenarios
   - ~40 minutes total

2. **CHATGPT-STRUCTURED-PROMPTS.md**
   - 5 prompts focusing on: Research validation, Cost analysis, Timeline reality, Alternatives
   - Forces ChatGPT to spawn 5 specialized agents (different roles)
   - More skeptical, cost-focused, proposes alternatives
   - ~40 minutes total

**Why both?**
- Different perspectives = better coverage
- Catch errors the other misses
- Independent validation
- Compare findings for synthesis

---

## 🚀 STEP-BY-STEP EXECUTION

### **OPTION A: Sequential (Recommended)**

**Safer, easier to track, can pause between models**

1. **Open Gemini in browser**
   - Go to gemini.google.com
   - Start new chat

2. **Run Gemini prompts** (one at a time)
   - Open GEMINI-STRUCTURED-PROMPTS.md
   - Copy PROMPT 1 (entire text between markers)
   - Paste into Gemini
   - Wait for full response (could be 5-10 min)
   - Save response (copy to notepad or text file)
   - Repeat for PROMPT 2, 3, 4, 5

3. **Open ChatGPT in browser**
   - Go to chat.openai.com
   - Start new chat

4. **Run ChatGPT prompts** (one at a time)
   - Open CHATGPT-STRUCTURED-PROMPTS.md
   - Copy PROMPT 1
   - Paste into ChatGPT
   - Wait for full response
   - Save response
   - Repeat for PROMPT 2, 3, 4, 5

5. **Bring results back to Claude**
   - Paste all Gemini responses in one message
   - Paste all ChatGPT responses in another message
   - Claude will synthesize

**Total time: ~90 minutes (Gemini: 40 min, ChatGPT: 40 min, breaks: 10 min)**

---

### **OPTION B: Parallel (Faster)**

**More complex, need to juggle two chats at once**

1. **Open both**
   - Gemini in one browser tab
   - ChatGPT in another browser tab

2. **Start both at same time**
   - Paste PROMPT 1 to Gemini
   - Immediately paste PROMPT 1 to ChatGPT
   - Wait for both to respond

3. **Continue in parallel**
   - As soon as each finishes, paste next prompt
   - Save responses as you go

4. **Collect and return**
   - Once both complete all 5 prompts
   - Bring all results back to Claude

**Total time: ~50 minutes (models run in parallel)**

---

## 📝 RESPONSE COLLECTION TIPS

**Best practice:**

1. **Create two text files:**
   - `gemini_responses.txt`
   - `chatgpt_responses.txt`

2. **For each prompt response:**
   ```
   ===== PROMPT 1 RESPONSE =====
   [paste full response here]
   
   ===== PROMPT 2 RESPONSE =====
   [paste full response here]
   
   etc...
   ```

3. **Keep formatting intact**
   - Tables, bullet points, code blocks
   - Makes synthesis easier

4. **Don't edit responses**
   - Even if they seem wrong
   - Claude needs to see raw output

---

## ⚠️ COMMON ISSUES & SOLUTIONS

**Issue 1: Model refuses to spawn agents**
- Solution: Rephrase slightly - "Create 6 specialized analysis perspectives" instead of "spawn agents"

**Issue 2: Response too long, cuts off**
- Solution: Ask "Continue from where you left off"
- Or: "Complete the analysis for Agent X"

**Issue 3: Model goes off-track**
- Solution: Paste prompt again with "Focus specifically on the questions asked"

**Issue 4: Model doesn't use structured format**
- Solution: "Please provide response in the exact format requested: Agent 1 (Role): [details]"

**Issue 5: Rate limits hit**
- Solution: Wait 5-10 minutes between prompts
- Or: Spread across multiple sessions

---

## 🎯 WHAT TO EXPECT

**Gemini will likely:**
- Spawn exactly 6 agents as requested
- Provide technical analysis
- Find architectural issues
- Give moderate grades (75-85/100)
- Recommend modifications

**ChatGPT will likely:**
- Be more skeptical
- Challenge cost assumptions
- Question timeline
- Propose alternatives
- Give harsher grades (65-80/100)

**This is GOOD - we want different perspectives!**

---

## 🔥 AFTER COMPLETION

**Bring results back to Claude with:**

```
Claude, here are the results:

GEMINI RESPONSES:
[paste all 5 prompt responses]

CHATGPT RESPONSES:
[paste all 5 prompt responses]

Please synthesize findings.
```

**Then Claude will:**
1. Compare both analyses
2. Identify agreements and conflicts
3. Validate research claims
4. Grade each model's critique
5. Synthesize unified recommendations
6. Highlight critical issues
7. Provide go/no-go decision

---

## 📊 EXPECTED OUTPUT FROM CLAUDE

**After synthesis, you'll get:**

1. **Error Correction Report**
   - Issues both models found
   - Issues only one found
   - False alarms (non-issues)

2. **Consensus Analysis**
   - Where they agree (high confidence)
   - Where they disagree (needs discussion)
   - Unique insights from each

3. **Grade Reconciliation**
   - Gemini's grades
   - ChatGPT's grades
   - Claude's final grades
   - Justification for differences

4. **Critical Issues List**
   - Showstoppers (must fix)
   - Major concerns (should fix)
   - Minor issues (nice to fix)
   - Non-issues (ignore)

5. **Revised Plan**
   - Updated architecture (if needed)
   - Realistic timeline
   - Cost estimates
   - Risk mitigation
   - Alternative approaches

6. **Final Recommendation**
   - PROCEED / REVISE / RETHINK
   - Confidence level
   - Next steps

---

## 🎉 WHY THIS IS WORTH IT

**Time investment:** ~2 hours  
**Value:**
- Catch critical flaws before 10-week build
- Validate research papers (don't build on bad assumptions)
- Get realistic timeline (not optimistic fantasy)
- Explore alternatives (maybe there's a better way)
- Build confidence (3 AI minds validate approach)

**If this finds even ONE critical flaw, it saves weeks of wasted work.**

---

## 🚀 READY TO GO?

**Checklist:**
- [ ] Gemini tab open
- [ ] ChatGPT tab open
- [ ] GEMINI-STRUCTURED-PROMPTS.md ready
- [ ] CHATGPT-STRUCTURED-PROMPTS.md ready
- [ ] Text files for responses
- [ ] Coffee/energy drink ☕
- [ ] 1-2 hours blocked out

**LET'S DO THIS!**

Start with PROMPT 1 to Gemini. Come back when you have all responses from both models.

---

**Good luck, Jack! 🔥**
