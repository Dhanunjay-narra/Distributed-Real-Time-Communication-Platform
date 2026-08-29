from packages.presence.tracker import PresenceTracker

def test_presence_heartbeat_tracking():
    tracker = PresenceTracker(ttl_seconds=5.0)
    tracker.heartbeat("user-alpha")
    assert tracker.is_online("user-alpha") is True
    assert tracker.is_online("user-unknown") is False
