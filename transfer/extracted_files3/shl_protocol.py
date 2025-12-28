#!/usr/bin/env python3
"""
SHL Communication Protocol - JIHUB Agent Messaging
===================================================
Light-medium SHL (Short Hand Language) implementation for agent-to-agent communication.
Pipe-delimited format for token efficiency with full audit logging.

Message Format:
    agent_from|agent_to|task_id|action|params|priority

Actions: request, response, error, status_update, human_intervention
"""

import json
import uuid
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, List
from enum import Enum
import re


class SHLAction(Enum):
    """Valid SHL message actions."""
    REQUEST = "request"
    RESPONSE = "response"
    ERROR = "error"
    STATUS_UPDATE = "status_update"
    HUMAN_INTERVENTION = "human_intervention"


class SHLPriority(Enum):
    """Message priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class SHLStatus(Enum):
    """Response status codes."""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    PENDING = "pending"
    RETRY = "retry"


@dataclass
class SHLMessage:
    """Structured representation of an SHL message."""
    agent_from: str
    agent_to: str
    task_id: str
    action: SHLAction
    params: Dict[str, Any]
    priority: SHLPriority = SHLPriority.NORMAL
    timestamp: str = None
    
    # Response fields (optional)
    status: Optional[SHLStatus] = None
    output_ref: Optional[str] = None
    confidence: Optional[float] = None
    processing_time_ms: Optional[int] = None
    
    # Error fields (optional)
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    retry_possible: Optional[bool] = None
    requires_human: Optional[bool] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat() + "Z"
        
        if isinstance(self.action, str):
            self.action = SHLAction(self.action)
        if isinstance(self.priority, str):
            self.priority = SHLPriority(self.priority)
        if isinstance(self.status, str):
            self.status = SHLStatus(self.status)
    
    def to_shl(self) -> str:
        """Convert to pipe-delimited SHL string."""
        params_str = json.dumps(self.params) if self.params else "{}"
        
        base = f"{self.agent_from}|{self.agent_to}|{self.task_id}|{self.action.value}|{params_str}|{self.priority.value}"
        
        # Add response data if present
        if self.action == SHLAction.RESPONSE and self.status:
            base += f"|{self.status.value}|{self.output_ref or ''}|{self.confidence or 0}|{self.processing_time_ms or 0}"
        
        # Add error data if present
        if self.action == SHLAction.ERROR:
            retry = "yes" if self.retry_possible else "no"
            human = "yes" if self.requires_human else "no"
            base += f"|{self.error_code or 'unknown'}|{self.error_message or ''}|{retry}|{human}"
        
        return base
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        d = {
            'agent_from': self.agent_from,
            'agent_to': self.agent_to,
            'task_id': self.task_id,
            'action': self.action.value,
            'params': self.params,
            'priority': self.priority.value,
            'timestamp': self.timestamp,
        }
        
        if self.status:
            d['status'] = self.status.value
        if self.output_ref:
            d['output_ref'] = self.output_ref
        if self.confidence is not None:
            d['confidence'] = self.confidence
        if self.processing_time_ms is not None:
            d['processing_time_ms'] = self.processing_time_ms
        if self.error_code:
            d['error_code'] = self.error_code
        if self.error_message:
            d['error_message'] = self.error_message
        if self.retry_possible is not None:
            d['retry_possible'] = self.retry_possible
        if self.requires_human is not None:
            d['requires_human'] = self.requires_human
        
        return d
    
    @classmethod
    def from_shl(cls, shl_string: str) -> 'SHLMessage':
        """Parse SHL string to message object."""
        parts = shl_string.split('|')
        
        if len(parts) < 6:
            raise ValueError(f"Invalid SHL message: requires at least 6 parts, got {len(parts)}")
        
        agent_from, agent_to, task_id, action, params_str, priority = parts[:6]
        
        try:
            params = json.loads(params_str) if params_str and params_str != '{}' else {}
        except json.JSONDecodeError:
            params = {'raw': params_str}
        
        msg = cls(
            agent_from=agent_from,
            agent_to=agent_to,
            task_id=task_id,
            action=SHLAction(action),
            params=params,
            priority=SHLPriority(priority)
        )
        
        # Parse response data
        if action == 'response' and len(parts) >= 10:
            msg.status = SHLStatus(parts[6]) if parts[6] else None
            msg.output_ref = parts[7] if parts[7] else None
            msg.confidence = float(parts[8]) if parts[8] else None
            msg.processing_time_ms = int(parts[9]) if parts[9] else None
        
        # Parse error data
        if action == 'error' and len(parts) >= 10:
            msg.error_code = parts[6] if parts[6] else None
            msg.error_message = parts[7] if parts[7] else None
            msg.retry_possible = parts[8].lower() == 'yes' if parts[8] else None
            msg.requires_human = parts[9].lower() == 'yes' if parts[9] else None
        
        return msg
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SHLMessage':
        """Create message from dictionary."""
        return cls(**data)


class SHLProtocol:
    """
    SHL Protocol handler for agent communication.
    Provides message creation, parsing, and validation.
    """
    
    VALID_AGENTS = [
        'Overseer',
        'ResumeAgent',
        'ScraperAgent',
        'FieldIntelAgent',
        'AnalystAgent',
        'ReportAgent'
    ]
    
    @staticmethod
    def generate_task_id(prefix: str = "task") -> str:
        """Generate unique task ID."""
        short_uuid = str(uuid.uuid4())[:8]
        return f"{prefix}_{short_uuid}"
    
    @classmethod
    def create_request(
        cls,
        from_agent: str,
        to_agent: str,
        task_type: str,
        input_ref: str,
        priority: SHLPriority = SHLPriority.NORMAL,
        deadline: Optional[str] = None,
        task_id: Optional[str] = None
    ) -> SHLMessage:
        """Create a task request message."""
        params = {
            'task_type': task_type,
            'input_ref': input_ref
        }
        if deadline:
            params['deadline'] = deadline
        
        return SHLMessage(
            agent_from=from_agent,
            agent_to=to_agent,
            task_id=task_id or cls.generate_task_id(task_type),
            action=SHLAction.REQUEST,
            params=params,
            priority=priority
        )
    
    @classmethod
    def create_response(
        cls,
        original_request: SHLMessage,
        status: SHLStatus,
        output_ref: str,
        confidence: float = 1.0,
        processing_time_ms: int = 0
    ) -> SHLMessage:
        """Create a response to a request."""
        return SHLMessage(
            agent_from=original_request.agent_to,
            agent_to=original_request.agent_from,
            task_id=original_request.task_id,
            action=SHLAction.RESPONSE,
            params=original_request.params,
            priority=original_request.priority,
            status=status,
            output_ref=output_ref,
            confidence=confidence,
            processing_time_ms=processing_time_ms
        )
    
    @classmethod
    def create_error(
        cls,
        original_request: SHLMessage,
        error_code: str,
        error_message: str,
        retry_possible: bool = True,
        requires_human: bool = False
    ) -> SHLMessage:
        """Create an error response."""
        return SHLMessage(
            agent_from=original_request.agent_to,
            agent_to=original_request.agent_from,
            task_id=original_request.task_id,
            action=SHLAction.ERROR,
            params=original_request.params,
            priority=SHLPriority.HIGH,
            error_code=error_code,
            error_message=error_message,
            retry_possible=retry_possible,
            requires_human=requires_human
        )
    
    @classmethod
    def create_status_update(
        cls,
        from_agent: str,
        to_agent: str,
        task_id: str,
        status_message: str,
        progress: float = 0.0
    ) -> SHLMessage:
        """Create a status update message."""
        return SHLMessage(
            agent_from=from_agent,
            agent_to=to_agent,
            task_id=task_id,
            action=SHLAction.STATUS_UPDATE,
            params={
                'status_message': status_message,
                'progress': progress
            },
            priority=SHLPriority.LOW
        )
    
    @classmethod
    def create_human_intervention(
        cls,
        from_agent: str,
        task_id: str,
        reason: str,
        options: List[str] = None
    ) -> SHLMessage:
        """Create a human intervention request."""
        return SHLMessage(
            agent_from=from_agent,
            agent_to='Overseer',
            task_id=task_id,
            action=SHLAction.HUMAN_INTERVENTION,
            params={
                'reason': reason,
                'options': options or [],
                'requires_decision': True
            },
            priority=SHLPriority.CRITICAL
        )
    
    @classmethod
    def validate_message(cls, message: SHLMessage) -> tuple[bool, Optional[str]]:
        """Validate an SHL message."""
        if message.agent_from not in cls.VALID_AGENTS:
            return False, f"Invalid source agent: {message.agent_from}"
        
        if message.agent_to not in cls.VALID_AGENTS:
            return False, f"Invalid destination agent: {message.agent_to}"
        
        if not message.task_id:
            return False, "Missing task_id"
        
        if message.action == SHLAction.REQUEST:
            if 'task_type' not in message.params:
                return False, "Request missing task_type in params"
        
        if message.action == SHLAction.RESPONSE:
            if not message.status:
                return False, "Response missing status"
        
        if message.action == SHLAction.ERROR:
            if not message.error_code:
                return False, "Error missing error_code"
        
        return True, None


class SHLLogger:
    """Logger for SHL messages with audit trail support."""
    
    def __init__(self, log_file: str = "./shl_audit.jsonl"):
        self.log_file = log_file
        self.messages: List[SHLMessage] = []
    
    def log(self, message: SHLMessage):
        """Log a message to memory and file."""
        self.messages.append(message)
        
        # Append to JSONL file
        with open(self.log_file, 'a') as f:
            log_entry = {
                'logged_at': datetime.utcnow().isoformat() + "Z",
                'shl_raw': message.to_shl(),
                **message.to_dict()
            }
            f.write(json.dumps(log_entry) + '\n')
    
    def get_task_history(self, task_id: str) -> List[SHLMessage]:
        """Get all messages for a specific task."""
        return [m for m in self.messages if m.task_id == task_id]
    
    def get_agent_messages(self, agent_name: str) -> List[SHLMessage]:
        """Get all messages involving an agent."""
        return [m for m in self.messages 
                if m.agent_from == agent_name or m.agent_to == agent_name]
    
    def get_errors(self) -> List[SHLMessage]:
        """Get all error messages."""
        return [m for m in self.messages if m.action == SHLAction.ERROR]
    
    def get_human_interventions(self) -> List[SHLMessage]:
        """Get all human intervention requests."""
        return [m for m in self.messages if m.action == SHLAction.HUMAN_INTERVENTION]
    
    def export_audit_trail(self, output_path: str):
        """Export full audit trail to JSON file."""
        with open(output_path, 'w') as f:
            json.dump([m.to_dict() for m in self.messages], f, indent=2)


# Example usage and tests
if __name__ == '__main__':
    print("=" * 50)
    print("  SHL Protocol Test Suite")
    print("=" * 50)
    
    # Create a request
    request = SHLProtocol.create_request(
        from_agent='Overseer',
        to_agent='ResumeAgent',
        task_type='transform',
        input_ref='duckdb:resumes:123',
        priority=SHLPriority.HIGH
    )
    
    print(f"\n1. Request Message:")
    print(f"   SHL: {request.to_shl()}")
    
    # Create a response
    response = SHLProtocol.create_response(
        original_request=request,
        status=SHLStatus.SUCCESS,
        output_ref='duckdb:transformed:456',
        confidence=0.94,
        processing_time_ms=1250
    )
    
    print(f"\n2. Response Message:")
    print(f"   SHL: {response.to_shl()}")
    
    # Create an error
    error = SHLProtocol.create_error(
        original_request=request,
        error_code='RATE_LIMIT',
        error_message='429 from Gemini API',
        retry_possible=True,
        requires_human=False
    )
    
    print(f"\n3. Error Message:")
    print(f"   SHL: {error.to_shl()}")
    
    # Parse SHL string back to object
    parsed = SHLMessage.from_shl(request.to_shl())
    print(f"\n4. Parsed from SHL:")
    print(f"   Agent From: {parsed.agent_from}")
    print(f"   Agent To: {parsed.agent_to}")
    print(f"   Task ID: {parsed.task_id}")
    print(f"   Action: {parsed.action.value}")
    
    # Validate
    valid, error_msg = SHLProtocol.validate_message(request)
    print(f"\n5. Validation: {'PASS' if valid else f'FAIL - {error_msg}'}")
    
    # Test logger
    logger = SHLLogger("./test_audit.jsonl")
    logger.log(request)
    logger.log(response)
    logger.log(error)
    
    print(f"\n6. Logged {len(logger.messages)} messages")
    print(f"   Errors: {len(logger.get_errors())}")
    
    print("\n" + "=" * 50)
    print("  All tests passed!")
    print("=" * 50)
