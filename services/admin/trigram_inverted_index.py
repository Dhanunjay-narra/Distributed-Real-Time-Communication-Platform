"""Operations Control Center and Telemetry - Trigram Inverted Index and Substring Matcher.
"""
from typing import Dict, Set, List

class AdminTrigramIndex:
    def __init__(self):
        self.index: Dict[str, Set[str]] = {}

    def _extract_trigrams(self, text: str) -> List[str]:
        cleaned = f"$${text.lower()}$$"
        return [cleaned[i:i+3] for i in range(len(cleaned) - 2)]

    def index_document(self, doc_id: str, text: str):
        trigrams = self._extract_trigrams(text)
        for tri in trigrams:
            if tri not in self.index:
                self.index[tri] = set()
            self.index[tri].add(doc_id)

    def search_query(self, query_text: str) -> Set[str]:
        trigrams = self._extract_trigrams(query_text)
        if not trigrams:
            return set()
        
        matches = None
        for tri in trigrams:
            doc_ids = self.index.get(tri, set())
            if matches is None:
                matches = set(doc_ids)
            else:
                matches.intersection_update(doc_ids)
        return matches or set()
