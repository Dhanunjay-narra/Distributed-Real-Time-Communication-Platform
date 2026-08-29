import pytest, asyncio
from services.coordination.locks import DistributedLockManager
from services.coordination.raft import RaftNode, RaftRole, LogEntry

@pytest.mark.asyncio
async def test_distributed_lock_manager():
    lock_mgr = DistributedLockManager("node-alpha")
    resource = "partition:conv-101"

    # 1. Acquire Lock
    lease_1 = await lock_mgr.acquire_lock(resource, ttl_seconds=2.0)
    assert lease_1 is not None

    # 2. Re-acquire by competitor fails
    lease_2 = await lock_mgr.acquire_lock(resource, ttl_seconds=2.0)
    assert lease_2 is None

    # 3. Release Lock
    released = await lock_mgr.release_lock(resource, lease_1)
    assert released is True

    # 4. Acquire succeeds after release
    lease_3 = await lock_mgr.acquire_lock(resource, ttl_seconds=2.0)
    assert lease_3 is not None

def test_raft_consensus_election_and_log_replication():
    n1 = RaftNode("Node1", ["Node2", "Node3"])
    n2 = RaftNode("Node2", ["Node1", "Node3"])
    n3 = RaftNode("Node3", ["Node1", "Node2"])

    # 1. Initial State -> All Followers
    assert n1.role == RaftRole.FOLLOWER
    assert n2.role == RaftRole.FOLLOWER

    # 2. Node1 starts election (Term 1)
    term = n1.start_election()
    assert term == 1
    assert n1.role == RaftRole.CANDIDATE

    # 3. Node1 requests vote from Node2 -> Granted
    voted_n2 = n2.request_vote(term=1, candidate_id="Node1", last_log_index=0, last_log_term=0)
    assert voted_n2 is True
    assert n1.receive_vote() is True  # Majority reached!
    assert n1.role == RaftRole.LEADER

    # 4. Leader replicates log entry to Followers
    entry = LogEntry(term=1, command={"op": "ALLOCATE_PARTITION", "conversation_id": "conv-55"})
    n1.log.append(entry)

    heartbeat_ok = n2.append_entries(term=1, leader_id="Node1", prev_log_index=0, prev_log_term=0, entries=[entry], leader_commit=1)
    assert heartbeat_ok is True
    assert len(n2.log) == 1
    assert len(n2.state_machine) == 1
    assert n2.state_machine[0]["conversation_id"] == "conv-55"
