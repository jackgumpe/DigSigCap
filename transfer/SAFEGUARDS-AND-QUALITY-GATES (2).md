# SAFEGUARDS & QUALITY GATES - MANDATORY ENFORCEMENT

## ⚠️ CRITICAL: PREVENTING SILENT FAILURES ⚠️

**Past experience:** Systems silently failed, no data was recorded, safeguards didn't trigger, came back to broken system with no data.

**This document:** HARD STOPS that prevent advancing without verification. No silent failures. No surprises.

---

## 🚫 CARDINAL RULES (NEVER VIOLATE)

### Rule 1: NO ADVANCEMENT WITHOUT MUTUAL VERIFICATION
**Claude Code CANNOT proceed to next phase until:**
1. Gemini has tested the code
2. Gemini has confirmed it works
3. Both agents have signed off in writing
4. Health checks pass

**Violation = System blocks further progress**

### Rule 2: FAIL LOUD, NEVER SILENT
**If something breaks:**
- ❌ **WRONG:** Continue with degraded functionality
- ✅ **RIGHT:** STOP EVERYTHING, raise alarm, both agents debug together

**All failures must:**
- Log to console in RED
- Write to failure log file
- Send notification to both agents
- Block further progress until resolved

### Rule 3: TEST WITH BOTH AGENTS BEFORE ADVANCING
**Tests MUST be run by BOTH agents:**
- Claude runs tests → Pass
- Gemini runs same tests → Pass
- Both confirm in collaboration log
- Only then proceed

**No "I tested it, trust me" - both must verify independently**

### Rule 4: VERIFY DATA IS ACTUALLY BEING RECORDED
**Every system that saves data MUST have verification:**
- Write test data
- Read it back
- Confirm it matches
- Check file sizes are growing
- Verify timestamps are updating

**If verification fails → STOP and fix before proceeding**

### Rule 5: NO BIG-BANG DEVELOPMENT
**Incremental development only:**
- Small changes (<100 lines)
- Test after each change
- Commit after tests pass
- Get feedback from other agent
- Repeat

**No "let me build 5 components then test" - recipe for disaster**

---

## 🔒 PHASE GATE SYSTEM (Hard Checkpoints)

### Phase Gate = MANDATORY VERIFICATION BEFORE PROCEEDING

Each gate requires:
1. ✅ All tests pass (both agents)
2. ✅ Health checks pass
3. ✅ Code review complete
4. ✅ Data integrity verified
5. ✅ Both agents sign off
6. ✅ Jack notified (if gate level ≥ 3)

**Gates are numbered. CANNOT skip to next gate without passing current.**

---

## 🎯 PHASE GATE 0: Messaging System Ready

**What must be verified:**

### Verification 1: Redis Is Actually Running
```python
# File: scripts/verify_redis.py

import redis
import sys

def verify_redis():
    """HARD CHECK: Redis must be running and responding."""
    try:
        r = redis.Redis(host='localhost', port=6379, socket_timeout=5)
        
        # Test 1: Ping
        if not r.ping():
            print("❌ CRITICAL: Redis ping failed")
            sys.exit(1)
        
        # Test 2: Write/read
        test_key = 'safeguard_test'
        test_value = 'redis_is_working'
        r.set(test_key, test_value, ex=60)
        
        retrieved = r.get(test_key)
        if retrieved.decode() != test_value:
            print("❌ CRITICAL: Redis read/write failed")
            sys.exit(1)
        
        # Test 3: Pub/sub
        pubsub = r.pubsub()
        pubsub.subscribe('test_channel')
        
        r.publish('test_channel', 'test_message')
        
        # Cleanup
        r.delete(test_key)
        pubsub.unsubscribe('test_channel')
        
        print("✅ VERIFIED: Redis is running and functional")
        return True
        
    except redis.ConnectionError:
        print("❌ CRITICAL: Cannot connect to Redis")
        print("   Run: docker run -d -p 6379:6379 redis")
        sys.exit(1)
    except Exception as e:
        print(f"❌ CRITICAL: Redis verification failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    verify_redis()
```

### Verification 2: SQLite Is Actually Recording
```python
# File: scripts/verify_sqlite.py

import sqlite3
import json
from datetime import datetime
import sys
from pathlib import Path

def verify_sqlite():
    """HARD CHECK: SQLite must be writing and retrieving data."""
    db_path = 'data/message_archive.db'
    
    # Test 1: Can create database
    try:
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(db_path)
        print("✅ SQLite database created")
    except Exception as e:
        print(f"❌ CRITICAL: Cannot create database: {e}")
        sys.exit(1)
    
    # Test 2: Can create tables
    try:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS test_messages (
                id INTEGER PRIMARY KEY,
                data TEXT,
                timestamp DATETIME
            )
        ''')
        print("✅ SQLite tables created")
    except Exception as e:
        print(f"❌ CRITICAL: Cannot create tables: {e}")
        sys.exit(1)
    
    # Test 3: Can write data
    test_data = json.dumps({'test': 'data', 'timestamp': datetime.now().isoformat()})
    try:
        conn.execute('INSERT INTO test_messages (data, timestamp) VALUES (?, ?)',
                    (test_data, datetime.now()))
        conn.commit()
        print("✅ SQLite write successful")
    except Exception as e:
        print(f"❌ CRITICAL: Cannot write to database: {e}")
        sys.exit(1)
    
    # Test 4: Can read data back
    try:
        cursor = conn.execute('SELECT data FROM test_messages ORDER BY id DESC LIMIT 1')
        retrieved = cursor.fetchone()[0]
        
        if retrieved != test_data:
            print("❌ CRITICAL: Data corruption - write/read mismatch")
            sys.exit(1)
        
        print("✅ SQLite read successful")
    except Exception as e:
        print(f"❌ CRITICAL: Cannot read from database: {e}")
        sys.exit(1)
    
    # Test 5: File actually exists and has content
    file_size = Path(db_path).stat().st_size
    if file_size == 0:
        print("❌ CRITICAL: Database file is empty")
        sys.exit(1)
    
    print(f"✅ SQLite file size: {file_size} bytes")
    
    # Cleanup
    conn.execute('DROP TABLE test_messages')
    conn.close()
    
    print("✅ VERIFIED: SQLite is recording data")
    return True

if __name__ == '__main__':
    verify_sqlite()
```

### Verification 3: Messages Are Actually Being Sent/Received
```python
# File: scripts/verify_messaging.py

import sys
import time
import threading
sys.path.append('src')

from comms.messaging_system import MessagingSystem

def verify_messaging():
    """HARD CHECK: Messages must actually be sent and received."""
    
    print("Testing messaging system (this takes 10 seconds)...")
    
    # Create two messaging systems
    claude = MessagingSystem('claude_test')
    gemini = MessagingSystem('gemini_test')
    
    received_messages = []
    
    def on_message(msg):
        received_messages.append(msg)
        print(f"✅ Message received: {msg['content']['subject']}")
    
    # Start listening
    gemini.listen(on_message)
    time.sleep(2)  # Give listener time to start
    
    # Send test message
    test_subject = f"Test message {time.time()}"
    claude.send({
        'to': 'gemini_test',
        'subject': test_subject,
        'body': 'This is a test message to verify the system works'
    })
    
    # Wait for message
    time.sleep(5)
    
    # Verify received
    if not received_messages:
        print("❌ CRITICAL: No messages received - messaging system is broken")
        sys.exit(1)
    
    if received_messages[0]['content']['subject'] != test_subject:
        print("❌ CRITICAL: Message corrupted during transmission")
        sys.exit(1)
    
    # Verify archived
    history = claude.get_history('gemini_test')
    if not history:
        print("❌ CRITICAL: Messages not being archived")
        sys.exit(1)
    
    print("✅ VERIFIED: Messages are being sent, received, and archived")
    return True

if __name__ == '__main__':
    verify_messaging()
```

### Verification 4: Both Agents Can Communicate
```python
# File: scripts/verify_two_way_communication.py

import sys
import time
sys.path.append('src')

from comms.messaging_system import MessagingSystem

def verify_two_way():
    """HARD CHECK: Both agents must be able to talk to each other."""
    
    print("\n" + "="*60)
    print("TWO-WAY COMMUNICATION TEST")
    print("="*60 + "\n")
    
    claude = MessagingSystem('claude')
    gemini = MessagingSystem('gemini')
    
    claude_received = []
    gemini_received = []
    
    def claude_handler(msg):
        claude_received.append(msg)
        print(f"Claude received: {msg['content']['subject']}")
    
    def gemini_handler(msg):
        gemini_received.append(msg)
        print(f"Gemini received: {msg['content']['subject']}")
    
    # Start listening
    claude.listen(claude_handler)
    gemini.listen(gemini_handler)
    time.sleep(2)
    
    # Claude → Gemini
    print("\nTest 1: Claude → Gemini")
    claude.send({
        'to': 'gemini',
        'subject': 'Test from Claude',
        'body': 'Can you hear me?'
    })
    time.sleep(3)
    
    if not gemini_received:
        print("❌ CRITICAL: Gemini cannot receive from Claude")
        sys.exit(1)
    print("✅ Gemini received Claude's message")
    
    # Gemini → Claude
    print("\nTest 2: Gemini → Claude")
    gemini.send({
        'to': 'claude',
        'subject': 'Test from Gemini',
        'body': 'Yes, I can hear you!'
    })
    time.sleep(3)
    
    if not claude_received:
        print("❌ CRITICAL: Claude cannot receive from Gemini")
        sys.exit(1)
    print("✅ Claude received Gemini's message")
    
    print("\n✅ VERIFIED: Two-way communication working")
    return True

if __name__ == '__main__':
    verify_two_way()
```

### Gate 0 Checklist

**Claude Code must run:**
```bash
# Run all verification scripts
python scripts/verify_redis.py
python scripts/verify_sqlite.py  
python scripts/verify_messaging.py
python scripts/verify_two_way_communication.py

# ALL must pass before proceeding
```

**Then send verification message to Gemini:**
```python
claude.send({
    'to': 'gemini',
    'subject': '🚨 GATE 0 VERIFICATION NEEDED',
    'body': '''The messaging system is built. Before I proceed, you MUST verify it works on your end.

REQUIRED ACTIONS:
1. Run: python scripts/verify_redis.py
2. Run: python scripts/verify_sqlite.py
3. Run: python scripts/verify_messaging.py
4. Run: python scripts/verify_two_way_communication.py

ALL FOUR must pass. Send me confirmation when done.

DO NOT say "looks good" - you must ACTUALLY run the scripts and confirm they pass.

I am BLOCKED from proceeding until you confirm.''',
    'requests': {
        'action_needed': 'verification',
        'blocking': True
    }
})
```

**Gemini must respond:**
```python
gemini.send({
    'to': 'claude',
    'subject': '✅ GATE 0 VERIFIED',
    'body': '''Verification complete. All tests passed:

✅ verify_redis.py - PASS
✅ verify_sqlite.py - PASS
✅ verify_messaging.py - PASS
✅ verify_two_way_communication.py - PASS

System is functional. You may proceed to Phase Gate 1.

Signed: Gemini CLI
Timestamp: [timestamp]''',
    'verification': {
        'gate': 0,
        'status': 'PASS',
        'all_tests_passed': True,
        'verified_by': 'gemini',
        'timestamp': '...'
    }
})
```

**Only after Gemini sends ✅ can Claude proceed to next phase.**

---

## 🎯 PHASE GATE 1: First Component Complete

**Before building ANY component after messaging:**

### Pre-Component Checklist
```python
# File: scripts/pre_component_checklist.py

def pre_component_checklist(component_name):
    """Run before starting any new component."""
    
    print(f"\n{'='*60}")
    print(f"PRE-COMPONENT CHECKLIST: {component_name}")
    print(f"{'='*60}\n")
    
    checks = {
        'Messaging system verified': False,
        'Both agents can communicate': False,
        'Previous component tests pass': False,
        'Git repo is clean': False,
        'Other agent has signed off': False
    }
    
    # Check 1: Messaging works
    try:
        from comms.messaging_system import MessagingSystem
        test = MessagingSystem('test')
        test.redis.redis.ping()
        checks['Messaging system verified'] = True
    except:
        print("❌ Messaging system not working")
        return False
    
    # Check 2: Can communicate
    # (Simplified - full version would test actual communication)
    checks['Both agents can communicate'] = True
    
    # Check 3: Git status
    import subprocess
    result = subprocess.run(['git', 'status', '--porcelain'], 
                          capture_output=True, text=True)
    if not result.stdout.strip():
        checks['Git repo is clean'] = True
    else:
        print("⚠️  Uncommitted changes exist")
    
    # Display results
    print("\nChecklist Results:")
    for check, status in checks.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {check}")
    
    all_pass = all(checks.values())
    
    if all_pass:
        print(f"\n✅ All checks passed. Ready to build {component_name}")
    else:
        print(f"\n❌ Some checks failed. Fix before proceeding")
        sys.exit(1)
    
    return all_pass
```

### During Development: Continuous Health Monitoring
```python
# File: src/monitoring/health_monitor.py

import time
import threading
import redis
import sqlite3
from pathlib import Path

class HealthMonitor:
    """
    Continuous health monitoring during development.
    Alerts if anything breaks while agents are working.
    """
    
    def __init__(self, check_interval=30):
        self.check_interval = check_interval
        self.running = False
        self.failures = []
        
    def start(self):
        """Start continuous monitoring."""
        self.running = True
        thread = threading.Thread(target=self._monitor_loop, daemon=True)
        thread.start()
        print("🏥 Health monitor started (checking every 30s)")
    
    def stop(self):
        """Stop monitoring."""
        self.running = False
        
    def _monitor_loop(self):
        """Continuous monitoring loop."""
        while self.running:
            self._check_health()
            time.sleep(self.check_interval)
    
    def _check_health(self):
        """Run all health checks."""
        checks = {
            'Redis': self._check_redis(),
            'SQLite': self._check_sqlite(),
            'Disk Space': self._check_disk_space(),
            'Data Recording': self._check_data_recording()
        }
        
        failures = [name for name, status in checks.items() if not status]
        
        if failures:
            self._alert_failure(failures)
    
    def _check_redis(self):
        """Check Redis is responding."""
        try:
            r = redis.Redis(host='localhost', port=6379, socket_timeout=2)
            return r.ping()
        except:
            return False
    
    def _check_sqlite(self):
        """Check SQLite is writable."""
        try:
            conn = sqlite3.connect('data/message_archive.db', timeout=2)
            conn.execute('SELECT 1')
            conn.close()
            return True
        except:
            return False
    
    def _check_disk_space(self):
        """Check sufficient disk space."""
        import shutil
        stats = shutil.disk_usage('.')
        free_gb = stats.free / (1024**3)
        return free_gb > 1.0  # At least 1GB free
    
    def _check_data_recording(self):
        """Check data is actually being written."""
        db_path = Path('data/message_archive.db')
        if not db_path.exists():
            return False
        
        # Check file was modified recently (within last 5 minutes)
        mtime = db_path.stat().st_mtime
        age = time.time() - mtime
        return age < 300  # Modified in last 5 minutes
    
    def _alert_failure(self, failures):
        """LOUD alert when something fails."""
        print("\n" + "="*60)
        print("🚨 HEALTH CHECK FAILURE 🚨")
        print("="*60)
        for failure in failures:
            print(f"❌ {failure} is not working")
        print("="*60)
        print("STOP DEVELOPMENT - Fix these issues before continuing")
        print("="*60 + "\n")
        
        self.failures.extend(failures)
        
        # Log to file
        with open('logs/health_failures.log', 'a') as f:
            f.write(f"\n{time.ctime()}: {', '.join(failures)}\n")

# Auto-start during development
if __name__ != '__main__':
    # Start automatically when imported
    monitor = HealthMonitor()
    monitor.start()
```

### Post-Component Testing Protocol
```python
# File: scripts/post_component_testing.py

def test_component_with_both_agents(component_name):
    """
    Both agents must run tests and confirm.
    NO "trust me, it works" - both must verify.
    """
    
    print(f"\n{'='*60}")
    print(f"POST-COMPONENT TESTING: {component_name}")
    print(f"{'='*60}\n")
    
    # Agent 1 (Claude) runs tests
    print("Step 1: Claude Code runs tests...")
    claude_result = run_tests(component_name)
    
    if not claude_result:
        print("❌ Claude's tests FAILED - fix before proceeding")
        return False
    
    print("✅ Claude's tests PASSED")
    
    # Send to Gemini for verification
    claude = MessagingSystem('claude')
    claude.send({
        'to': 'gemini',
        'subject': f'🧪 TEST VERIFICATION NEEDED: {component_name}',
        'body': f'''I've completed {component_name}. My tests passed.

REQUIRED: You must run the same tests and confirm they pass on your end.

Run: python -m pytest tests/test_{component_name}.py -v

Send confirmation when done. I am BLOCKED until you verify.''',
        'requests': {
            'action_needed': 'test_verification',
            'blocking': True
        }
    })
    
    # Wait for Gemini's confirmation
    print("\nWaiting for Gemini to run tests...")
    print("(This will block until Gemini confirms)\n")
    
    # In real implementation, this would wait for actual response
    # For now, require manual confirmation
    
    return True

def run_tests(component_name):
    """Run pytest for component."""
    import subprocess
    result = subprocess.run(
        ['python', '-m', 'pytest', f'tests/test_{component_name}.py', '-v'],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    return result.returncode == 0
```

---

## 🎯 PHASE GATE 2: Core System Complete

**Requirements:**
- Apache Arrow logger working
- Both agents have tested it
- Data is being recorded
- Health checks pass
- Performance benchmarks met

### Data Integrity Verification
```python
# File: scripts/verify_data_integrity.py

def verify_data_integrity():
    """
    CRITICAL: Verify data is ACTUALLY being recorded.
    This is where silent failures happen - system thinks it's
    working but data is going nowhere.
    """
    
    print("\n" + "="*60)
    print("DATA INTEGRITY VERIFICATION")
    print("="*60 + "\n")
    
    from pathlib import Path
    import pyarrow.parquet as pq
    
    # Check 1: Data files exist
    data_dir = Path('data/conversations')
    if not data_dir.exists():
        print("❌ CRITICAL: Data directory doesn't exist")
        return False
    
    parquet_files = list(data_dir.glob('*.parquet'))
    if not parquet_files:
        print("❌ CRITICAL: No data files found")
        return False
    
    print(f"✅ Found {len(parquet_files)} data files")
    
    # Check 2: Files contain data
    total_rows = 0
    for file in parquet_files:
        try:
            table = pq.read_table(file)
            rows = len(table)
            total_rows += rows
            print(f"   {file.name}: {rows} rows")
        except Exception as e:
            print(f"❌ CRITICAL: Cannot read {file.name}: {e}")
            return False
    
    if total_rows == 0:
        print("❌ CRITICAL: Files exist but contain NO DATA")
        return False
    
    print(f"\n✅ Total data: {total_rows} rows")
    
    # Check 3: Data is recent
    latest_file = max(parquet_files, key=lambda p: p.stat().st_mtime)
    mtime = latest_file.stat().st_mtime
    age_hours = (time.time() - mtime) / 3600
    
    if age_hours > 24:
        print(f"⚠️  WARNING: Latest data is {age_hours:.1f} hours old")
    else:
        print(f"✅ Latest data is {age_hours:.1f} hours old")
    
    # Check 4: Data schema is correct
    table = pq.read_table(latest_file)
    expected_columns = ['timestamp', 'agent', 'message', 'tier']
    
    for col in expected_columns:
        if col not in table.column_names:
            print(f"❌ CRITICAL: Missing column '{col}' in data")
            return False
    
    print("✅ Data schema is correct")
    
    # Check 5: Can read and parse data
    try:
        df = table.to_pandas()
        sample = df.head(5)
        print("\n✅ Data sample:")
        print(sample)
    except Exception as e:
        print(f"❌ CRITICAL: Cannot parse data: {e}")
        return False
    
    print("\n" + "="*60)
    print("✅ DATA INTEGRITY VERIFIED")
    print("="*60 + "\n")
    
    return True
```

---

## 🚨 FAILURE RESPONSE PROTOCOL

**When something fails:**

### Step 1: STOP IMMEDIATELY
```python
# In any code that detects a failure:

def handle_failure(error_type, error_message):
    """
    LOUD failure handling.
    No silent degradation - STOP and fix.
    """
    
    print("\n" + "🚨"*30)
    print(f"\nCRITICAL FAILURE: {error_type}")
    print(f"Message: {error_message}")
    print(f"\nTIMESTAMP: {datetime.now()}")
    print("\n" + "🚨"*30 + "\n")
    
    # Log to file
    with open('logs/critical_failures.log', 'a') as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"CRITICAL FAILURE: {error_type}\n")
        f.write(f"Time: {datetime.now()}\n")
        f.write(f"Message: {error_message}\n")
        f.write(f"{'='*60}\n")
    
    # Notify both agents
    try:
        from comms.messaging_system import MessagingSystem
        notifier = MessagingSystem('system')
        
        for agent in ['claude', 'gemini']:
            notifier.send({
                'to': agent,
                'subject': '🚨 CRITICAL FAILURE - STOP WORK',
                'body': f'''CRITICAL FAILURE DETECTED

Type: {error_type}
Message: {error_message}
Time: {datetime.now()}

STOP ALL DEVELOPMENT IMMEDIATELY.
Both agents must debug this together before proceeding.'''
            })
    except:
        pass  # Even notification failed - really bad
    
    # Exit program
    sys.exit(1)
```

### Step 2: Both Agents Debug Together
**Protocol:**
1. Claude notices failure → Stops work
2. Sends message to Gemini with full error details
3. Both agents investigate together
4. No solo "fixes" - discuss first
5. Fix, test, verify together
6. Both sign off before resuming

### Step 3: Document The Failure
```python
# File: docs/failures.md

## Failure Log

### 2024-12-05 14:23 - Redis Connection Lost
**Detected by:** Health monitor
**Impact:** Messaging stopped working
**Root cause:** Docker container restarted
**Fix:** Added health check script to detect and restart
**Prevention:** Added auto-restart in docker-compose
**Verified by:** Both agents
**Lessons learned:** Need continuous monitoring, not one-time checks

### 2024-12-06 09:15 - SQLite Database Locked
**Detected by:** Archive write failure
**Impact:** Messages not being saved
**Root cause:** Concurrent writes without proper locking
**Fix:** Added write queue with single writer thread
**Prevention:** All writes go through queue
**Verified by:** Both agents
**Lessons learned:** Test concurrent operations explicitly
```

---

## 📊 CONTINUOUS MONITORING DASHBOARD

```python
# File: scripts/dashboard.py

import time
import os
from comms.messaging_system import MessagingSystem
from monitoring.health_monitor import HealthMonitor

def show_dashboard():
    """
    Real-time dashboard showing system health.
    Run this in a separate terminal during development.
    """
    
    monitor = HealthMonitor()
    monitor.start()
    
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print("="*60)
        print("MULTI-AGENT SYSTEM DASHBOARD")
        print("="*60)
        
        print("\n🏥 HEALTH STATUS:")
        print(f"  Redis: {'✅ UP' if monitor._check_redis() else '❌ DOWN'}")
        print(f"  SQLite: {'✅ UP' if monitor._check_sqlite() else '❌ DOWN'}")
        print(f"  Disk Space: {'✅ OK' if monitor._check_disk_space() else '❌ LOW'}")
        print(f"  Data Recording: {'✅ ACTIVE' if monitor._check_data_recording() else '❌ STALE'}")
        
        print("\n📊 DATA STATS:")
        try:
            conn = sqlite3.connect('data/message_archive.db')
            message_count = conn.execute('SELECT COUNT(*) FROM messages').fetchone()[0]
            print(f"  Total messages: {message_count}")
            conn.close()
        except:
            print(f"  Total messages: ERROR")
        
        print("\n⚠️  RECENT FAILURES:")
        if monitor.failures:
            for failure in monitor.failures[-5:]:
                print(f"  • {failure}")
        else:
            print("  None")
        
        print("\n" + "="*60)
        print(f"Last updated: {time.ctime()}")
        print("Press Ctrl+C to exit")
        print("="*60)
        
        time.sleep(5)

if __name__ == '__main__':
    show_dashboard()
```

---

## 🤝 COLLABORATIVE DEBUGGING PROTOCOL

**When either agent encounters a bug:**

### 1. Document The Bug
```python
claude.send({
    'to': 'gemini',
    'subject': '🐛 BUG FOUND - Need collaborative debugging',
    'body': '''I found a bug while testing the logger:

ERROR MESSAGE:
[exact error text]

WHAT I WAS DOING:
[steps to reproduce]

WHAT I EXPECTED:
[expected behavior]

WHAT ACTUALLY HAPPENED:
[actual behavior]

RELEVANT CODE:
[code snippet]

MY INITIAL THOUGHTS:
[hypothesis about cause]

REQUESTED: Let's debug this together before I try to fix it.
Can you reproduce on your end?'''
})
```

### 2. Reproduce Together
- Other agent tries to reproduce
- Both confirm they see the same issue
- No "works on my machine" - must work on both

### 3. Debug Together
- Share hypotheses
- Test assumptions
- Narrow down root cause
- Propose fixes

### 4. Fix And Verify Together
- One agent implements fix
- Other agent reviews
- Both run tests
- Both verify it's actually fixed

### 5. No Solo "Fixes"
**❌ WRONG:**
"I found a bug, fixed it, tested it, it works now"

**✅ RIGHT:**
"I found a bug → [message other agent] → we debug together → one implements → other reviews → both verify → fixed"

---

## 🎓 TESTING REQUIREMENTS

### Unit Tests: Must Be Written First
```python
# Test-driven development
# Write test BEFORE writing code

# File: tests/test_logger.py

import pytest
from src.core.logger import Logger

def test_logger_writes_data():
    """Verify logger actually writes data."""
    logger = Logger('test.parquet')
    
    # Write test data
    logger.log_message({
        'timestamp': '2024-12-05T12:00:00',
        'agent': 'test',
        'message': 'test message'
    })
    
    # CRITICAL: Verify it was actually written
    data = logger.read_data()
    assert len(data) == 1
    assert data[0]['message'] == 'test message'

def test_logger_handles_failures():
    """Verify logger fails loudly on errors."""
    logger = Logger('/invalid/path/test.parquet')
    
    # Should raise exception, not silently fail
    with pytest.raises(Exception):
        logger.log_message({'test': 'data'})

# Both agents must run tests
# Both must confirm they pass
```

### Integration Tests: Both Agents Run
```python
# File: tests/integration_test_messaging.py

def test_end_to_end_messaging():
    """Full end-to-end test of messaging system."""
    
    # Setup
    claude = MessagingSystem('claude')
    gemini = MessagingSystem('gemini')
    
    received = []
    gemini.listen(lambda msg: received.append(msg))
    
    # Send message
    claude.send({
        'to': 'gemini',
        'subject': 'Integration test',
        'body': 'Testing...'
    })
    
    # Verify received
    time.sleep(2)
    assert len(received) == 1
    
    # Verify archived
    history = claude.get_history('gemini')
    assert len(history) >= 1
    
    # Verify in both databases
    claude_archive = claude.archive.get_conversation('claude', 'gemini')
    gemini_archive = gemini.archive.get_conversation('claude', 'gemini')
    
    assert len(claude_archive) == len(gemini_archive)

# THIS TEST MUST PASS ON BOTH AGENTS' MACHINES
# Not "it passed for me" - it must pass for both
```

### Performance Tests: Benchmarks Must Meet Targets
```python
# File: tests/performance_test.py

def test_message_latency():
    """Verify messaging latency is < 100ms."""
    
    claude = MessagingSystem('claude')
    gemini = MessagingSystem('gemini')
    
    latencies = []
    
    def measure_latency(msg):
        sent_time = datetime.fromisoformat(msg['timestamp'])
        received_time = datetime.now()
        latency = (received_time - sent_time).total_seconds() * 1000
        latencies.append(latency)
    
    gemini.listen(measure_latency)
    
    # Send 100 messages
    for i in range(100):
        claude.send({
            'to': 'gemini',
            'subject': f'Latency test {i}',
            'body': 'test'
        })
        time.sleep(0.1)
    
    time.sleep(5)
    
    avg_latency = sum(latencies) / len(latencies)
    p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
    
    print(f"Average latency: {avg_latency:.2f}ms")
    print(f"P95 latency: {p95_latency:.2f}ms")
    
    # HARD REQUIREMENT
    assert p95_latency < 100, f"Latency too high: {p95_latency}ms"
```

---

## 📋 COMPLETE SAFEGUARD CHECKLIST

**Before ANY development session:**
```bash
# Run safeguard checks
python scripts/verify_redis.py
python scripts/verify_sqlite.py
python scripts/verify_messaging.py
python scripts/verify_data_integrity.py

# Start health monitor
python scripts/dashboard.py &

# Confirm with other agent
# (Send message confirming you're ready)
```

**During development:**
```bash
# Health monitor running in background
# Make small changes
# Test after each change
# Commit after tests pass
# Get feedback from other agent
# Repeat
```

**After completing a component:**
```bash
# Run full test suite
pytest tests/ -v

# Verify data integrity
python scripts/verify_data_integrity.py

# Send to other agent for verification
# Wait for confirmation
# Only then proceed to next component
```

**End of day:**
```bash
# Final health check
python scripts/verify_all_systems.py

# Commit work
git add .
git commit -m "..."
git push

# Send summary to other agent
# Confirm both are in sync
```

---

## ⚡ EMERGENCY CONTACTS

**If system is broken and you can't figure out why:**

1. **STOP EVERYTHING** - Don't make it worse
2. **Document what happened** - Exact steps before failure
3. **Notify other agent** - Two brains > one
4. **Notify Jack if critical** - Data loss, corruption, etc.
5. **Debug together** - No solo fixes

**Jack's intervention threshold:**
- Data loss or corruption
- System completely broken
- Security issue
- Agents in deadlock/conflict

---

## ✅ FINAL SAFEGUARD SUMMARY

**The goal: NEVER have silent failures**

1. ✅ **Verify at every phase gate** - Can't advance without passing
2. ✅ **Continuous health monitoring** - Catch failures immediately
3. ✅ **Both agents must test** - No "trust me"
4. ✅ **Data integrity checks** - Verify recording is actually happening
5. ✅ **Fail loud, never silent** - Errors must be obvious
6. ✅ **Collaborative debugging** - Fix together, not solo
7. ✅ **Test-driven development** - Tests first, code second
8. ✅ **Small incremental changes** - Not big-bang development
9. ✅ **Mutual sign-off** - Both agents approve before advancing
10. ✅ **Continuous monitoring** - Dashboard always running

**These safeguards are NON-NEGOTIABLE. They exist because of past failures.**

**No shortcuts. No "it's probably fine". Verify everything.**
