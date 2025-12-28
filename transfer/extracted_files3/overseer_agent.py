#!/usr/bin/env python3
"""
OverseerAgent - JIHUB Central Orchestrator
==========================================
Manages task routing, error correction, and human-in-loop checkpoints.
Acts as the central nervous system for all agent communication.

Responsibilities:
- Route tasks to appropriate specialist agents
- Handle error recovery (retry, redirect, escalate)
- Enforce human checkpoints before costly operations
- Monitor agent health
- Log all agent communications
"""

import json
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
from pathlib import Path
import threading
from queue import Queue, Empty

from shl_protocol import (
    SHLMessage, SHLProtocol, SHLAction, SHLPriority, SHLStatus, SHLLogger
)


class AgentStatus(Enum):
    """Agent health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"


@dataclass
class AgentInfo:
    """Information about a registered agent."""
    name: str
    domain: str
    handler: Optional[Callable] = None
    status: AgentStatus = AgentStatus.UNKNOWN
    last_heartbeat: Optional[datetime] = None
    tasks_completed: int = 0
    tasks_failed: int = 0
    average_response_ms: float = 0.0
    
    def update_stats(self, success: bool, response_time_ms: int):
        """Update agent statistics."""
        if success:
            self.tasks_completed += 1
        else:
            self.tasks_failed += 1
        
        # Rolling average
        total = self.tasks_completed + self.tasks_failed
        self.average_response_ms = (
            (self.average_response_ms * (total - 1) + response_time_ms) / total
        )


@dataclass
class TaskContext:
    """Context for a task being processed."""
    task_id: str
    original_request: SHLMessage
    created_at: datetime
    retry_count: int = 0
    current_agent: Optional[str] = None
    status: str = "pending"
    history: List[SHLMessage] = field(default_factory=list)
    
    def add_to_history(self, message: SHLMessage):
        self.history.append(message)


class HumanCheckpoint:
    """Represents a point requiring human decision."""
    
    def __init__(
        self,
        task_id: str,
        reason: str,
        options: List[str],
        context: Dict[str, Any]
    ):
        self.task_id = task_id
        self.reason = reason
        self.options = options
        self.context = context
        self.created_at = datetime.utcnow()
        self.resolved = False
        self.decision: Optional[str] = None
        self.resolved_at: Optional[datetime] = None
    
    def resolve(self, decision: str):
        """Record human decision."""
        self.decision = decision
        self.resolved = True
        self.resolved_at = datetime.utcnow()


class OverseerAgent:
    """
    Central orchestrator for JIHUB agent system.
    Routes tasks, handles errors, manages human checkpoints.
    """
    
    MAX_RETRIES = 3
    BACKOFF_BASE_MS = 1000
    HEALTH_CHECK_INTERVAL_S = 30
    API_COST_ALERT_THRESHOLD = 10.0  # dollars
    
    def __init__(
        self,
        db_path: str = "./jihub.duckdb",
        log_path: str = "./shl_audit.jsonl"
    ):
        self.db_path = db_path
        self.logger = SHLLogger(log_path)
        
        # Agent registry
        self.agents: Dict[str, AgentInfo] = {}
        
        # Task management
        self.active_tasks: Dict[str, TaskContext] = {}
        self.task_queue: Queue = Queue()
        
        # Human checkpoints
        self.pending_checkpoints: Dict[str, HumanCheckpoint] = {}
        
        # API cost tracking
        self.api_costs: Dict[str, float] = {}
        self.total_api_cost = 0.0
        
        # Thread control
        self.running = False
        self._worker_thread: Optional[threading.Thread] = None
        self._health_thread: Optional[threading.Thread] = None
        
        # Register self
        self._register_default_agents()
    
    def _register_default_agents(self):
        """Register the default specialist agents."""
        default_agents = [
            AgentInfo(name="Overseer", domain="orchestration"),
            AgentInfo(name="ResumeAgent", domain="resume_transformation"),
            AgentInfo(name="ScraperAgent", domain="job_posting_collection"),
            AgentInfo(name="FieldIntelAgent", domain="media_processing"),
            AgentInfo(name="AnalystAgent", domain="predictions_and_scoring"),
            AgentInfo(name="ReportAgent", domain="assessment_generation"),
        ]
        
        for agent in default_agents:
            self.agents[agent.name] = agent
    
    def register_agent(
        self,
        name: str,
        domain: str,
        handler: Optional[Callable] = None
    ):
        """Register a specialist agent."""
        self.agents[name] = AgentInfo(
            name=name,
            domain=domain,
            handler=handler,
            status=AgentStatus.HEALTHY,
            last_heartbeat=datetime.utcnow()
        )
        print(f"[Overseer] Registered agent: {name} ({domain})")
    
    def route_task(self, task_type: str) -> Optional[str]:
        """Determine which agent should handle a task type."""
        routing = {
            'transform': 'ResumeAgent',
            'parse_resume': 'ResumeAgent',
            'scrape': 'ScraperAgent',
            'scrape_jobs': 'ScraperAgent',
            'process_photo': 'FieldIntelAgent',
            'process_audio': 'FieldIntelAgent',
            'process_video': 'FieldIntelAgent',
            'transcribe': 'FieldIntelAgent',
            'analyze': 'AnalystAgent',
            'predict': 'AnalystAgent',
            'score': 'AnalystAgent',
            'generate_report': 'ReportAgent',
            'export': 'ReportAgent',
        }
        
        return routing.get(task_type)
    
    def submit_task(
        self,
        task_type: str,
        input_ref: str,
        priority: SHLPriority = SHLPriority.NORMAL,
        deadline: Optional[str] = None,
        requires_human_approval: bool = False
    ) -> str:
        """Submit a new task for processing."""
        
        target_agent = self.route_task(task_type)
        if not target_agent:
            raise ValueError(f"Unknown task type: {task_type}")
        
        request = SHLProtocol.create_request(
            from_agent='Overseer',
            to_agent=target_agent,
            task_type=task_type,
            input_ref=input_ref,
            priority=priority,
            deadline=deadline
        )
        
        # Create task context
        context = TaskContext(
            task_id=request.task_id,
            original_request=request,
            created_at=datetime.utcnow(),
            current_agent=target_agent
        )
        context.add_to_history(request)
        
        self.active_tasks[request.task_id] = context
        self.logger.log(request)
        
        # Check if human approval needed
        if requires_human_approval:
            self._create_checkpoint(
                request.task_id,
                f"Approval required for {task_type} task",
                ["approve", "reject", "modify"]
            )
            return request.task_id
        
        # Queue for processing
        self.task_queue.put(request)
        
        print(f"[Overseer] Task submitted: {request.task_id} -> {target_agent}")
        return request.task_id
    
    def _create_checkpoint(
        self,
        task_id: str,
        reason: str,
        options: List[str]
    ):
        """Create a human checkpoint."""
        context = self.active_tasks.get(task_id)
        
        checkpoint = HumanCheckpoint(
            task_id=task_id,
            reason=reason,
            options=options,
            context=context.original_request.to_dict() if context else {}
        )
        
        self.pending_checkpoints[task_id] = checkpoint
        
        # Create SHL message
        intervention = SHLProtocol.create_human_intervention(
            from_agent='Overseer',
            task_id=task_id,
            reason=reason,
            options=options
        )
        
        self.logger.log(intervention)
        print(f"[Overseer] Human checkpoint created: {task_id}")
        print(f"           Reason: {reason}")
        print(f"           Options: {options}")
    
    def resolve_checkpoint(self, task_id: str, decision: str) -> bool:
        """Resolve a pending human checkpoint."""
        checkpoint = self.pending_checkpoints.get(task_id)
        
        if not checkpoint:
            print(f"[Overseer] No pending checkpoint for task: {task_id}")
            return False
        
        if decision not in checkpoint.options:
            print(f"[Overseer] Invalid decision: {decision}")
            return False
        
        checkpoint.resolve(decision)
        del self.pending_checkpoints[task_id]
        
        # Resume task if approved
        if decision == 'approve':
            context = self.active_tasks.get(task_id)
            if context:
                self.task_queue.put(context.original_request)
                print(f"[Overseer] Task resumed: {task_id}")
        elif decision == 'reject':
            self._cancel_task(task_id, "Rejected by human")
        
        return True
    
    def handle_response(self, response: SHLMessage):
        """Handle a response from a specialist agent."""
        self.logger.log(response)
        
        context = self.active_tasks.get(response.task_id)
        if not context:
            print(f"[Overseer] Warning: Response for unknown task {response.task_id}")
            return
        
        context.add_to_history(response)
        
        if response.action == SHLAction.RESPONSE:
            if response.status == SHLStatus.SUCCESS:
                self._complete_task(response.task_id, response)
            elif response.status == SHLStatus.FAILED:
                self._handle_failure(response)
            elif response.status == SHLStatus.RETRY:
                self._schedule_retry(response)
        
        elif response.action == SHLAction.ERROR:
            self._handle_error(response)
        
        # Update agent stats
        agent = self.agents.get(response.agent_from)
        if agent:
            success = response.status == SHLStatus.SUCCESS if response.status else False
            agent.update_stats(success, response.processing_time_ms or 0)
    
    def _complete_task(self, task_id: str, response: SHLMessage):
        """Mark task as completed."""
        context = self.active_tasks.get(task_id)
        if context:
            context.status = "completed"
            print(f"[Overseer] Task completed: {task_id}")
            print(f"           Output: {response.output_ref}")
            print(f"           Confidence: {response.confidence}")
    
    def _handle_failure(self, response: SHLMessage):
        """Handle a failed task."""
        context = self.active_tasks.get(response.task_id)
        if not context:
            return
        
        if context.retry_count < self.MAX_RETRIES:
            self._schedule_retry(response)
        else:
            context.status = "failed"
            self._create_checkpoint(
                response.task_id,
                f"Task failed after {self.MAX_RETRIES} retries",
                ["retry", "redirect", "cancel"]
            )
    
    def _handle_error(self, error: SHLMessage):
        """Handle an error from an agent."""
        print(f"[Overseer] Error from {error.agent_from}: {error.error_code}")
        print(f"           Message: {error.error_message}")
        
        context = self.active_tasks.get(error.task_id)
        if not context:
            return
        
        if error.requires_human:
            self._create_checkpoint(
                error.task_id,
                f"Error requires human intervention: {error.error_message}",
                ["retry", "redirect", "cancel", "ignore"]
            )
        elif error.retry_possible and context.retry_count < self.MAX_RETRIES:
            self._schedule_retry(error)
        else:
            context.status = "failed"
            print(f"[Overseer] Task failed permanently: {error.task_id}")
    
    def _schedule_retry(self, message: SHLMessage):
        """Schedule a task retry with exponential backoff."""
        context = self.active_tasks.get(message.task_id)
        if not context:
            return
        
        context.retry_count += 1
        
        # Exponential backoff with jitter
        import random
        delay_ms = self.BACKOFF_BASE_MS * (2 ** context.retry_count)
        delay_ms += random.randint(0, 500)  # jitter
        
        print(f"[Overseer] Scheduling retry #{context.retry_count} for {message.task_id}")
        print(f"           Delay: {delay_ms}ms")
        
        # In production, use proper async scheduling
        time.sleep(delay_ms / 1000)
        self.task_queue.put(context.original_request)
    
    def _cancel_task(self, task_id: str, reason: str):
        """Cancel a task."""
        context = self.active_tasks.get(task_id)
        if context:
            context.status = "cancelled"
            print(f"[Overseer] Task cancelled: {task_id}")
            print(f"           Reason: {reason}")
    
    def track_api_cost(
        self,
        api_name: str,
        cost: float,
        task_id: Optional[str] = None
    ):
        """Track API usage costs."""
        self.api_costs[api_name] = self.api_costs.get(api_name, 0) + cost
        self.total_api_cost += cost
        
        if self.total_api_cost >= self.API_COST_ALERT_THRESHOLD:
            print(f"[Overseer] ⚠️  API cost alert: ${self.total_api_cost:.2f}")
            
            # Create checkpoint for cost approval
            self._create_checkpoint(
                task_id or "cost_alert",
                f"API costs have reached ${self.total_api_cost:.2f}",
                ["continue", "pause", "switch_to_local"]
            )
    
    def get_agent_health(self) -> Dict[str, Dict]:
        """Get health status of all agents."""
        return {
            name: {
                'status': agent.status.value,
                'last_heartbeat': agent.last_heartbeat.isoformat() if agent.last_heartbeat else None,
                'tasks_completed': agent.tasks_completed,
                'tasks_failed': agent.tasks_failed,
                'average_response_ms': agent.average_response_ms
            }
            for name, agent in self.agents.items()
        }
    
    def get_pending_checkpoints(self) -> List[Dict]:
        """Get all pending human checkpoints."""
        return [
            {
                'task_id': cp.task_id,
                'reason': cp.reason,
                'options': cp.options,
                'created_at': cp.created_at.isoformat()
            }
            for cp in self.pending_checkpoints.values()
        ]
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get status of a specific task."""
        context = self.active_tasks.get(task_id)
        if not context:
            return None
        
        return {
            'task_id': task_id,
            'status': context.status,
            'retry_count': context.retry_count,
            'current_agent': context.current_agent,
            'created_at': context.created_at.isoformat(),
            'history_length': len(context.history)
        }
    
    def print_status(self):
        """Print current system status."""
        print("\n" + "=" * 60)
        print("  JIHUB Overseer Status")
        print("=" * 60)
        
        print(f"\n📊 Tasks:")
        print(f"   Active: {len(self.active_tasks)}")
        print(f"   Queued: {self.task_queue.qsize()}")
        
        print(f"\n🚨 Pending Checkpoints: {len(self.pending_checkpoints)}")
        for cp in self.pending_checkpoints.values():
            print(f"   - {cp.task_id}: {cp.reason}")
        
        print(f"\n💰 API Costs: ${self.total_api_cost:.4f}")
        for api, cost in self.api_costs.items():
            print(f"   - {api}: ${cost:.4f}")
        
        print(f"\n🤖 Agent Health:")
        for name, agent in self.agents.items():
            status_icon = "✓" if agent.status == AgentStatus.HEALTHY else "!"
            print(f"   [{status_icon}] {name}: {agent.tasks_completed} completed, {agent.tasks_failed} failed")
        
        print("=" * 60)


# CLI interface
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="JIHUB Overseer Agent")
    parser.add_argument('--status', action='store_true', help='Show system status')
    parser.add_argument('--submit', type=str, help='Submit a task (format: type:input_ref)')
    parser.add_argument('--resolve', type=str, help='Resolve checkpoint (format: task_id:decision)')
    parser.add_argument('--demo', action='store_true', help='Run demo')
    
    args = parser.parse_args()
    
    overseer = OverseerAgent()
    
    if args.status:
        overseer.print_status()
    
    elif args.submit:
        parts = args.submit.split(':')
        if len(parts) >= 2:
            task_id = overseer.submit_task(parts[0], ':'.join(parts[1:]))
            print(f"Submitted task: {task_id}")
        else:
            print("Invalid format. Use: type:input_ref")
    
    elif args.resolve:
        parts = args.resolve.split(':')
        if len(parts) == 2:
            success = overseer.resolve_checkpoint(parts[0], parts[1])
            print(f"Resolved: {success}")
        else:
            print("Invalid format. Use: task_id:decision")
    
    elif args.demo:
        print("[Demo] Starting Overseer demo...")
        
        # Submit some tasks
        t1 = overseer.submit_task('transform', 'file:resume.pdf', requires_human_approval=True)
        t2 = overseer.submit_task('scrape', 'indeed:software_engineer:miami')
        
        # Simulate responses
        response = SHLProtocol.create_response(
            overseer.active_tasks[t2].original_request,
            SHLStatus.SUCCESS,
            'duckdb:jobs:123',
            confidence=0.95,
            processing_time_ms=2500
        )
        overseer.handle_response(response)
        
        # Show status
        overseer.print_status()
        
        # Resolve checkpoint
        overseer.resolve_checkpoint(t1, 'approve')
        overseer.print_status()
    
    else:
        overseer.print_status()
