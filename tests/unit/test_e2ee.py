from packages.crypto.e2ee import DoubleRatchetSession

def test_double_ratchet_key_derivation():
    session = DoubleRatchetSession(b"pre-shared-master-ephemeral-key")
    k1 = session.step_ratchet(b"hello")
    k2 = session.step_ratchet(b"world")
    assert k1 != k2
    assert session.message_number == 2
