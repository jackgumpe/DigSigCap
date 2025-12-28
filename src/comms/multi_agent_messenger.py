from typing import List, Dict, Optional, Callable
import redis
import json
from datetime import datetime
from pathlib import Path
import threading
import time
import os

# Assuming a simple SQLite message archive is available or mocked
class MockMessageArchive:
    def __init__(self, agent_id="mock_archive"):
        self.agent_id = agent_id
        self.messages = []
        print(f"[{self.agent_id}] MockMessageArchive initialized.")

    def archive_message(self, message: Dict):
        # print(f"[{self.agent_id}] Mock archiving message: {message.get('message_id')}")
        self.messages.append(message)

    def get_conversation(self, agent1: str, agent2: str, limit=50):
        # Mock retrieval, very basic
        return [
            msg for msg in self.messages
            if (msg.get('from') == agent1 and msg.get('to') == agent2) or
               (msg.get('from') == agent2 and msg.get('to') == agent1)
        ][:limit]

# Import AgentRegistry (assuming it's in the same directory)
try:
    from .agent_registry import AgentRegistry
except ImportError:
    class AgentRegistry: # Mock if not available
        def __init__(self):
            pass
        def list_active_agents(self) -> List[Dict]: return [{"id": "claude"}, {"id": "gemini"}, {"id": "deepseek"}]
        def get_agent(self, agent_id: str) -> Optional[Dict]: 
            if agent_id == "claude": return {"id": "claude", "capabilities": ["code"]}
            if agent_id == "gemini": return {"id": "gemini", "capabilities": ["multimodal"]}
            return None
        def list_agents_with_capability(self, capability: str) -> List[Dict]:
            if capability == "code": return [{"id": "claude"}]
            if capability == "multimodal": return [{"id": "gemini"}]
            return []
    print("WARNING: Using MockAgentRegistry. Actual AgentRegistry not found.")


class MultiAgentMessenger:
    """
    Messaging system supporting N agents with unicast, multicast, broadcast.
    Leverages Redis for real-time communication and a MessageArchive for persistence.
    """
    
    def __init__(self, agent_id: str, registry: AgentRegistry, redis_host='localhost', redis_port=6379):
        self.agent_id = agent_id
        self.registry = registry
        
        try:
            self.redis = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
            self.redis.ping() # Test connection
        except redis.ConnectionError:
            print(f"ERROR: Cannot connect to Redis on {redis_host}:{redis_port}. Ensure Redis server is running.")
            raise
        
        # Initialize Message Archive
        self.message_archive = MockMessageArchive(agent_id=f"{agent_id}_archive") # Replace with actual MessageArchive

        # Subscribe to personal inbox + broadcast channel
        self.channels = [
            f'{agent_id}_inbox',
            'broadcast_all_agents'
        ]
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe(*self.channels)
        self._listener_thread = None

    def _wrap_message(self, content: Dict, recipients: List[str], broadcast=False) -> Dict:
        """Wrap content with metadata."""
        return {
            'message_id': f"msg_{datetime.now().timestamp()}_{self.agent_id}_{os.urandom(4).hex()}",
            'from': self.agent_id,
            'to': recipients if not broadcast else "broadcast",
            'broadcast': broadcast,
            'timestamp': datetime.now().isoformat(),
            'content': content
        }
    
    def _log_and_publish(self, channel: str, full_msg: Dict):
        """Archives message and publishes to Redis."""
        self.message_archive.archive_message(full_msg)
        self.redis.publish(channel, json.dumps(full_msg))

    def send_unicast(self, to_agent: str, message: Dict):
        """Send to single agent."""
        full_msg = self._wrap_message(message, recipients=[to_agent])
        self._log_and_publish(f'{to_agent}_inbox', full_msg)
        # print(f"[{self.agent_id}] Sent unicast to {to_agent}: {message.get('subject', 'No subject')}")
    
    def send_multicast(self, to_agents: List[str], message: Dict):
        """Send to multiple specific agents."""
        full_msg = self._wrap_message(message, recipients=to_agents)
        for agent_id in to_agents:
            self._log_and_publish(f'{agent_id}_inbox', full_msg)
        # print(f"[{self.agent_id}] Sent multicast to {to_agents}: {message.get('subject', 'No subject')}")
    
    def send_broadcast(self, message: Dict, exclude_self=True):
        """Send to all active agents."""
        agents = self.registry.list_active_agents()
        recipients = [a['id'] for a in agents if not (exclude_self and a['id'] == self.agent_id)]
        
        full_msg = self._wrap_message(message, recipients=recipients, broadcast=True)
        self._log_and_publish('broadcast_all_agents', full_msg)
        # print(f"[{self.agent_id}] Sent broadcast: {message.get('subject', 'No subject')}")
    
    def send_to_capability(self, capability: str, message: Dict):
        """Send to all agents with specific capability."""
        agents = self.registry.list_agents_with_capability(capability)
        to_agents_ids = [a['id'] for a in agents]
        if to_agents_ids:
            self.send_multicast(to_agents_ids, message)
            # print(f"[{self.agent_id}] Sent to capability '{capability}': {message.get('subject', 'No subject')}")
        else:
            print(f"[{self.agent_id}] No agents found with capability '{capability}'. Message not sent.")

    def start_listening(self, callback: Callable):
        """
        Starts a background thread to listen for incoming messages.
        Calls the provided callback function for each new message.
        """
        if self._listener_thread and self._listener_thread.is_alive():
            print(f"[{self.agent_id}] Listener already running.")
            return

        def listener_loop():
            # print(f"[{self.agent_id}] Listener thread started, subscribing to {self.channels}")
            for message in self.pubsub.listen():
                if message['type'] == 'message':
                    try:
                        msg_data = json.loads(message['data'])
                        # print(f"[{self.agent_id}] Raw message received on {message['channel']}: {msg_data}")
                        if msg_data['from'] != self.agent_id:  # Don't process own messages
                            self.message_archive.archive_message(msg_data) # Archive received message
                            callback(msg_data)
                    except json.JSONDecodeError:
                        print(f"[{self.agent_id}] Received non-JSON message on {message['channel']}: {message['data']}")
                    except Exception as e:
                        print(f"[{self.agent_id}] Error processing message: {e}")
                # else:
                    # print(f"[{self.agent_id}] Non-message type received: {message['type']}")
        
        self._listener_thread = threading.Thread(target=listener_loop, daemon=True)
        self._listener_thread.start()
        print(f"[{self.agent_id}] Listening for messages on {self.channels}...")
    
    def stop_listening(self):
        if self._listener_thread and self._listener_thread.is_alive():
            self.pubsub.unsubscribe()
            self.pubsub.close()
            # self._listener_thread.join() # Don't join daemon thread on shutdown
            print(f"[{self.agent_id}] Listener stopped.")

    # You might want methods to retrieve history directly from the archive
    def get_message_history(self, other_agent_id: str, limit: int = 50) -> List[Dict]:
        return self.message_archive.get_conversation(self.agent_id, other_agent_id, limit)

    def __del__(self):
        self.stop_listening()


# Example Usage (for testing this module independently)
if __name__ == '__main__':
    print("--- MultiAgentMessenger Test ---")
    
    # Ensure Redis is running: docker run -d -p 6379:6379 redis
    # (Or choco install redis / brew install redis and start)

    # Mock registry for standalone test
    class TestRegistry(AgentRegistry):
        def __init__(self):
            # Use a more robust path for the dummy config
            config_dir = Path('./temp_config')
            config_dir.mkdir(exist_ok=True)
            self.config_path = config_dir / 'agents.json'
            
            # For standalone test, ensure some agents exist
            if not self.config_path.exists():
                print(f"Creating dummy config at {self.config_path}.")
                dummy_default = {
                    "agents": [
                        {"id": "test_claude", "name": "Test Claude", "capabilities": ["code"], "active": True},
                        {"id": "test_gemini", "name": "Test Gemini", "capabilities": ["multimodal", "analysis"], "active": True},
                        {"id": "test_deepseek", "name": "Test DeepSeek", "capabilities": ["code", "reasoning"], "active": True}
                    ]
                }
                with open(self.config_path, "w") as f:
                    json.dump(dummy_default, f, indent=2)
                self.agents = {a['id']: a for a in dummy_default['agents']}
            else:
                self.agents = self._load_agents()
        
        def _load_agents(self):
            try:
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                    return {a['id']: a for a in config_data.get('agents', [])}
            except (FileNotFoundError, json.JSONDecodeError):
                print(f"Error loading agents from {self.config_path}. Using empty list.")
                return {}

        def list_active_agents(self) -> List[Dict]: return list(self.agents.values())
        def list_agents_with_capability(self, capability: str) -> List[Dict]:
            return [a for a in self.agents.values() if capability in a.get("capabilities", [])]


    registry = TestRegistry()
    
    # Agent A
    agent_a = MultiAgentMessenger("test_claude", registry)
    
    # Agent B
    agent_b = MultiAgentMessenger("test_gemini", registry)

    def agent_a_callback(message):
        print(f"\n[Agent A - {agent_a.agent_id}] Received: From={message['from']}, Subject={message['content'].get('subject')}")
        # print(f"Full message: {json.dumps(message, indent=2)}")

    def agent_b_callback(message):
        print(f"\n[Agent B - {agent_b.agent_id}] Received: From={message['from']}, Subject={message['content'].get('subject')}")
        # print(f"Full message: {json.dumps(message, indent=2)}")
        if "OCR_REQUEST" in message['content'].get('subject', ''):
            agent_b.send_unicast(message['from'], {
                "subject": f"OCR_RESPONSE to {message['content'].get('file_path', '')}",
                "body": "Mock OCR processing complete.",
                "request_id": message.get('message_id')
            })


    agent_a.start_listening(agent_a_callback)
    agent_b.start_listening(agent_b_callback)

    print("\n--- Sending test messages ---")
    time.sleep(1) # Give listeners a moment to start

    # Test Unicast
    print("\nSending unicast from A to B...")
    agent_a.send_unicast("test_gemini", {"subject": "Hello B", "body": "This is a direct message."})
    time.sleep(0.5)

    # Test Broadcast
    print("\nSending broadcast from A...")
    agent_a.send_broadcast({"subject": "System Announcement", "body": "All agents, please note important info."})
    time.sleep(0.5)

    # Test Multicast (A to B and DeepSeek)
    print("\nSending multicast from A to B and DeepSeek (capability 'code')...")
    agent_a.send_multicast(["test_gemini", "test_deepseek"], {"subject": "Multicast Test", "body": "This message is for specific agents."})
    time.sleep(0.5)

    # Test Send to Capability
    print("\nSending to agents with 'multimodal' capability (Gemini)...")
    agent_a.send_to_capability("multimodal", {"subject": "Check Multimodal capabilities", "body": "Can you process this image?"})
    time.sleep(0.5)
    
    print("\nSending an OCR request from A to B to simulate agent-to-agent interaction...")
    agent_a.send_unicast("test_gemini", {
        "subject": "OCR_REQUEST for image.png", 
        "body": "Please process this file.",
        "content": {"file_path": "/path/to/image.png"}
    })
    time.sleep(2) # Give agent B time to process and respond

    print("\n--- Test complete. Listeners will remain active. Press Ctrl+C to exit. ---")
    
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nExiting test script.")
    finally:
        agent_a.stop_listening()
        agent_b.stop_listening()
        # Clean up dummy config if created
        try:
            Path('./temp_config/agents.json').unlink(missing_ok=True)
            Path('./temp_config').rmdir()
        except OSError as e:
            print(f"Error cleaning up temp config: {e}")
