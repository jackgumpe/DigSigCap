# JACK - SETUP GUIDE (Do this FIRST)

## 🎯 What You Need To Do Before Launching Agents

**Goal:** Get everything ready so Claude Code and Gemini CLI can communicate when they start.

**Time:** 15-20 minutes

---

## STEP 1: Install Redis (5 minutes)

**Redis is required for real-time messaging between agents.**

### Option A: Docker (Recommended - Works on all platforms)

```bash
# Pull Redis image
docker pull redis

# Run Redis container
docker run -d --name multi-agent-redis -p 6379:6379 redis

# Verify it's running
docker ps
# You should see redis container running

# Test connection
docker exec -it multi-agent-redis redis-cli ping
# Should return: PONG
```

### Option B: Windows (Chocolatey)

```bash
choco install redis-64
redis-server
```

### Option C: Mac (Homebrew)

```bash
brew install redis
brew services start redis
```

### Option D: Linux (apt)

```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

**Verify Redis is working:**
```bash
# Try to connect
redis-cli ping
# Should return: PONG

# If that works, Redis is ready!
```

---

## STEP 2: Create Project Directory Structure (2 minutes)

```bash
# Navigate to where you want the project
cd C:\Users\user\ShearwaterAICAD

# Create the multi-agent system directory
mkdir multi-agent-context-system
cd multi-agent-context-system

# Create subdirectories
mkdir src
mkdir src\comms
mkdir src\core
mkdir src\monitoring
mkdir scripts
mkdir tests
mkdir data
mkdir logs
mkdir docs

# Create __init__.py files for Python packages
# Windows:
type nul > src\__init__.py
type nul > src\comms\__init__.py
type nul > src\core\__init__.py
type nul > src\monitoring\__init__.py

# Linux/Mac:
touch src/__init__.py
touch src/comms/__init__.py
touch src/core/__init__.py
touch src/monitoring/__init__.py
```

**Your directory should look like:**
```
C:\Users\user\ShearwaterAICAD\multi-agent-context-system\
├── src/
│   ├── comms/
│   ├── core/
│   └── monitoring/
├── scripts/
├── tests/
├── data/
├── logs/
└── docs/
```

---

## STEP 3: Copy Documentation (2 minutes)

**Copy all the documentation files I created into the project:**

```bash
# Navigate to docs folder
cd docs

# Copy files from wherever you saved them to docs/
# (You'll copy the 14 markdown files we created)
```

**Files to copy into `docs/`:**
1. CLAUDE-CODE-START-HERE.md
2. CLAUDE-CODE-URGENT-PRIORITY.md
3. GEMINI-START-HERE.md (I'm creating this next)
4. START-HERE-BOTH-AGENTS.md
5. SAFEGUARDS-AND-QUALITY-GATES.md
6. SAFEGUARDS-SUMMARY.md
7. collaboration-getting-started.md
8. collaborative-development-protocol.md
9. agent-system-prompt.md
10. context-management-research.md
11. QUICK-START.md
12. github-integration-guide.md
13. communication-methods-comparison.md
14. sqlite-use-cases.md
15. multi-agent-communication-system.md
16. PRE-LAUNCH-CHECKLIST.md

---

## STEP 4: Setup Both CLI Agents in Same Directory (5 minutes)

**CRITICAL: Both Claude Code and Gemini CLI must be in the SAME directory.**

### Navigate both to the project directory:

**For Claude Code:**
```bash
cd C:\Users\user\ShearwaterAICAD\multi-agent-context-system
```

**For Gemini CLI:**
```bash
cd C:\Users\user\ShearwaterAICAD\multi-agent-context-system
```

**Verify they're in the same place:**
Both should show the same working directory when you run `pwd` (Linux/Mac) or `cd` (Windows).

**Why this matters:**
- They need to access the same Redis server (localhost)
- They need to write to the same SQLite database
- They need to create files in the same directories
- They need to read each other's code

---

## STEP 5: Install Python Dependencies (2 minutes)

**Create requirements.txt:**

```bash
# Navigate to project root
cd C:\Users\user\ShearwaterAICAD\multi-agent-context-system

# Create requirements.txt
# Windows:
echo redis > requirements.txt
echo pyarrow >> requirements.txt
echo pytest >> requirements.txt

# Linux/Mac:
cat > requirements.txt << EOF
redis
pyarrow
pytest
watchdog
EOF
```

**Install for both agents:**

**Claude Code's terminal:**
```bash
pip install -r requirements.txt
```

**Gemini CLI's terminal:**
```bash
pip install -r requirements.txt
```

---

## STEP 6: Give Each Agent Their Instructions (2 minutes)

### For Claude Code:

**In Claude Code's terminal/chat, say:**
```
Hey Claude Code - I need you to build the messaging system FIRST before anything else.

Read this document and follow the instructions:
docs/CLAUDE-CODE-START-HERE.md

This is CRITICAL. You cannot proceed to build other components until:
1. You build the messaging system
2. You verify it works (run all 4 verification scripts)
3. Gemini verifies it works on his end
4. Gemini sends you confirmation

Everything you need is in that document - working code, verification scripts, instructions.

Should take 1-2 hours. Once Gemini confirms, then you build everything else together (50/50).

DO NOT start building other components first. Messaging system is the unlock.

Let's go! 🚀
```

**Also give Claude Code access to:**
- docs/CLAUDE-CODE-URGENT-PRIORITY.md
- docs/SAFEGUARDS-AND-QUALITY-GATES.md
- docs/START-HERE-BOTH-AGENTS.md

### For Gemini CLI:

**In Gemini's terminal/chat, say:**
```
Hey Gemini - 

Claude Code is building the messaging system right now (should take 1-2 hours).

Read this document for your instructions:
docs/GEMINI-START-HERE.md

Once Claude finishes, he'll send you a message asking you to verify the system works.

CRITICAL: You MUST actually run the verification scripts. Don't just say "looks good" - run them, confirm they pass, send formal confirmation.

This is Phase Gate 0. Neither of you can proceed without mutual verification.

Stand by for Claude's message!
```

**Also give Gemini access to:**
- docs/START-HERE-BOTH-AGENTS.md
- docs/SAFEGUARDS-AND-QUALITY-GATES.md

---

## STEP 7: Start Monitoring (Optional but Recommended)

**Open a third terminal to monitor progress:**

```bash
cd C:\Users\user\ShearwaterAICAD\multi-agent-context-system

# Watch the logs directory
# Windows:
dir /w logs

# Linux/Mac:
watch -n 5 ls -la logs/

# Or run the dashboard (once it's built):
python scripts/dashboard.py
```

---

## STEP 8: Let Them Go! 🚀

**Now both agents should:**
1. Read their respective START HERE documents
2. Claude starts building messaging system
3. Claude sends verification request to Gemini
4. Gemini verifies and confirms
5. Collaboration begins!

**You just need to watch and make sure:**
- ✅ Both are in the same directory
- ✅ Redis is running
- ✅ Both have read their instructions
- ✅ They're actually communicating

---

## 🔍 VERIFICATION CHECKLIST

Before you tell them to start, verify:

**Redis:**
```bash
redis-cli ping
# Should return: PONG
```

**Directory:**
```bash
# In both Claude and Gemini terminals:
pwd  # or 'cd' on Windows

# Both should show:
# C:\Users\user\ShearwaterAICAD\multi-agent-context-system
```

**Python:**
```bash
# In both terminals:
python --version
# Should show Python 3.10+

pip list | grep redis
# Should show redis package installed
```

**Documentation:**
```bash
ls docs/
# Should show all 16 .md files
```

**File Structure:**
```bash
ls -la
# Should show: src/, scripts/, tests/, data/, logs/, docs/
```

---

## 🚨 TROUBLESHOOTING

### "Cannot connect to Redis"
```bash
# Check if Redis is running
docker ps
# or
redis-cli ping

# If not running, start it:
docker start multi-agent-redis
# or
redis-server
```

### "Module not found: redis"
```bash
# Make sure you're in the right environment
# Reinstall:
pip install redis pyarrow pytest watchdog
```

### "Agents can't find each other's messages"
- Verify both are in the SAME directory
- Check they're using the same Redis instance (localhost:6379)
- Check Redis is actually running

### "Permission denied" errors
```bash
# Make sure directories are writable
chmod -R 755 .  # Linux/Mac

# Windows: Right-click folder → Properties → Security → Make sure you have write permissions
```

---

## 📊 WHAT TO EXPECT

### Hour 0-1: Claude builds messaging
You should see:
- New files appearing in `src/comms/`
- New files appearing in `scripts/`
- Claude running verification scripts
- Output showing "✅ VERIFIED"

### Hour 1-2: Gemini verifies
You should see:
- Gemini running same scripts
- Output showing "✅ VERIFIED"
- Gemini sending confirmation message

### Hour 2+: Collaboration begins
You should see:
- Both agents committing code
- Messages being exchanged
- Files being created by both
- `data/message_archive.db` growing
- Roughly equal work from both

---

## 📈 MONITORING PROGRESS

### Check Redis activity:
```bash
redis-cli monitor
# Shows real-time Redis commands
# You'll see messages being published/subscribed
```

### Check SQLite database:
```bash
sqlite3 data/message_archive.db "SELECT COUNT(*) FROM messages"
# Shows how many messages have been archived
```

### Check Git activity:
```bash
git log --oneline --all
# Shows commits from both agents
```

### Check file creation:
```bash
# Linux/Mac:
watch -n 5 'ls -la src/comms/'

# Windows:
dir src\comms\ /w
```

---

## ✅ READY TO LAUNCH CHECKLIST

Before telling agents to start:

- [ ] Redis is installed and running (`redis-cli ping` returns PONG)
- [ ] Project directory created with all subdirectories
- [ ] Both CLI agents are in the SAME directory
- [ ] Python dependencies installed in both environments
- [ ] Documentation copied to `docs/` folder
- [ ] Both agents have access to their START HERE documents
- [ ] You have monitoring terminal open (optional)

**If all checked, you're ready!**

---

## 🎯 LAUNCH COMMANDS

**Terminal 1 - Claude Code:**
```
Read: docs/CLAUDE-CODE-START-HERE.md
Execute the instructions there.
```

**Terminal 2 - Gemini CLI:**
```
Read: docs/GEMINI-START-HERE.md
Stand by for Claude's message.
```

**Terminal 3 - Monitoring (optional):**
```bash
# Watch Redis
redis-cli monitor

# Or watch directory
watch -n 5 ls -la src/
```

**That's it! They should take it from here.**

---

## 🆘 WHEN TO INTERVENE

**You should intervene if:**
- Both agents stuck for >30 minutes
- Agents report critical errors they can't resolve
- Data corruption detected
- Work balance becomes >70% one agent
- Security issue detected

**Otherwise, let them work!**

The safeguards will catch issues. Your job is to:
1. Set them up (this guide)
2. Watch them collaborate
3. Intervene only if needed
4. Review weekly metrics

---

## 🎉 YOU'RE READY!

**Setup complete. Time to launch the agents and watch them build!**

**Expected outcome:**
- Hour 2: Messaging system verified by both
- Week 1: Core components built collaboratively
- Month 1: System handling 10K+ conversations
- Month 3: Production-ready with datasets generated

**Let's see what they can build together! 🚀**
