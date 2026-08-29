import asyncio, random, time
from enum import Enum
from typing import List, Dict, Any, Optional

class RaftRole(str, Enum):
    FOLLOWER = "FOLLOWER"
    CANDIDATE = "CANDIDATE"
    LEADER = "LEADER"

class LogEntry:
    def __init__(self, term: int, command: Any):
        self.term = term
        self.command = command

class RaftNode:
    def __init__(self, node_id: str, peers: List[str]):
        self.node_id = node_id
        self.peers = peers
        self.role = RaftRole.FOLLOWER
        self.current_term = 0
        self.voted_for: Optional[str] = None
        self.log: List[LogEntry] = []
        self.commit_index = 0
        self.state_machine: List[Any] = []
        self.votes_received = 0

    def start_election(self) -> int:
        self.role = RaftRole.CANDIDATE
        self.current_term += 1
        self.voted_for = self.node_id
        self.votes_received = 1
        return self.current_term

    def request_vote(self, term: int, candidate_id: str, last_log_index: int, last_log_term: int) -> bool:
        if term > self.current_term:
            self.current_term = term
            self.role = RaftRole.FOLLOWER
            self.voted_for = None

        if term == self.current_term and (self.voted_for is None or self.voted_for == candidate_id):
            self.voted_for = candidate_id
            return True
        return False

    def receive_vote(self) -> bool:
        self.votes_received += 1
        total_cluster_size = len(self.peers) + 1
        majority = (total_cluster_size // 2) + 1
        if self.role == RaftRole.CANDIDATE and self.votes_received >= majority:
            self.role = RaftRole.LEADER
            return True
        return False

    def append_entries(self, term: int, leader_id: str, prev_log_index: int, prev_log_term: int, entries: List[LogEntry], leader_commit: int) -> bool:
        if term < self.current_term:
            return False

        if term > self.current_term:
            self.current_term = term
            self.role = RaftRole.FOLLOWER
            self.voted_for = None

        self.role = RaftRole.FOLLOWER

        for entry in entries:
            self.log.append(entry)

        if leader_commit > self.commit_index:
            self.commit_index = min(leader_commit, len(self.log))
            while len(self.state_machine) < self.commit_index:
                idx = len(self.state_machine)
                self.state_machine.append(self.log[idx].command)

        return True
