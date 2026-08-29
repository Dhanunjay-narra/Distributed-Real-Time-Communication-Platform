from typing import Dict, List

class ContentFilter:
    def __init__(self, blocked_words: List[str] = None):
        self.blocked_words = set(w.lower() for w in (blocked_words or ["spam", "scam", "phishing", "malware"]))

    def evaluate_message(self, text: str) -> Dict[str, any]:
        words = set(text.lower().split())
        matched = words.intersection(self.blocked_words)
        is_flagged = len(matched) > 0
        return {"is_flagged": is_flagged, "flagged_words": list(matched)}
