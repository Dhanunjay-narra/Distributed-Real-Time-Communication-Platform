"""Time-Series Aggregations and DAU Metrics - Data Access and Repository Layer.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_

class AnalyticsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self._memory_store: Dict[str, Dict[str, Any]] = {}

    async def find_by_id(self, entity_id: str) -> Optional[Dict[str, Any]]:
        return self._memory_store.get(entity_id)

    async def persist(self, entity_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        self._memory_store[entity_id] = data
        return data

    async def list_entities(self, offset: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        items = list(self._memory_store.values())
        return items[offset:offset + limit]

    async def count_all(self) -> int:
        return len(self._memory_store)

    async def remove_by_id(self, entity_id: str) -> bool:
        if entity_id in self._memory_store:
            del self._memory_store[entity_id]
            return True
        return False
