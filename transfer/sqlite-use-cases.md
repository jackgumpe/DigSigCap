# SQLite: Perfect Use Cases in Multi-Agent System

## TL;DR

**SQLite is NOT ideal for:** Real-time messaging (requires polling)
**SQLite IS ideal for:** Everything else that needs a database!

---

## RECOMMENDED ARCHITECTURE: Redis + SQLite Together

```
Real-Time Layer (Redis)
├── Instant messaging
├── Push notifications
└── Live collaboration

Persistence Layer (SQLite)
├── Message archive
├── Work log/audit trail
├── Analytics database
├── Decision database
└── Configuration storage
```

**Why this combo is perfect:**
- Redis = Fast, ephemeral, real-time
- SQLite = Persistent, queryable, analytical

---

## USE CASE 1: Message Archive (Essential!)

### The Problem
Redis is **in-memory** - if Redis crashes or you restart it, all messages are gone!

### The Solution
Every message sent via Redis is ALSO saved to SQLite for permanent storage.

```python
class MessageArchive:
    def __init__(self, db_path='data/message_archive.db'):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT UNIQUE,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                from_agent TEXT,
                to_agent TEXT,
                message_type TEXT,
                subject TEXT,
                body TEXT,
                work_completed JSON,
                context_data JSON,
                delivery_confirmed BOOLEAN DEFAULT 0,
                read_at DATETIME
            )
        ''')
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON messages(timestamp)')
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_agents ON messages(from_agent, to_agent)')
        
    def archive_message(self, message: dict):
        """Save message to permanent storage."""
        self.conn.execute('''
            INSERT INTO messages (message_id, from_agent, to_agent, message_type, 
                                  subject, body, work_completed, context_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            message['message_id'],
            message['from'],
            message['to'],
            message['type'],
            message['content']['subject'],
            message['content']['body'],
            json.dumps(message.get('work_completed')),
            json.dumps(message.get('context_understanding'))
        ))
        self.conn.commit()
    
    def get_conversation_history(self, agent1: str, agent2: str, limit=50):
        """Retrieve full conversation between two agents."""
        return self.conn.execute('''
            SELECT * FROM messages 
            WHERE (from_agent=? AND to_agent=?) OR (from_agent=? AND to_agent=?)
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (agent1, agent2, agent2, agent1, limit)).fetchall()
    
    def search_messages(self, query: str):
        """Full-text search across all messages."""
        return self.conn.execute('''
            SELECT * FROM messages
            WHERE subject LIKE ? OR body LIKE ?
            ORDER BY timestamp DESC
        ''', (f'%{query}%', f'%{query}%')).fetchall()
```

**Usage:**
```python
# When sending via Redis
redis.publish('gemini_inbox', json.dumps(message))
archive.archive_message(message)  # Also save permanently!

# Later: retrieve full history
history = archive.get_conversation_history('claude', 'gemini')
```

**Value:** Never lose conversation history, can review later, audit trail.

---

## USE CASE 2: Work Log / Audit Trail

### What It Tracks
Every file change, commit, test run, deployment - permanent queryable record.

```python
class WorkLog:
    def __init__(self, db_path='data/work_log.db'):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS work_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                agent TEXT,
                event_type TEXT,  -- 'file_created', 'file_modified', 'commit', 'test_run', etc.
                description TEXT,
                files_affected JSON,
                lines_added INTEGER,
                lines_deleted INTEGER,
                commit_hash TEXT,
                success BOOLEAN,
                metadata JSON
            )
        ''')
        
    def log_file_change(self, agent: str, action: str, files: list, lines_changed: dict):
        """Log whenever an agent creates/modifies files."""
        self.conn.execute('''
            INSERT INTO work_events (agent, event_type, files_affected, 
                                     lines_added, lines_deleted)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            agent,
            f'file_{action}',
            json.dumps(files),
            lines_changed.get('added', 0),
            lines_changed.get('deleted', 0)
        ))
        self.conn.commit()
    
    def log_commit(self, agent: str, commit_hash: str, message: str, files: list):
        """Log git commits."""
        self.conn.execute('''
            INSERT INTO work_events (agent, event_type, description, 
                                     commit_hash, files_affected)
            VALUES (?, 'git_commit', ?, ?, ?)
        ''', (agent, message, commit_hash, json.dumps(files)))
        self.conn.commit()
    
    def get_agent_activity(self, agent: str, days=7):
        """See what an agent has been working on."""
        return self.conn.execute('''
            SELECT * FROM work_events
            WHERE agent=? AND timestamp > datetime('now', '-{} days')
            ORDER BY timestamp DESC
        '''.format(days), (agent,)).fetchall()
    
    def get_work_balance_metrics(self):
        """Check if work is balanced 50/50."""
        return self.conn.execute('''
            SELECT 
                agent,
                COUNT(*) as total_events,
                SUM(lines_added) as total_lines_added,
                SUM(lines_deleted) as total_lines_deleted,
                COUNT(DISTINCT DATE(timestamp)) as active_days
            FROM work_events
            WHERE timestamp > datetime('now', '-30 days')
            GROUP BY agent
        ''').fetchall()
```

**Value:** 
- Track who's doing what
- Ensure 50/50 work balance
- Detect if one agent is dominating
- Audit trail for debugging ("when did this file change?")

---

## USE CASE 3: Decision Database

### What It Stores
Every architectural decision, debate, conflict resolution - with full context.

```python
class DecisionLog:
    def __init__(self, db_path='data/decisions.db'):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                decision_id TEXT UNIQUE,
                category TEXT,  -- 'architecture', 'api_design', 'dependency', etc.
                question TEXT,
                claude_position TEXT,
                gemini_position TEXT,
                final_decision TEXT,
                rationale TEXT,
                decision_method TEXT,  -- 'consensus', 'compromise', 'vote', 'jack_override'
                participants JSON,
                related_files JSON,
                status TEXT DEFAULT 'active',  -- 'active', 'revised', 'deprecated'
                impact_score INTEGER  -- 1-10, how important is this decision?
            )
        ''')
        
    def log_decision(self, question: str, claude_pos: str, gemini_pos: str, 
                     final: str, rationale: str):
        """Record an architectural decision."""
        decision_id = f"decision_{int(time.time())}"
        self.conn.execute('''
            INSERT INTO decisions (decision_id, question, claude_position, 
                                  gemini_position, final_decision, rationale)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (decision_id, question, claude_pos, gemini_pos, final, rationale))
        self.conn.commit()
        return decision_id
    
    def get_decision_history(self, category=None):
        """Retrieve past decisions (learn from history!)."""
        if category:
            return self.conn.execute('''
                SELECT * FROM decisions 
                WHERE category=? 
                ORDER BY timestamp DESC
            ''', (category,)).fetchall()
        else:
            return self.conn.execute('''
                SELECT * FROM decisions 
                ORDER BY timestamp DESC
            ''').fetchall()
    
    def revise_decision(self, decision_id: str, new_decision: str, reason: str):
        """Update a decision (with audit trail)."""
        self.conn.execute('''
            UPDATE decisions 
            SET status='revised', final_decision=?, rationale=?
            WHERE decision_id=?
        ''', (new_decision, reason, decision_id))
        self.conn.commit()
```

**Value:**
- "Why did we choose X over Y?" - Just query the database!
- Learn from past decisions
- Track decision evolution
- Show Jack exactly how agents are collaborating

---

## USE CASE 4: Analytics Dashboard Data

### What It Powers
Jack's oversight dashboard - see collaboration metrics in real-time.

```python
class AnalyticsDB:
    def __init__(self, db_path='data/analytics.db'):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS daily_metrics (
                date DATE PRIMARY KEY,
                claude_commits INTEGER DEFAULT 0,
                gemini_commits INTEGER DEFAULT 0,
                claude_lines_added INTEGER DEFAULT 0,
                gemini_lines_added INTEGER DEFAULT 0,
                messages_sent INTEGER DEFAULT 0,
                decisions_made INTEGER DEFAULT 0,
                conflicts_resolved INTEGER DEFAULT 0,
                tests_passed INTEGER DEFAULT 0,
                tests_failed INTEGER DEFAULT 0
            )
        ''')
        
    def update_daily_metrics(self, agent: str, metric: str, value: int):
        """Update metrics for today."""
        today = datetime.now().date()
        column = f"{agent}_{metric}"
        self.conn.execute(f'''
            INSERT INTO daily_metrics (date, {column})
            VALUES (?, ?)
            ON CONFLICT(date) DO UPDATE SET {column} = {column} + ?
        ''', (today, value, value))
        self.conn.commit()
    
    def get_weekly_summary(self):
        """Generate Jack's weekly dashboard."""
        return self.conn.execute('''
            SELECT 
                date,
                claude_commits + gemini_commits as total_commits,
                (claude_commits * 100.0 / (claude_commits + gemini_commits)) as claude_percentage,
                claude_lines_added + gemini_lines_added as total_lines,
                decisions_made,
                conflicts_resolved,
                tests_passed,
                tests_failed
            FROM daily_metrics
            WHERE date > date('now', '-7 days')
            ORDER BY date
        ''').fetchall()
    
    def check_balance(self):
        """Alert if work is unbalanced (>70% one agent)."""
        result = self.conn.execute('''
            SELECT 
                SUM(claude_commits) as claude_total,
                SUM(gemini_commits) as gemini_total
            FROM daily_metrics
            WHERE date > date('now', '-7 days')
        ''').fetchone()
        
        total = result[0] + result[1]
        if total == 0:
            return True
        
        claude_pct = (result[0] / total) * 100
        if claude_pct > 70 or claude_pct < 30:
            return False  # Unbalanced!
        return True
```

**Value:**
- Jack can see metrics without asking
- Auto-detect imbalances
- Track progress over time
- Generate reports

---

## USE CASE 5: Configuration Management

### What It Stores
System settings, agent preferences, tier assignments, token budgets.

```python
class ConfigDB:
    def __init__(self, db_path='data/config.db'):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT,
                value_type TEXT,  -- 'int', 'float', 'string', 'json'
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_by TEXT
            )
        ''')
        
    def set_config(self, key: str, value, updated_by: str):
        """Set a configuration value."""
        if isinstance(value, (dict, list)):
            value_str = json.dumps(value)
            value_type = 'json'
        elif isinstance(value, int):
            value_str = str(value)
            value_type = 'int'
        elif isinstance(value, float):
            value_str = str(value)
            value_type = 'float'
        else:
            value_str = str(value)
            value_type = 'string'
        
        self.conn.execute('''
            INSERT INTO config (key, value, value_type, updated_by)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET 
                value=?, value_type=?, updated_at=CURRENT_TIMESTAMP, updated_by=?
        ''', (key, value_str, value_type, updated_by, value_str, value_type, updated_by))
        self.conn.commit()
    
    def get_config(self, key: str, default=None):
        """Get a configuration value."""
        result = self.conn.execute(
            'SELECT value, value_type FROM config WHERE key=?', 
            (key,)
        ).fetchone()
        
        if not result:
            return default
        
        value_str, value_type = result
        if value_type == 'json':
            return json.loads(value_str)
        elif value_type == 'int':
            return int(value_str)
        elif value_type == 'float':
            return float(value_str)
        else:
            return value_str
```

**Value:**
- Centralized configuration
- Track who changed what setting
- Easy to query/update
- Version history

---

## USE CASE 6: Checkpoint Metadata

### What It Stores
Not the full checkpoint data (that's in Parquet), but METADATA about checkpoints.

```python
class CheckpointRegistry:
    def __init__(self, db_path='data/checkpoints.db'):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS checkpoints (
                checkpoint_id TEXT PRIMARY KEY,
                checkpoint_type TEXT,  -- 'main', 'sub', 'micro'
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                message_count INTEGER,
                conversation_id TEXT,
                parent_checkpoint TEXT,
                data_path TEXT,  -- Path to Parquet file
                summary TEXT,
                entities JSON,
                active_threads JSON,
                tier_distribution JSON,
                file_size_bytes INTEGER,
                quality_score FLOAT
            )
        ''')
        
    def register_checkpoint(self, checkpoint_id: str, checkpoint_type: str, 
                           data_path: str, metadata: dict):
        """Register a new checkpoint."""
        self.conn.execute('''
            INSERT INTO checkpoints 
            (checkpoint_id, checkpoint_type, data_path, message_count,
             summary, entities, active_threads, tier_distribution, quality_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            checkpoint_id,
            checkpoint_type,
            data_path,
            metadata['message_count'],
            metadata['summary'],
            json.dumps(metadata['entities']),
            json.dumps(metadata['active_threads']),
            json.dumps(metadata['tier_distribution']),
            metadata.get('quality_score', 0.0)
        ))
        self.conn.commit()
    
    def find_checkpoint(self, message_id: str):
        """Find which checkpoint contains a specific message."""
        # This would query based on message_count ranges
        pass
    
    def list_checkpoints(self, conversation_id: str, checkpoint_type=None):
        """List all checkpoints for a conversation."""
        if checkpoint_type:
            return self.conn.execute('''
                SELECT * FROM checkpoints
                WHERE conversation_id=? AND checkpoint_type=?
                ORDER BY created_at
            ''', (conversation_id, checkpoint_type)).fetchall()
        else:
            return self.conn.execute('''
                SELECT * FROM checkpoints
                WHERE conversation_id=?
                ORDER BY created_at
            ''', (conversation_id,)).fetchall()
```

**Value:**
- Quick lookups: "Which checkpoint has message 5000?"
- Don't need to load Parquet files to find checkpoints
- Metadata queries are instant

---

## ARCHITECTURE: How It All Fits Together

```
┌─────────────────────────────────────────┐
│         REDIS (Real-Time Layer)         │
│  ┌────────────┐      ┌────────────┐    │
│  │   Claude   │◄────►│   Gemini   │    │
│  │   Inbox    │      │   Inbox    │    │
│  └────────────┘      └────────────┘    │
└──────────────┬──────────────────────────┘
               │ Every message also sent to...
               ▼
┌─────────────────────────────────────────┐
│        SQLite (Persistence Layer)        │
│                                          │
│  ┌──────────────┐  ┌──────────────┐    │
│  │   Message    │  │   Work Log   │    │
│  │   Archive    │  │              │    │
│  └──────────────┘  └──────────────┘    │
│                                          │
│  ┌──────────────┐  ┌──────────────┐    │
│  │   Decision   │  │  Analytics   │    │
│  │   Database   │  │              │    │
│  └──────────────┘  └──────────────┘    │
│                                          │
│  ┌──────────────┐  ┌──────────────┐    │
│  │    Config    │  │  Checkpoint  │    │
│  │              │  │   Registry   │    │
│  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────┘
```

---

## COMPLETE INTEGRATION EXAMPLE

```python
# comms/messaging_system.py

class MessagingSystem:
    def __init__(self, agent_id: str):
        # Redis for real-time
        self.redis = RedisMessenger(agent_id)
        
        # SQLite for persistence
        self.archive = MessageArchive()
        self.work_log = WorkLog()
        self.decisions = DecisionLog()
        self.analytics = AnalyticsDB()
        self.config = ConfigDB()
        
        self.agent_id = agent_id
    
    def send_message(self, to_agent: str, message: dict):
        """Send message via Redis AND save to SQLite."""
        # Real-time delivery
        self.redis.send_message(to_agent, message)
        
        # Permanent archive
        self.archive.archive_message(message)
        
        # Update analytics
        self.analytics.update_daily_metrics(self.agent_id, 'messages_sent', 1)
        
        # Log work if included
        if 'work_completed' in message:
            work = message['work_completed']
            if work.get('files_added') or work.get('files_modified'):
                self.work_log.log_file_change(
                    self.agent_id,
                    'modified',
                    work.get('files_modified', []),
                    {'added': work.get('lines_added', 0)}
                )
    
    def start_listening(self, callback):
        """Listen for messages (real-time via Redis)."""
        def handle_message(msg):
            # Archive incoming message
            self.archive.archive_message(msg)
            
            # Call user's callback
            callback(msg)
        
        self.redis.start_listening(handle_message)
    
    def log_decision(self, question: str, my_position: str, 
                     their_position: str, final: str, rationale: str):
        """Record an architectural decision."""
        return self.decisions.log_decision(
            question, 
            my_position if self.agent_id == 'claude' else their_position,
            their_position if self.agent_id == 'claude' else my_position,
            final,
            rationale
        )
    
    def get_my_metrics(self):
        """How am I doing this week?"""
        return self.analytics.get_weekly_summary()

# Usage
claude = MessagingSystem('claude')
claude.send_message('gemini', {...})  # Sent via Redis, archived in SQLite
claude.log_decision(...)              # Saved to SQLite
metrics = claude.get_my_metrics()     # Query SQLite
```

---

## ANSWER TO YOUR QUESTION

**Q: Is SQLite worth looking into for another function?**

**A: ABSOLUTELY YES!** 

SQLite should be used for:
1. ✅ **Message Archive** (essential - Redis is ephemeral!)
2. ✅ **Work Log** (track who did what)
3. ✅ **Decision Database** (record architectural choices)
4. ✅ **Analytics** (power Jack's dashboard)
5. ✅ **Configuration** (system settings)
6. ✅ **Checkpoint Registry** (metadata about checkpoints)

**The architecture should be:**
- **Redis:** Real-time messaging (instant notifications)
- **SQLite:** Everything else (persistent, queryable)
- **Parquet/Arrow:** Raw conversation data (bulk storage)
- **Neo4j:** Thread graphs (relationships)
- **Qdrant:** Embeddings (semantic search)

Each tool for its strength! SQLite is absolutely critical for this project - just not for real-time messaging.

---

## IMPLEMENTATION PRIORITY

**Week 1: Core messaging**
- Redis real-time layer
- SQLite message archive

**Week 2: Logging & tracking**
- Work log
- Analytics database

**Week 3: Decision tracking**
- Decision database
- Configuration management

**Week 4: Advanced features**
- Checkpoint registry
- Dashboard integration

**This is definitely worth implementing!** SQLite gives you a queryable history of EVERYTHING that happens in the system.
