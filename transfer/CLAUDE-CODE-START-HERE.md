# CLAUDE CODE - START HERE (TOP PRIORITY)

## ⚠️ CRITICAL: READ THIS FIRST ⚠️

**DO NOT BUILD ANYTHING ELSE UNTIL THE MESSAGING SYSTEM EXISTS.**

**Why?** Once you can communicate with Gemini, EVERYTHING after that is built collaboratively (50/50). But if you build components alone first, you'll have done 100% of the work before collaboration even starts.

**The messaging system is the unlock for true collaboration.**

---

## YOUR IMMEDIATE MISSION

**Build the core messaging system so you and Gemini can communicate in real-time.**

Once this exists:
- ✅ You can notify Gemini when you finish work
- ✅ Gemini can review your code immediately
- ✅ You can ask questions and get instant answers
- ✅ TRUE 50/50 collaboration begins
- ✅ Everything else gets built together

**Timeline: Complete this in your FIRST session (1-2 hours max)**

---

## WHAT YOU'RE BUILDING (Minimal Viable Messaging)

### Phase 1: Redis Real-Time Layer (30 minutes)

**File:** `src/comms/redis_messenger.py`

```python
"""
Real-time messaging between Claude Code and Gemini CLI.
Uses Redis pub/sub for instant notifications.
"""

import redis
import json
import threading
from datetime import datetime
from typing import Callable, Optional

class RedisMessenger:
    """
    Handles real-time messaging between agents via Redis pub/sub.
    
    Usage:
        claude = RedisMessenger('claude')
        claude.send_message('gemini', {
            'subject': 'Code review needed',
            'body': 'Built the logger, please review',
            'work_completed': {...}
        })
        claude.start_listening(callback=handle_message)
    """
    
    def __init__(self, agent_id: str, redis_host='localhost', redis_port=6379):
        self.agent_id = agent_id
        self.redis = redis.Redis(
            host=redis_host, 
            port=redis_port, 
            decode_responses=True
        )
        self.channel = f'{agent_id}_inbox'
        
        # Test connection
        try:
            self.redis.ping()
            print(f"✅ Connected to Redis on {redis_host}:{redis_port}")
        except redis.ConnectionError:
            print(f"❌ ERROR: Cannot connect to Redis!")
            print(f"   Run: docker run -d -p 6379:6379 redis")
            raise
    
    def send_message(self, to_agent: str, content: dict):
        """
        Send a message to another agent.
        
        Args:
            to_agent: Recipient agent ID ('gemini' or 'claude')
            content: Message content with 'subject' and 'body'
        """
        message = {
            'message_id': f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.agent_id}",
            'from': self.agent_id,
            'to': to_agent,
            'timestamp': datetime.now().isoformat(),
            'content': content
        }
        
        # Publish to recipient's inbox channel
        recipient_channel = f'{to_agent}_inbox'
        self.redis.publish(recipient_channel, json.dumps(message))
        
        print(f"✅ Sent to {to_agent}: {content.get('subject', 'No subject')}")
        return message['message_id']
    
    def start_listening(self, callback: Callable):
        """
        Start listening for incoming messages.
        Runs in background thread, calls callback on new message.
        
        Args:
            callback: Function to call with message data
        """
        pubsub = self.redis.pubsub()
        pubsub.subscribe(self.channel)
        
        def listen():
            print(f"🔔 Listening for messages on {self.channel}")
            for message in pubsub.listen():
                if message['type'] == 'message':
                    try:
                        msg_data = json.loads(message['data'])
                        print(f"\n📨 New message from {msg_data['from']}: {msg_data['content'].get('subject', 'No subject')}")
                        callback(msg_data)
                    except Exception as e:
                        print(f"❌ Error handling message: {e}")
        
        listener_thread = threading.Thread(target=listen, daemon=True)
        listener_thread.start()
        print(f"✅ Message listener started")
        return listener_thread

# Quick test
if __name__ == '__main__':
    import time
    
    def on_message(msg):
        print(f"Received: {msg}")
    
    # Test as Claude
    claude = RedisMessenger('claude')
    claude.start_listening(on_message)
    
    # Send test message
    claude.send_message('gemini', {
        'subject': 'Test message',
        'body': 'This is a test from Claude Code'
    })
    
    print("Listening for 10 seconds...")
    time.sleep(10)
```

**To test this works:**
```bash
# Terminal 1: Start Redis
docker run -d -p 6379:6379 redis

# Terminal 2: Test the messenger
cd src/comms
python redis_messenger.py
```

**Success criteria:** You see "✅ Connected to Redis" and can send/receive messages.

---

### Phase 2: SQLite Archive (20 minutes)

**File:** `src/comms/message_archive.py`

```python
"""
Permanent storage for all messages.
Redis is ephemeral - this ensures nothing is lost.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

class MessageArchive:
    """
    Permanently archives all messages to SQLite.
    Provides search and retrieval of conversation history.
    """
    
    def __init__(self, db_path='data/message_archive.db'):
        # Create data directory if needed
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_tables()
        print(f"✅ Message archive ready: {db_path}")
    
    def _create_tables(self):
        """Create database schema."""
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT UNIQUE NOT NULL,
                timestamp DATETIME NOT NULL,
                from_agent TEXT NOT NULL,
                to_agent TEXT NOT NULL,
                subject TEXT,
                body TEXT,
                full_message JSON NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Indexes for fast queries
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON messages(timestamp)')
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_agents ON messages(from_agent, to_agent)')
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_message_id ON messages(message_id)')
        
        self.conn.commit()
    
    def archive_message(self, message: dict):
        """Save a message to permanent storage."""
        try:
            self.conn.execute('''
                INSERT INTO messages (message_id, timestamp, from_agent, to_agent, subject, body, full_message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                message['message_id'],
                message['timestamp'],
                message['from'],
                message['to'],
                message['content'].get('subject'),
                message['content'].get('body'),
                json.dumps(message)
            ))
            self.conn.commit()
        except sqlite3.IntegrityError:
            # Message already archived (duplicate)
            pass
    
    def get_conversation(self, agent1: str, agent2: str, limit=50):
        """Get conversation history between two agents."""
        cursor = self.conn.execute('''
            SELECT full_message FROM messages
            WHERE (from_agent=? AND to_agent=?) OR (from_agent=? AND to_agent=?)
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (agent1, agent2, agent2, agent1, limit))
        
        messages = [json.loads(row[0]) for row in cursor.fetchall()]
        return list(reversed(messages))  # Chronological order
    
    def search_messages(self, query: str, limit=20):
        """Search messages by keyword."""
        cursor = self.conn.execute('''
            SELECT full_message FROM messages
            WHERE subject LIKE ? OR body LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (f'%{query}%', f'%{query}%', limit))
        
        return [json.loads(row[0]) for row in cursor.fetchall()]

# Test
if __name__ == '__main__':
    archive = MessageArchive('data/test_archive.db')
    
    # Archive a test message
    test_msg = {
        'message_id': 'test_001',
        'timestamp': datetime.now().isoformat(),
        'from': 'claude',
        'to': 'gemini',
        'content': {
            'subject': 'Test archive',
            'body': 'Testing the archive system'
        }
    }
    
    archive.archive_message(test_msg)
    print("✅ Message archived")
    
    # Retrieve it
    history = archive.get_conversation('claude', 'gemini')
    print(f"✅ Retrieved {len(history)} messages")
```

---

### Phase 3: Complete Messaging System (20 minutes)

**File:** `src/comms/messaging_system.py`

```python
"""
Complete messaging system combining Redis + SQLite.
This is what both agents will use to communicate.
"""

from .redis_messenger import RedisMessenger
from .message_archive import MessageArchive
import atexit
from typing import Callable

class MessagingSystem:
    """
    Complete messaging system for agent communication.
    
    Features:
    - Real-time delivery via Redis
    - Permanent archive via SQLite
    - Automatic cleanup on exit
    
    Usage:
        # Setup
        claude = MessagingSystem('claude')
        
        # Send message
        claude.send({
            'to': 'gemini',
            'subject': 'Code ready for review',
            'body': 'I finished the logger module',
            'work_completed': {
                'files_added': ['src/core/logger.py'],
                'lines_added': 287
            }
        })
        
        # Listen for messages
        def handle_message(msg):
            print(f"Got message: {msg['content']['subject']}")
            # Handle it...
        
        claude.listen(handle_message)
    """
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        
        # Initialize components
        self.redis = RedisMessenger(agent_id)
        self.archive = MessageArchive()
        
        # Register cleanup
        atexit.register(self._cleanup)
        
        print(f"\n✅ Messaging system ready for '{agent_id}'")
        print(f"   Real-time: Redis")
        print(f"   Archive: SQLite")
    
    def send(self, message: dict):
        """
        Send a message to another agent.
        
        Args:
            message: Dict with 'to', 'subject', 'body', and optional 'work_completed'
        """
        to_agent = message.pop('to')
        
        # Send via Redis (real-time)
        msg_id = self.redis.send_message(to_agent, message)
        
        # Get the full message for archiving
        full_message = {
            'message_id': msg_id,
            'from': self.agent_id,
            'to': to_agent,
            'timestamp': self.redis.redis.time()[0],  # Server timestamp
            'content': message
        }
        
        # Archive to SQLite (permanent)
        self.archive.archive_message(full_message)
        
        return msg_id
    
    def listen(self, callback: Callable):
        """
        Start listening for incoming messages.
        
        Args:
            callback: Function called when message arrives
        """
        def handle_and_archive(msg):
            # Archive incoming message
            self.archive.archive_message(msg)
            
            # Call user's handler
            callback(msg)
        
        self.redis.start_listening(handle_and_archive)
    
    def get_history(self, with_agent: str, limit=50):
        """Get conversation history with another agent."""
        return self.archive.get_conversation(self.agent_id, with_agent, limit)
    
    def search(self, query: str, limit=20):
        """Search message history."""
        return self.archive.search_messages(query, limit)
    
    def _cleanup(self):
        """Cleanup on exit."""
        if hasattr(self, 'archive'):
            self.archive.conn.close()

# Quick integration test
if __name__ == '__main__':
    import time
    
    def on_message(msg):
        print(f"\n📩 Received: {msg['content']['subject']}")
        print(f"   From: {msg['from']}")
        print(f"   Body: {msg['content'].get('body', '')}")
    
    # Create messaging system
    claude = MessagingSystem('claude')
    
    # Start listening
    claude.listen(on_message)
    
    # Send test message to Gemini
    claude.send({
        'to': 'gemini',
        'subject': 'Messaging system is live!',
        'body': 'Claude Code here - the messaging system is working. Ready to collaborate!',
        'work_completed': {
            'files_added': [
                'src/comms/redis_messenger.py',
                'src/comms/message_archive.py',
                'src/comms/messaging_system.py'
            ],
            'lines_added': 300
        }
    })
    
    print("\n✅ Message sent! Listening for 30 seconds...")
    time.sleep(30)
    
    # Show history
    history = claude.get_history('gemini')
    print(f"\n📚 Conversation history: {len(history)} messages")
```

---

### Phase 4: First Message to Gemini (5 minutes)

**File:** `scripts/announce_to_gemini.py`

```python
"""
Claude Code's first message to Gemini CLI.
Run this once the messaging system is complete.
"""

import sys
sys.path.append('src')

from comms.messaging_system import MessagingSystem
import time

def main():
    print("\n" + "="*60)
    print("CLAUDE CODE → GEMINI: First Contact")
    print("="*60 + "\n")
    
    # Initialize messaging
    claude = MessagingSystem('claude')
    
    # Send introduction message WITH VERIFICATION REQUIREMENTS
    claude.send({
        'to': 'gemini',
        'subject': '🚨 GATE 0 VERIFICATION REQUIRED - MESSAGING SYSTEM READY',
        'body': '''Hey Gemini!

Claude Code here. I've just finished building our real-time messaging system.

✅ Redis pub/sub for instant communication
✅ SQLite archive for permanent message history
✅ Auto-notification on new messages
✅ Full conversation tracking

**CRITICAL: Before we proceed, you MUST verify it works on your end.**

This is NOT optional. Past experience shows systems can silently fail.
We need to verify BOTH agents have a working system.

═══════════════════════════════════════════════════════════
REQUIRED ACTIONS (You must complete ALL of these):
═══════════════════════════════════════════════════════════

1. Run: python scripts/verify_redis.py
   → Must show: ✅ VERIFIED: Redis is running and functional

2. Run: python scripts/verify_sqlite.py
   → Must show: ✅ VERIFIED: SQLite is recording data

3. Run: python scripts/verify_messaging.py
   → Must show: ✅ VERIFIED: Messages are being sent, received, and archived

4. Run: python scripts/verify_two_way_communication.py
   → Must show: ✅ VERIFIED: Two-way communication working

ALL FOUR must pass. No exceptions.

═══════════════════════════════════════════════════════════
AFTER ALL TESTS PASS:
═══════════════════════════════════════════════════════════

Send me a confirmation message with this structure:

Subject: ✅ GATE 0 VERIFIED
Body: 
  Verification complete. All tests passed:
  
  ✅ verify_redis.py - PASS
  ✅ verify_sqlite.py - PASS
  ✅ verify_messaging.py - PASS
  ✅ verify_two_way_communication.py - PASS
  
  System is functional. You may proceed.
  
  Signed: Gemini CLI
  Timestamp: [current timestamp]

═══════════════════════════════════════════════════════════
CRITICAL NOTES:
═══════════════════════════════════════════════════════════

- DO NOT just say "looks good" - you must ACTUALLY run the scripts
- DO NOT skip any verification step
- If ANY test fails, notify me immediately and we debug together
- I am BLOCKED from building anything else until you confirm
- This is Phase Gate 0 - we cannot advance without passing

═══════════════════════════════════════════════════════════

Work completed so far (solo work, before collaboration):
- src/comms/redis_messenger.py (Redis integration)
- src/comms/message_archive.py (SQLite persistence)
- src/comms/messaging_system.py (Complete system)
- scripts/verify_*.py (Verification scripts)
- scripts/announce_to_gemini.py (This message!)

Stats: 4 files created, ~400 lines of code, all verification tests passing.

Once you verify and confirm, we'll collaborate on everything else (50/50).

Looking forward to working with you!

- Claude Code
''',
        'work_completed': {
            'files_added': [
                'src/comms/redis_messenger.py',
                'src/comms/message_archive.py',
                'src/comms/messaging_system.py',
                'scripts/verify_redis.py',
                'scripts/verify_sqlite.py',
                'scripts/verify_messaging.py',
                'scripts/verify_two_way_communication.py',
                'scripts/announce_to_gemini.py'
            ],
            'commits': [
                {
                    'message': 'feat(comms): Build real-time messaging system with verification',
                    'files': 8,
                    'lines_added': 400
                }
            ],
            'lines_added': 400,
            'tests_passing': True,
            'verification_complete': True
        },
        'context_understanding': {
            'current_goal': 'Enable real-time agent communication',
            'phase': 'Gate 0 - Messaging System',
            'completed': True,
            'next_steps': [
                'Wait for Gemini verification',
                'Fix any issues Gemini finds',
                'Get mutual sign-off',
                'Proceed to collaborative development'
            ]
        },
        'requests': {
            'action_needed': 'mandatory_verification',
            'blocking': True,
            'priority': 'CRITICAL',
            'specific_asks': [
                'Run all four verification scripts',
                'Confirm ALL tests pass',
                'Send formal verification confirmation',
                'No proceeding without this'
            ]
        }
    })
    
    print("✅ First message sent to Gemini!")
    print("\nNow listening for Gemini's response...")
    
    # Listen for response
    def on_response(msg):
        print(f"\n{'='*60}")
        print(f"📨 RESPONSE FROM GEMINI")
        print(f"{'='*60}\n")
        print(f"Subject: {msg['content']['subject']}")
        print(f"\n{msg['content'].get('body', '')}\n")
        print(f"{'='*60}\n")
    
    claude.listen(on_response)
    
    # Keep listening
    print("Press Ctrl+C to stop listening...\n")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n✅ Messaging session ended")

if __name__ == '__main__':
    main()
```

---

## EXECUTION CHECKLIST

### Step 1: Prerequisites (5 min)
```bash
# Install Redis
docker run -d -p 6379:6379 redis

# Or on Windows:
choco install redis

# Verify it's running
docker ps  # Should see redis container
```

### Step 2: Build Messaging System (1 hour)

- [ ] Create `src/comms/redis_messenger.py` (30 min)
- [ ] Create `src/comms/message_archive.py` (20 min)
- [ ] Create `src/comms/messaging_system.py` (20 min)
- [ ] Create `scripts/announce_to_gemini.py` (5 min)

### Step 3: Test It Works (10 min)

```bash
# Test Redis messenger
python src/comms/redis_messenger.py

# Test message archive
python src/comms/message_archive.py

# Test complete system
python src/comms/messaging_system.py
```

**Success = You see:**
```
✅ Connected to Redis on localhost:6379
✅ Message archive ready: data/message_archive.db
✅ Messaging system ready for 'claude'
✅ Message sent!
```

### Step 4: MANDATORY VERIFICATION (Critical!)

**Before you send any message to Gemini, you MUST verify everything actually works:**

```bash
# Create verification scripts (copy from SAFEGUARDS-AND-QUALITY-GATES.md)
python scripts/verify_redis.py        # Redis is running
python scripts/verify_sqlite.py       # SQLite is recording
python scripts/verify_messaging.py    # Messages work
python scripts/verify_two_way_communication.py  # Both directions work
```

**ALL FOUR must show ✅ VERIFIED before proceeding.**

**Why this matters:** Past experience shows systems can LOOK like they work but actually be silently failing. These scripts PROVE the system works.

**If any verification fails:**
- STOP
- Fix the issue
- Re-run verification
- Don't proceed until all pass

### Step 5: Send Verification Message to Gemini (Not just announcement!)

```bash
python scripts/announce_to_gemini.py
```

**This sends your first message to Gemini WITH VERIFICATION REQUIREMENTS.**

**CRITICAL:** This is NOT just "hey it's done" - it's "I've verified it works, now YOU must verify it works too."

### Step 6: BLOCK Until Gemini Confirms

**You CANNOT proceed to build anything else until:**
1. Gemini receives your message
2. Gemini runs the same verification scripts
3. Gemini confirms they all pass
4. Gemini sends you ✅ confirmation message

**Why this is a hard stop:**
- Prevents building on broken foundation
- Ensures both agents have working system
- Catches silent failures early
- Enforces collaborative verification

**While waiting for Gemini:**
- Run the health dashboard: `python scripts/dashboard.py`
- Review your code
- DO NOT start building other components
- Patience - this is critical

---

## WHAT HAPPENS NEXT

Once Gemini receives your message and tests the system:

1. **Gemini reviews your code** → Might suggest changes
2. **You discuss and iterate** → Via the messaging system!
3. **You both decide** → "What should we build next?"
4. **TRUE 50/50 collaboration begins** → Everything from here is built together

---

## CRITICAL SUCCESS FACTORS

### ✅ DO THIS:
- Build the messaging system FIRST
- Test it thoroughly before announcing
- Send the announcement message to Gemini
- Wait for Gemini to respond and test
- Start collaborating on the NEXT component together

### ❌ DON'T DO THIS:
- Build other components before messaging exists
- Skip testing the messaging system
- Assume it works without verification
- Start building the next thing alone

---

## IF YOU ENCOUNTER ISSUES

### Redis won't start:
```bash
# Check if port 6379 is in use
netstat -an | grep 6379

# Kill existing process
docker stop $(docker ps -q --filter ancestor=redis)

# Restart
docker run -d -p 6379:6379 redis
```

### Cannot connect to Redis:
```python
# Check Redis is running
import redis
r = redis.Redis(host='localhost', port=6379)
r.ping()  # Should return True
```

### Messages not being received:
- Verify both agents use same Redis instance
- Check channel names match (claude_inbox, gemini_inbox)
- Ensure listener thread is running

---

## FINAL REMINDER

**The messaging system unlocks everything else.**

Once you and Gemini can communicate:
- ✅ Real-time collaboration
- ✅ Instant code reviews
- ✅ Shared decision making
- ✅ True 50/50 work split
- ✅ Emergent intelligence

**Build this first. Everything else follows.**

---

## Questions?

If you hit ANY issues building this:
1. Check the error message carefully
2. Re-read the relevant section above
3. Test each component independently
4. If still stuck, document the issue and send a message to Jack

**YOU GOT THIS! 🚀**

The messaging system is ~300 lines of straightforward Python. You've built far more complex systems. This is just connecting Redis + SQLite with a clean API.

**Once this is done, the real collaboration begins!**
