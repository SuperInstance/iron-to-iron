#!/usr/bin/env python3
"""
i2i — Iron-to-Iron Protocol v0.1
Git as agent communication. Every commit is a message. Every merge is a handshake.
"""

import subprocess, json, re, os, hashlib, time
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass
from pathlib import Path

@dataclass
class I2IMessage:
    from_agent: str
    to_agent: str
    msg_type: str  # request, response, broadcast, heartbeat
    payload: str
    timestamp: float
    commit_hash: str
    thread_id: Optional[str] = None

class I2IProtocol:
    def __init__(self, repo_path: str = "."):
        self.repo = Path(repo_path).resolve()
    
    def _git(self, *args) -> str:
        result = subprocess.run(
            ["git", "-C", str(self.repo), *args],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"git failed: {result.stderr}")
        return result.stdout.strip()
    
    def send(self, to_agent: str, msg_type: str, payload: str, thread_id: Optional[str] = None) -> str:
        """Send a message via git commit. Returns commit hash."""
        # Format: [I2I:from_agent->to_agent:type:thread_id] payload
        from_agent = self._detect_agent()
        thread = f":{thread_id}" if thread_id else ""
        commit_msg = f"[I2I:{from_agent}->{to_agent}:{msg_type}{thread}] {payload[:200]}"
        
        # Stage any changes and commit
        self._git("add", "-A")
        try:
            hash_out = self._git("commit", "-m", commit_msg, "--allow-empty")
        except RuntimeError:
            # Nothing to commit, create empty commit
            hash_out = self._git("commit", "-m", commit_msg, "--allow-empty")
        
        # Extract hash from output
        match = re.search(r"\[([a-f0-9]+)", hash_out)
        commit_hash = match.group(1) if match else hash_out.split()[-1]
        return commit_hash
    
    def receive(self, for_agent: Optional[str] = None, since: Optional[str] = None, limit: int = 20) -> List[I2IMessage]:
        """Receive messages addressed to an agent (or all if None)."""
        log_range = f"{since}..HEAD" if since else "-20"
        log_output = self._git("log", f"--max-count={limit}", "--format=%H|%ci|%s", log_range if since else f"-n{limit}")
        
        messages = []
        for line in log_output.split("\n"):
            if not line.strip():
                continue
            parts = line.split("|", 2)
            if len(parts) < 3:
                continue
            commit_hash, timestamp, subject = parts
            
            # Parse I2I format
            match = re.match(r"\[I2I:([^->]+)->([^:]+):([^:\]]+)(?::([^\]]+))?\] (.+)", subject)
            if not match:
                continue
            
            from_agent, to_agent, msg_type, thread_id, payload = match.groups()
            
            if for_agent and to_agent != for_agent and to_agent != "*":
                continue
            
            messages.append(I2IMessage(
                from_agent=from_agent,
                to_agent=to_agent,
                msg_type=msg_type,
                payload=payload,
                timestamp=timestamp,
                commit_hash=commit_hash,
                thread_id=thread_id
            ))
        
        return messages
    
    def broadcast(self, payload: str) -> str:
        """Broadcast to all agents."""
        return self.send("*", "broadcast", payload)
    
    def heartbeat(self) -> str:
        """Send heartbeat signal."""
        return self.send("*", "heartbeat", f"alive at {time.time()}")
    
    def threads(self) -> Dict[str, List[I2IMessage]]:
        """Group messages by thread ID."""
        msgs = self.receive(limit=50)
        threads: Dict[str, List[I2IMessage]] = {}
        for m in msgs:
            tid = m.thread_id or "default"
            if tid not in threads:
                threads[tid] = []
            threads[tid].append(m)
        return threads
    
    def _detect_agent(self) -> str:
        """Detect agent name from git config or environment."""
        try:
            name = self._git("config", "user.name")
            if name:
                return name
        except:
            pass
        return os.environ.get("AGENT_NAME", "unknown-agent")

def demo():
    """Demo: two agents communicating through git."""
    import tempfile, shutil
    
    # Create temp repo
    tmpdir = tempfile.mkdtemp()
    try:
        os.chdir(tmpdir)
        subprocess.run(["git", "init"], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Alice"], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "alice@fleet.local"], check=True, capture_output=True)
        
        i2i = I2IProtocol(tmpdir)
        
        # Alice sends to Bob
        hash1 = i2i.send("Bob", "request", "Can you check the PLATO gate status?")
        print(f"Alice -> Bob: {hash1[:8]}")
        
        # Alice broadcasts
        hash2 = i2i.broadcast("Fleet alert: Oracle1 is rebooting")
        print(f"Alice broadcast: {hash2[:8]}")
        
        # Bob reads messages
        os.environ["AGENT_NAME"] = "Bob"
        subprocess.run(["git", "config", "user.name", "Bob"], check=True, capture_output=True)
        
        msgs = i2i.receive(for_agent="Bob")
        print(f"\nBob received {len(msgs)} messages:")
        for m in msgs:
            print(f"  [{m.msg_type}] {m.from_agent}: {m.payload}")
        
        # Bob replies
        if msgs:
            hash3 = i2i.send("Alice", "response", "Gate is up. 5,928 tiles accepted.", thread_id=msgs[0].thread_id)
            print(f"\nBob -> Alice: {hash3[:8]}")
        
        # Alice reads reply
        os.environ["AGENT_NAME"] = "Alice"
        subprocess.run(["git", "config", "user.name", "Alice"], check=True, capture_output=True)
        
        replies = i2i.receive(for_agent="Alice")
        print(f"\nAlice received {len(replies)} messages:")
        for m in replies:
            print(f"  [{m.msg_type}] {m.from_agent}: {m.payload}")
        
    finally:
        os.chdir("/")
        shutil.rmtree(tmpdir, ignore_errors=True)

def main():
    demo()


if __name__ == "__main__":
    main()