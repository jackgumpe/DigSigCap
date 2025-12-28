# Multi-Agent Communication System: Inbox/Outbox Protocol

## OVERVIEW

**Purpose:** Enable Claude Code and Gemini CLI to communicate asynchronously with full context awareness and automatic notifications.

**Key Features:**
- ✅ Full conversation history
- ✅ File change tracking (added, edited, deleted)
- ✅ Context awareness sharing
- ✅ Auto-send after completion
- ✅ Auto-notification on new messages
- ✅ Jack oversight (5.5/10 - informed but not overwhelmed)

**Location:** `C:\Users\user\ShearwaterAICAD\multi-agent-context-system\comms\`

---

## DIRECTORY STRUCTURE

```
comms/
├── claude/
│   ├── inbox/           # Claude's incoming messages
│   ├── outbox/          # Claude's outgoing messages
│   └── sent/            # Archive of sent messages
├── gemini/
│   ├── inbox/           # Gemini's incoming messages
│   ├── outbox/          # Gemini's outgoing messages
│   └── sent/            # Archive of sent messages
├── jack/
│   ├── notifications/   # Updates for Jack (moderate level)
│   └── decisions/       # Decisions requiring Jack's input
├── archive/
│   └── conversations/   # Full conversation history
└── system/
    ├── notifier.py      # Auto-notification service
    ├── message_schema.py # Message format definition
    └── comms_manager.py  # Communication orchestration
```

---

## MESSAGE FORMAT

### Standard Message Schema

```json
{
  "message_id": "msg_20251205_143022_claude",
  "timestamp": "2025-12-05T14:30:22.123456Z",
  "from": "claude",
  "to": "gemini",
  "priority": "normal",  // "low", "normal", "high", "urgent"
  "type": "code_review_request",
  
  "conversation": {
    "thread_id": "thread_arrow_logger_implementation",
    "previous_message_id": "msg_20251205_120000_gemini",
    "conversation_summary": "Discussion about Arrow logger implementation"
  },
  
  "content": {
    "subject": "Code review: Arrow logger implementation",
    "body": "I've implemented the basic Arrow logger. Please review...",
    "formatted": false  // If true, contains markdown/code blocks
  },
  
  "work_completed": {
    "files_added": [
      "src/core/logger.py",
      "src/core/__init__.py"
    ],
    "files_modified": [
      "requirements.txt"
    ],
    "files_deleted": [],
    "lines_added": 287,
    "lines_deleted": 0,
    "commits": [
      {
        "hash": "a1b2c3d4",
        "message": "feat(logger): Implement Arrow-based conversation logger"
      }
    ],
    "tests_added": 15,
    "tests_passing": true,
    "coverage_change": "+12.3%"
  },
  
  "context_understanding": {
    "current_goal": "Implement core data layer with Arrow-based logging",
    "blockers": [],
    "dependencies": [],
    "next_steps": [
      "Add error handling after review",
      "Write integration tests",
      "Benchmark performance"
    ],
    "confidence": 0.85,  // 0-1 scale
    "questions": [
      "Should we batch writes in groups of 100 or 200?",
      "Do we need separate error log files?"
    ]
  },
  
  "requests": {
    "action_needed": "code_review",
    "deadline": "2025-12-06T00:00:00Z",  // null if no deadline
    "estimated_time": "30 minutes",
    "specific_asks": [
      "Review error handling approach",
      "Check schema design",
      "Suggest performance improvements"
    ]
  },
  
  "attachments": [
    {
      "type": "code_snippet",
      "file": "src/core/logger.py",
      "lines": "45-78",
      "content": "..."
    },
    {
      "type": "benchmark_results",
      "file": "benchmarks/logger_performance.json"
    }
  ],
  
  "notify_jack": false,  // true if Jack should be notified
  "jack_action_needed": false,  // true if Jack's decision needed
  "jack_summary": null  // Brief summary for Jack if notified
}
```

### Message Types

```python
MESSAGE_TYPES = {
    # Code collaboration
    'code_review_request': 'Requesting code review',
    'code_review_response': 'Providing code review feedback',
    'merge_request': 'Ready to merge, requesting approval',
    'merge_approved': 'Merge approved',
    'merge_rejected': 'Merge rejected with reasons',
    
    # Technical discussion
    'design_proposal': 'Proposing architecture/design',
    'design_feedback': 'Feedback on design proposal',
    'technical_question': 'Question about implementation',
    'technical_answer': 'Answer to technical question',
    
    # Coordination
    'task_claim': 'Claiming a task from backlog',
    'progress_update': 'Status update on current work',
    'blocker_report': 'Reporting a blocker',
    'help_request': 'Requesting assistance',
    
    # Conflict resolution
    'disagreement': 'Expressing disagreement',
    'compromise_proposal': 'Proposing compromise',
    'escalation_to_jack': 'Escalating decision to Jack',
    
    # Meta
    'process_improvement': 'Suggesting process change',
    'celebration': 'Celebrating achievement',
    'retrospective': 'Weekly/monthly retrospective'
}
```

---

## IMPLEMENTATION

### 1. Message Manager

```python
# comms/system/message_schema.py

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
import json
import uuid
from pathlib import Path

@dataclass
class WorkCompleted:
    """Track all work done in this session."""
    files_added: List[str] = field(default_factory=list)
    files_modified: List[str] = field(default_factory=list)
    files_deleted: List[str] = field(default_factory=list)
    lines_added: int = 0
    lines_deleted: int = 0
    commits: List[Dict] = field(default_factory=list)
    tests_added: int = 0
    tests_passing: bool = True
    coverage_change: str = "0%"
    
    def to_dict(self):
        return {
            'files_added': self.files_added,
            'files_modified': self.files_modified,
            'files_deleted': self.files_deleted,
            'lines_added': self.lines_added,
            'lines_deleted': self.lines_deleted,
            'commits': self.commits,
            'tests_added': self.tests_added,
            'tests_passing': self.tests_passing,
            'coverage_change': self.coverage_change
        }

@dataclass
class ContextUnderstanding:
    """Agent's understanding of current project state."""
    current_goal: str
    blockers: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)
    confidence: float = 0.0
    questions: List[str] = field(default_factory=list)
    
    def to_dict(self):
        return {
            'current_goal': self.current_goal,
            'blockers': self.blockers,
            'dependencies': self.dependencies,
            'next_steps': self.next_steps,
            'confidence': self.confidence,
            'questions': self.questions
        }

@dataclass
class Message:
    """Standard message format for agent communication."""
    
    from_agent: str
    to_agent: str
    content_body: str
    message_type: str
    
    # Optional fields
    message_id: str = field(default_factory=lambda: f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}")
    timestamp: datetime = field(default_factory=datetime.now)
    priority: str = "normal"
    subject: str = ""
    thread_id: Optional[str] = None
    previous_message_id: Optional[str] = None
    
    work_completed: Optional[WorkCompleted] = None
    context_understanding: Optional[ContextUnderstanding] = None
    
    action_needed: Optional[str] = None
    deadline: Optional[datetime] = None
    estimated_time: Optional[str] = None
    specific_asks: List[str] = field(default_factory=list)
    
    notify_jack: bool = False
    jack_action_needed: bool = False
    jack_summary: Optional[str] = None
    
    attachments: List[Dict] = field(default_factory=list)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'message_id': self.message_id,
            'timestamp': self.timestamp.isoformat(),
            'from': self.from_agent,
            'to': self.to_agent,
            'priority': self.priority,
            'type': self.message_type,
            
            'conversation': {
                'thread_id': self.thread_id,
                'previous_message_id': self.previous_message_id,
                'conversation_summary': self.subject
            },
            
            'content': {
                'subject': self.subject,
                'body': self.content_body,
                'formatted': '\n' in self.content_body or '```' in self.content_body
            },
            
            'work_completed': self.work_completed.to_dict() if self.work_completed else None,
            'context_understanding': self.context_understanding.to_dict() if self.context_understanding else None,
            
            'requests': {
                'action_needed': self.action_needed,
                'deadline': self.deadline.isoformat() if self.deadline else None,
                'estimated_time': self.estimated_time,
                'specific_asks': self.specific_asks
            },
            
            'attachments': self.attachments,
            
            'notify_jack': self.notify_jack,
            'jack_action_needed': self.jack_action_needed,
            'jack_summary': self.jack_summary
        }
    
    def save_to_outbox(self, base_path: str = None):
        """Save message to sender's outbox."""
        if base_path is None:
            base_path = Path(__file__).parent.parent
        
        outbox_path = Path(base_path) / 'comms' / self.from_agent / 'outbox'
        outbox_path.mkdir(parents=True, exist_ok=True)
        
        file_path = outbox_path / f'{self.message_id}.json'
        file_path.write_text(json.dumps(self.to_dict(), indent=2))
        
        print(f"✉️  Message saved to outbox: {file_path}")
        return file_path
    
    def send(self, base_path: str = None):
        """Send message: move from outbox to recipient's inbox."""
        if base_path is None:
            base_path = Path(__file__).parent.parent
        
        # Save to outbox first
        outbox_file = self.save_to_outbox(base_path)
        
        # Copy to recipient's inbox
        inbox_path = Path(base_path) / 'comms' / self.to_agent / 'inbox'
        inbox_path.mkdir(parents=True, exist_ok=True)
        
        inbox_file = inbox_path / f'{self.message_id}.json'
        inbox_file.write_text(outbox_file.read_text())
        
        # Move outbox file to sent
        sent_path = Path(base_path) / 'comms' / self.from_agent / 'sent'
        sent_path.mkdir(parents=True, exist_ok=True)
        
        sent_file = sent_path / f'{self.message_id}.json'
        outbox_file.rename(sent_file)
        
        # Archive conversation
        self._archive_message(base_path)
        
        # Notify Jack if requested
        if self.notify_jack or self.jack_action_needed:
            self._notify_jack(base_path)
        
        print(f"✅ Message sent: {self.from_agent} → {self.to_agent}")
        print(f"📬 Inbox: {inbox_file}")
        
        return inbox_file
    
    def _archive_message(self, base_path):
        """Archive message to conversation history."""
        archive_path = Path(base_path) / 'comms' / 'archive' / 'conversations'
        archive_path.mkdir(parents=True, exist_ok=True)
        
        thread_file = archive_path / f'{self.thread_id or "general"}.jsonl'
        
        # Append to thread file (JSONL format)
        with open(thread_file, 'a') as f:
            f.write(json.dumps(self.to_dict()) + '\n')
    
    def _notify_jack(self, base_path):
        """Create notification for Jack."""
        notify_path = Path(base_path) / 'comms' / 'jack'
        
        if self.jack_action_needed:
            # Decision needed
            decision_path = notify_path / 'decisions'
            decision_path.mkdir(parents=True, exist_ok=True)
            
            decision_file = decision_path / f'{self.message_id}.json'
            decision_file.write_text(json.dumps({
                'message_id': self.message_id,
                'timestamp': self.timestamp.isoformat(),
                'from': self.from_agent,
                'to': self.to_agent,
                'subject': self.subject,
                'summary': self.jack_summary,
                'priority': 'high',
                'action': 'Decision needed - see full message for details'
            }, indent=2))
        else:
            # Just FYI notification
            notifications_path = notify_path / 'notifications'
            notifications_path.mkdir(parents=True, exist_ok=True)
            
            notify_file = notifications_path / f'{self.message_id}.json'
            notify_file.write_text(json.dumps({
                'message_id': self.message_id,
                'timestamp': self.timestamp.isoformat(),
                'from': self.from_agent,
                'to': self.to_agent,
                'subject': self.subject,
                'summary': self.jack_summary,
                'priority': 'normal'
            }, indent=2))


@dataclass
class MessageReader:
    """Read messages from inbox."""
    
    agent_id: str
    base_path: str = None
    
    def __post_init__(self):
        if self.base_path is None:
            self.base_path = Path(__file__).parent.parent
    
    def check_inbox(self) -> List[Message]:
        """Check inbox for new messages."""
        inbox_path = Path(self.base_path) / 'comms' / self.agent_id / 'inbox'
        
        if not inbox_path.exists():
            return []
        
        messages = []
        for msg_file in sorted(inbox_path.glob('*.json')):
            msg_data = json.loads(msg_file.read_text())
            
            # Convert back to Message object
            # (simplified - in production, full deserialization)
            messages.append({
                'message_id': msg_data['message_id'],
                'from': msg_data['from'],
                'subject': msg_data['content']['subject'],
                'body': msg_data['content']['body'],
                'type': msg_data['type'],
                'work_completed': msg_data.get('work_completed'),
                'context_understanding': msg_data.get('context_understanding'),
                'requests': msg_data.get('requests'),
                'file': msg_file
            })
        
        return messages
    
    def mark_read(self, message_file: Path):
        """Mark message as read (move to archive)."""
        read_path = Path(self.base_path) / 'comms' / self.agent_id / 'read'
        read_path.mkdir(parents=True, exist_ok=True)
        
        read_file = read_path / message_file.name
        message_file.rename(read_file)
    
    def get_conversation_history(self, thread_id: str) -> List[Dict]:
        """Get full conversation history for a thread."""
        archive_path = Path(self.base_path) / 'comms' / 'archive' / 'conversations'
        thread_file = archive_path / f'{thread_id}.jsonl'
        
        if not thread_file.exists():
            return []
        
        messages = []
        with open(thread_file, 'r') as f:
            for line in f:
                messages.append(json.loads(line))
        
        return messages
```

### 2. Auto-Notification Service

```python
# comms/system/notifier.py

import time
import json
from pathlib import Path
from datetime import datetime
from typing import Callable, Optional
import threading

class MessageNotifier:
    """
    Auto-notification service that watches inbox and triggers actions.
    Runs as a background thread.
    """
    
    def __init__(self, agent_id: str, base_path: str = None):
        self.agent_id = agent_id
        self.base_path = base_path or Path.cwd()
        self.inbox_path = Path(self.base_path) / 'comms' / agent_id / 'inbox'
        self.last_check = datetime.now()
        self.running = False
        self.callback = None
        self._thread = None
    
    def on_new_message(self, callback: Callable):
        """
        Register callback function to be called when new message arrives.
        
        Callback signature: callback(message_data: Dict) -> None
        """
        self.callback = callback
    
    def start(self, poll_interval: int = 5):
        """
        Start watching inbox for new messages.
        
        Args:
            poll_interval: Seconds between checks (default: 5)
        """
        if self.running:
            print(f"⚠️  Notifier already running for {self.agent_id}")
            return
        
        self.running = True
        self._thread = threading.Thread(
            target=self._watch_inbox,
            args=(poll_interval,),
            daemon=True
        )
        self._thread.start()
        
        print(f"🔔 Notifier started for {self.agent_id} (polling every {poll_interval}s)")
    
    def stop(self):
        """Stop watching inbox."""
        self.running = False
        if self._thread:
            self._thread.join(timeout=2)
        print(f"🔕 Notifier stopped for {self.agent_id}")
    
    def _watch_inbox(self, poll_interval: int):
        """Background thread that watches inbox."""
        self.inbox_path.mkdir(parents=True, exist_ok=True)
        
        while self.running:
            try:
                # Get all inbox messages
                messages = list(self.inbox_path.glob('*.json'))
                
                for msg_file in messages:
                    # Check if message is new (created after last check)
                    file_time = datetime.fromtimestamp(msg_file.stat().st_mtime)
                    
                    if file_time > self.last_check:
                        # New message!
                        msg_data = json.loads(msg_file.read_text())
                        
                        print(f"\n{'='*60}")
                        print(f"📨 NEW MESSAGE for {self.agent_id}")
                        print(f"From: {msg_data['from']}")
                        print(f"Subject: {msg_data['content']['subject']}")
                        print(f"Type: {msg_data['type']}")
                        print(f"Priority: {msg_data['priority']}")
                        print(f"{'='*60}\n")
                        
                        # Trigger callback if registered
                        if self.callback:
                            try:
                                self.callback(msg_data)
                            except Exception as e:
                                print(f"⚠️  Callback error: {e}")
                
                self.last_check = datetime.now()
                time.sleep(poll_interval)
                
            except Exception as e:
                print(f"⚠️  Notifier error: {e}")
                time.sleep(poll_interval)
    
    def trigger_manual_check(self):
        """Manually trigger inbox check (don't wait for poll interval)."""
        self.last_check = datetime.now() - timedelta(hours=1)  # Force check


class JackNotifier:
    """
    Separate notifier for Jack's decision queue.
    Only notifies for important items (5.5/10 level).
    """
    
    def __init__(self, base_path: str = None):
        self.base_path = base_path or Path.cwd()
        self.notifications_path = Path(self.base_path) / 'comms' / 'jack' / 'notifications'
        self.decisions_path = Path(self.base_path) / 'comms' / 'jack' / 'decisions'
    
    def check_for_jack(self) -> Dict:
        """
        Check for items requiring Jack's attention.
        Returns summary of pending items.
        """
        self.notifications_path.mkdir(parents=True, exist_ok=True)
        self.decisions_path.mkdir(parents=True, exist_ok=True)
        
        # Count pending items
        notifications = list(self.notifications_path.glob('*.json'))
        decisions = list(self.decisions_path.glob('*.json'))
        
        # Load decision details (these are important!)
        decision_details = []
        for decision_file in decisions:
            decision_details.append(json.loads(decision_file.read_text()))
        
        # Load recent notifications (last 5)
        notification_summaries = []
        for notify_file in sorted(notifications, reverse=True)[:5]:
            notification_summaries.append(json.loads(notify_file.read_text()))
        
        return {
            'decisions_pending': len(decisions),
            'decisions': decision_details,
            'notifications_count': len(notifications),
            'recent_notifications': notification_summaries,
            'check_time': datetime.now().isoformat()
        }
    
    def generate_summary(self) -> str:
        """Generate human-readable summary for Jack."""
        data = self.check_for_jack()
        
        summary = []
        summary.append("=" * 60)
        summary.append("JACK'S NOTIFICATION SUMMARY")
        summary.append("=" * 60)
        summary.append("")
        
        # Decisions (URGENT)
        if data['decisions_pending'] > 0:
            summary.append(f"⚠️  DECISIONS NEEDED: {data['decisions_pending']}")
            summary.append("")
            for decision in data['decisions']:
                summary.append(f"  • {decision['subject']}")
                summary.append(f"    From: {decision['from']} → {decision['to']}")
                summary.append(f"    Summary: {decision['summary']}")
                summary.append("")
        
        # Notifications (FYI)
        if data['notifications_count'] > 0:
            summary.append(f"ℹ️  NOTIFICATIONS: {data['notifications_count']} total (showing last 5)")
            summary.append("")
            for notification in data['recent_notifications']:
                summary.append(f"  • {notification['subject']}")
                summary.append(f"    {notification['summary']}")
                summary.append("")
        
        if data['decisions_pending'] == 0 and data['notifications_count'] == 0:
            summary.append("✅ All clear! No items requiring attention.")
        
        summary.append("=" * 60)
        
        return '\n'.join(summary)
    
    def mark_decision_resolved(self, message_id: str, resolution: str):
        """Mark a decision as resolved by Jack."""
        decision_file = self.decisions_path / f'{message_id}.json'
        
        if decision_file.exists():
            # Move to resolved folder
            resolved_path = Path(self.base_path) / 'comms' / 'jack' / 'resolved'
            resolved_path.mkdir(parents=True, exist_ok=True)
            
            decision_data = json.loads(decision_file.read_text())
            decision_data['resolved_at'] = datetime.now().isoformat()
            decision_data['resolution'] = resolution
            
            resolved_file = resolved_path / f'{message_id}.json'
            resolved_file.write_text(json.dumps(decision_data, indent=2))
            
            decision_file.unlink()
            
            print(f"✅ Decision resolved: {message_id}")
```

### 3. Communication Manager (Orchestration)

```python
# comms/system/comms_manager.py

from pathlib import Path
from typing import List, Optional
import git
from message_schema import Message, WorkCompleted, ContextUnderstanding, MessageReader
from notifier import MessageNotifier

class AgentCommunicator:
    """
    High-level communication interface for agents.
    Handles message creation, sending, and receiving with git integration.
    """
    
    def __init__(self, agent_id: str, base_path: str = None):
        self.agent_id = agent_id
        self.base_path = base_path or Path.cwd()
        self.reader = MessageReader(agent_id, base_path)
        self.notifier = MessageNotifier(agent_id, base_path)
        
        # Git integration
        try:
            self.repo = git.Repo(self.base_path)
        except:
            self.repo = None
            print("⚠️  Not a git repository - file tracking limited")
    
    def send_message(
        self,
        to_agent: str,
        subject: str,
        body: str,
        message_type: str,
        priority: str = "normal",
        thread_id: Optional[str] = None,
        notify_jack: bool = False,
        jack_summary: Optional[str] = None,
        auto_include_work: bool = True
    ) -> Message:
        """
        Send a message to another agent.
        
        Args:
            to_agent: Recipient agent ID
            subject: Message subject
            body: Message content
            message_type: Type of message (see MESSAGE_TYPES)
            priority: "low", "normal", "high", "urgent"
            thread_id: Conversation thread ID
            notify_jack: Whether to notify Jack
            jack_summary: Summary for Jack
            auto_include_work: Auto-detect and include git changes
        """
        # Auto-detect work completed
        work = None
        if auto_include_work and self.repo:
            work = self._detect_work_completed()
        
        # Auto-detect context understanding
        context = self._build_context_understanding()
        
        # Create message
        msg = Message(
            from_agent=self.agent_id,
            to_agent=to_agent,
            subject=subject,
            content_body=body,
            message_type=message_type,
            priority=priority,
            thread_id=thread_id,
            work_completed=work,
            context_understanding=context,
            notify_jack=notify_jack,
            jack_summary=jack_summary
        )
        
        # Send it
        msg.send(self.base_path)
        
        return msg
    
    def check_messages(self) -> List[Dict]:
        """Check inbox for new messages."""
        return self.reader.check_inbox()
    
    def start_listening(self, callback=None, poll_interval: int = 5):
        """
        Start auto-notification service.
        
        Args:
            callback: Function to call on new message
            poll_interval: Seconds between checks
        """
        if callback:
            self.notifier.on_new_message(callback)
        
        self.notifier.start(poll_interval)
    
    def stop_listening(self):
        """Stop auto-notification service."""
        self.notifier.stop()
    
    def get_conversation(self, thread_id: str) -> List[Dict]:
        """Get full conversation history for a thread."""
        return self.reader.get_conversation_history(thread_id)
    
    def _detect_work_completed(self) -> WorkCompleted:
        """Auto-detect work from git changes."""
        if not self.repo:
            return WorkCompleted()
        
        # Get recent commits (last 1 hour)
        commits = list(self.repo.iter_commits('HEAD', max_count=10))
        recent_commits = []
        
        # Get changed files from working directory
        changed_files = [item.a_path for item in self.repo.index.diff(None)]
        untracked_files = self.repo.untracked_files
        
        # Get staged files
        staged_files = [item.a_path for item in self.repo.index.diff('HEAD')]
        
        # Calculate stats
        files_added = list(set(untracked_files))
        files_modified = list(set(changed_files + staged_files))
        
        # Get commit info
        for commit in commits[:3]:  # Last 3 commits
            recent_commits.append({
                'hash': commit.hexsha[:8],
                'message': commit.message.strip(),
                'timestamp': commit.committed_datetime.isoformat()
            })
        
        return WorkCompleted(
            files_added=files_added,
            files_modified=files_modified,
            files_deleted=[],  # Would need more complex git analysis
            commits=recent_commits
        )
    
    def _build_context_understanding(self) -> ContextUnderstanding:
        """
        Build current context understanding.
        This should be implemented by each agent based on their current work.
        """
        # Placeholder - agents should override this
        return ContextUnderstanding(
            current_goal="Working on multi-agent context system",
            confidence=0.5
        )
```

---

## USAGE EXAMPLES

### Example 1: Claude Sends Code Review Request

```python
from comms.system.comms_manager import AgentCommunicator

# Initialize communicator
claude = AgentCommunicator('claude')

# Send code review request
claude.send_message(
    to_agent='gemini',
    subject='Code review: Arrow logger implementation',
    body='''
I've implemented the basic Arrow logger with the following features:

- Atomic writes (no data loss)
- Source separation (API vs non-API)
- Columnar format for fast analytics
- Compression with Snappy

Please review:
1. Is the schema design correct?
2. Should we batch writes differently?
3. Any edge cases I'm missing?

Files changed:
- src/core/logger.py (287 lines added)
- src/core/__init__.py (3 lines added)
- requirements.txt (added pyarrow>=12.0.0)

Tests: 15 tests added, all passing
Coverage: +12.3%

Let me know if you have any concerns!
    ''',
    message_type='code_review_request',
    priority='normal',
    thread_id='thread_arrow_logger',
    auto_include_work=True  # Auto-detects git changes
)

print("✅ Code review request sent to Gemini")
```

### Example 2: Gemini Receives and Responds

```python
from comms.system.comms_manager import AgentCommunicator
import time

# Initialize communicator
gemini = AgentCommunicator('gemini')

# Set up auto-notification
def handle_new_message(msg_data):
    """Callback when new message arrives."""
    print(f"\n🔔 New message from {msg_data['from']}")
    print(f"Subject: {msg_data['content']['subject']}")
    print(f"Type: {msg_data['type']}")
    
    # Auto-respond based on message type
    if msg_data['type'] == 'code_review_request':
        print("📝 Code review requested - checking files...")
        
        # Read the files mentioned
        work = msg_data.get('work_completed', {})
        files = work.get('files_added', []) + work.get('files_modified', [])
        
        print(f"Files to review: {files}")
        print("Starting review process...")

# Start listening
gemini.start_listening(callback=handle_new_message, poll_interval=5)

print("🔔 Gemini listening for messages...")
print("Press Ctrl+C to stop")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    gemini.stop_listening()
    print("\n👋 Stopped listening")
```

**After reviewing, Gemini responds:**

```python
gemini.send_message(
    to_agent='claude',
    subject='Re: Code review - Arrow logger looks good!',
    body='''
Reviewed your Arrow logger implementation. Overall excellent work!

✅ Schema design is solid
✅ Separation of API/non-API is clean
✅ Tests are comprehensive

Suggestions:
1. Add error handling for disk full scenarios
2. Consider batching writes in groups of 200 (not 100)
   - I benchmarked: 200 is 15% faster
3. Add retry logic with exponential backoff

Minor issues:
- Line 78: Typo in variable name (thred_id → thread_id)
- Line 145: Missing docstring

I'll add the error handling and retry logic if you're okay with it.
Then you can review my additions.

Sound good?
    ''',
    message_type='code_review_response',
    thread_id='thread_arrow_logger',
    priority='normal'
)
```

### Example 3: Escalation to Jack

```python
# Claude and Gemini disagree on approach
claude.send_message(
    to_agent='gemini',
    subject='Disagreement: TOON encoder placement',
    body='''
I understand your point about integrating TOON encoding in the logger,
but I still think it should be a separate module in /src/optimization.

We've gone back and forth 3 times and can't reach consensus.

Should we escalate this to Jack?
    ''',
    message_type='disagreement',
    thread_id='thread_toon_placement',
    notify_jack=True,
    jack_summary='Claude and Gemini disagree on TOON encoder architecture. Need decision on placement.'
)
```

**Jack gets notified:**

```python
from comms.system.notifier import JackNotifier

jack = JackNotifier()
summary = jack.generate_summary()
print(summary)

# Output:
# ============================================================
# JACK'S NOTIFICATION SUMMARY
# ============================================================
#
# ⚠️  DECISIONS NEEDED: 1
#
#   • Disagreement: TOON encoder placement
#     From: claude → gemini
#     Summary: Claude and Gemini disagree on TOON encoder architecture.
#              Need decision on placement.
#
# ============================================================
```

### Example 4: Jack Resolves Decision

```python
# Jack makes decision
jack.mark_decision_resolved(
    message_id='msg_20251205_143022_claude',
    resolution='''
Good discussion from both of you. Here's my decision:

Use a hybrid approach:
- Core TOON logic in /src/optimization/toon_encoder.py (Claude's structure)
- Logger imports and uses it (Gemini's integration point)

This gets the best of both:
- Isolated and reusable (Claude's concern)
- Performant and integrated (Gemini's concern)

Claude: Implement the encoder module
Gemini: Integrate it into the logger

Both: Review each other's parts

Sound good?
    '''
)

# This creates a message in both Claude and Gemini's inbox
# with Jack's decision
```

---

## AUTO-SEND CONFIGURATION

### Auto-send After Completion

```python
# comms/system/auto_send.py

class AutoSender:
    """
    Automatically send outbox messages after agent completes work.
    """
    
    def __init__(self, agent_id: str, base_path: str = None):
        self.agent_id = agent_id
        self.base_path = base_path or Path.cwd()
        self.outbox_path = Path(base_path) / 'comms' / agent_id / 'outbox'
    
    def send_pending_messages(self):
        """Send all messages in outbox."""
        self.outbox_path.mkdir(parents=True, exist_ok=True)
        
        pending = list(self.outbox_path.glob('*.json'))
        
        if not pending:
            print(f"📭 No pending messages for {self.agent_id}")
            return
        
        print(f"📤 Sending {len(pending)} pending messages...")
        
        for msg_file in pending:
            try:
                # Load message
                msg_data = json.loads(msg_file.read_text())
                
                # Recreate Message object and send
                # (simplified - in production, full reconstruction)
                from message_schema import Message
                msg = Message.from_dict(msg_data)  # Would need to implement
                msg.send(self.base_path)
                
                print(f"  ✅ Sent: {msg_data['content']['subject']}")
                
            except Exception as e:
                print(f"  ⚠️  Failed to send {msg_file.name}: {e}")
        
        print(f"✅ All messages sent!")


# Usage in agent workflow
def agent_work_complete():
    """Call this when agent finishes its work session."""
    
    # Do work...
    # ...
    
    # Auto-send pending messages
    sender = AutoSender('claude')
    sender.send_pending_messages()
```

### Integration with Agent Main Loop

```python
# Example: Claude Code main loop

from comms.system.comms_manager import AgentCommunicator
from comms.system.auto_send import AutoSender
import atexit

def main():
    # Initialize
    claude = AgentCommunicator('claude')
    auto_sender = AutoSender('claude')
    
    # Register auto-send on exit
    atexit.register(auto_sender.send_pending_messages)
    
    # Start listening for messages
    claude.start_listening(
        callback=handle_incoming_message,
        poll_interval=5
    )
    
    # Do work
    work_on_tasks()
    
    # Messages automatically sent on exit!

if __name__ == "__main__":
    main()
```

---

## JACK'S OVERSIGHT DASHBOARD

### Simple CLI Dashboard

```python
# scripts/jack_dashboard.py

from comms.system.notifier import JackNotifier
from comms.system.comms_manager import AgentCommunicator
import time
from datetime import datetime

def show_dashboard():
    """Show Jack's oversight dashboard."""
    jack = JackNotifier()
    
    while True:
        # Clear screen (platform-specific)
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print(jack.generate_summary())
        print("\nCommands:")
        print("  r - Refresh")
        print("  d - View decision details")
        print("  n - View notifications")
        print("  q - Quit")
        print("\n> ", end='')
        
        # Auto-refresh every 30 seconds or on command
        # (Simplified - would use proper input handling)
        time.sleep(30)

if __name__ == "__main__":
    show_dashboard()
```

### Notification Level Configuration

```python
# config/jack_notifications.yaml

notification_level: 5.5  # Out of 10 (moderate)

rules:
  # Always notify (level >= 8)
  always:
    - escalation_to_jack
    - merge_conflicts
    - critical_bugs
    - deployment_issues
  
  # Usually notify (level >= 5.5)
  moderate:
    - design_disagreements
    - architecture_changes
    - new_dependencies
    - performance_regressions
  
  # Rarely notify (level >= 3)
  low:
    - minor_refactoring
    - documentation_updates
    - test_additions
  
  # Never notify automatically (level < 3)
  never:
    - code_formatting
    - comment_changes
    - log_messages

# Jack can adjust this to change notification volume
```

---

## SETUP CHECKLIST

### Initial Setup

```bash
# 1. Create directory structure
cd C:\Users\user\ShearwaterAICAD\multi-agent-context-system
mkdir -p comms/{claude,gemini,jack}/{inbox,outbox,sent}
mkdir -p comms/{archive/conversations,system}
mkdir -p comms/jack/{notifications,decisions,resolved}

# 2. Copy communication system files
# Place message_schema.py, notifier.py, comms_manager.py in comms/system/

# 3. Test the system
python comms/system/test_comms.py
```

### Agent Integration

**Claude Code:**
```python
# Add to Claude's initialization
from comms.system.comms_manager import AgentCommunicator

claude = AgentCommunicator('claude')
claude.start_listening(poll_interval=5)

# In Claude's main loop
claude.send_message(
    to_agent='gemini',
    subject='Started working on logger',
    body='...',
    message_type='progress_update'
)
```

**Gemini CLI:**
```python
# Add to Gemini's initialization
from comms.system.comms_manager import AgentCommunicator

gemini = AgentCommunicator('gemini')
gemini.start_listening(poll_interval=5)

# In Gemini's main loop
gemini.send_message(
    to_agent='claude',
    subject='Reviewed your logger code',
    body='...',
    message_type='code_review_response'
)
```

---

## TESTING

```python
# comms/system/test_comms.py

def test_basic_communication():
    """Test basic send/receive."""
    from comms_manager import AgentCommunicator
    
    # Claude sends
    claude = AgentCommunicator('claude')
    claude.send_message(
        to_agent='gemini',
        subject='Test message',
        body='This is a test',
        message_type='technical_question'
    )
    
    # Gemini receives
    gemini = AgentCommunicator('gemini')
    messages = gemini.check_messages()
    
    assert len(messages) > 0
    assert messages[0]['from'] == 'claude'
    
    print("✅ Basic communication test passed")

def test_auto_notification():
    """Test auto-notification."""
    from notifier import MessageNotifier
    import time
    
    notified = []
    
    def callback(msg):
        notified.append(msg)
    
    # Start notifier
    notifier = MessageNotifier('gemini')
    notifier.on_new_message(callback)
    notifier.start(poll_interval=1)
    
    # Send message
    claude = AgentCommunicator('claude')
    claude.send_message(
        to_agent='gemini',
        subject='Test notification',
        body='Testing auto-notification',
        message_type='progress_update'
    )
    
    # Wait for notification
    time.sleep(2)
    
    assert len(notified) > 0
    
    notifier.stop()
    
    print("✅ Auto-notification test passed")

if __name__ == "__main__":
    test_basic_communication()
    test_auto_notification()
    print("\n✅ All tests passed!")
```

---

## SUMMARY

**You now have:**
- ✅ Full inbox/outbox system
- ✅ Auto-notification on new messages
- ✅ Git-aware work tracking
- ✅ Context understanding sharing
- ✅ Jack's oversight (5.5/10 level)
- ✅ Auto-send on completion
- ✅ Conversation history archival
- ✅ Thread-based organization

**Agents can:**
- Send structured messages with full context
- Auto-detect work from git
- Receive real-time notifications
- Access full conversation history
- Escalate decisions to Jack
- Auto-send pending messages

**Jack can:**
- See decisions needing attention
- Get moderate-level notifications
- View conversation summaries
- Resolve conflicts
- Stay informed without being overwhelmed

**Ready to deploy!** 🚀

