
PRIMARY:
- Redis pub/sub
- <10ms latency
- Push-based notifications

FALLBACK:
- File-based inbox/outbox
- Watchdog filesystem events
- No polling

MESSAGE CONTENT:
- Subject
- Body
- Work completed
- Context snapshot
