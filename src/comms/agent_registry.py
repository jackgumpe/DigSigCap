import json
from pathlib import Path
from typing import List, Dict, Optional

class AgentRegistry:
    """
    Central registry of all agents in the system.
    Agents can discover each other dynamically.
    """
    
    def __init__(self, config_path='C:/Dev/llm-research/config/agents.json'): # Updated path
        self.config_path = Path(config_path)
        self.agents = self._load_agents()
        
    def _load_agents(self) -> Dict[str, Dict]:
        """Load agent configurations from JSON."""
        if not self.config_path.exists():
            # Create default config
            default = {
                "agents": [
                    {
                        "id": "claude",
                        "name": "Claude Code",
                        "model": "claude-sonnet-4.5",
                        "provider": "anthropic",
                        "capabilities": ["code", "analysis", "general"],
                        "cost_per_1m_input": 3.00,
                        "cost_per_1m_output": 15.00,
                        "max_tokens": 8192,
                        "active": True
                    },
                    {
                        "id": "gemini",
                        "name": "Gemini CLI",
                        "model": "gemini-2.0-flash",
                        "provider": "google",
                        "capabilities": ["code", "multimodal", "general"],
                        "cost_per_1m_input": 0.075,
                        "cost_per_1m_output": 0.30,
                        "max_tokens": 8192,
                        "active": True
                    },
                    {
                        "id": "deepseek",
                        "name": "DeepSeek",
                        "model": "deepseek-chat",
                        "provider": "deepseek",
                        "capabilities": ["code", "reasoning", "general"],
                        "cost_per_1m_input": 0.56,
                        "cost_per_1m_output": 1.68,
                        "cache_hit_discount": 0.875,  # 87.5% off = $0.07/M
                        "max_tokens": 8192,
                        "active": True
                    }
                ]
            }
            # Ensure config directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            self.config_path.write_text(json.dumps(default, indent=2))
            return {a['id']: a for a in default['agents']}
        
        config = json.loads(self.config_path.read_text())
        return {a['id']: a for a in config['agents']}
    
    def get_agent(self, agent_id: str) -> Optional[Dict]:
        """Get agent configuration by ID."""
        return self.agents.get(agent_id)
    
    def list_active_agents(self) -> List[Dict]:
        """Get all active agents."""
        return [a for a in self.agents.values() if a.get('active', True)]
    
    def list_agents_with_capability(self, capability: str) -> List[Dict]:
        """Find agents with specific capability."""
        return [
            a for a in self.list_active_agents()
            if capability in a.get('capabilities', [])
        ]
    
    def add_agent(self, agent_config: Dict):
        """Dynamically add a new agent."""
        agent_id = agent_config['id']
        self.agents[agent_id] = agent_config
        self._save_agents()
    
    def remove_agent(self, agent_id: str):
        """Remove an agent from registry."""
        if agent_id in self.agents:
            del self.agents[agent_id]
            self._save_agents()
    
    def _save_agents(self):
        """Persist agent configurations."""
        config = {"agents": list(self.agents.values())}
        self.config_path.write_text(json.dumps(config, indent=2))
