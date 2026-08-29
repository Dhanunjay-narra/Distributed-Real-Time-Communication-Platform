"""Social Contact Graph and Discovery - Dynamic Query Builder and SQL Generator.
"""
from typing import List, Dict, Any, Optional, Union
from sqlalchemy import select, and_, or_, not_, desc, asc, func

class ContactsQueryFilter:
    def __init__(self):
        self.conditions = []
        self.sort_fields = []
        self.limit_val: Optional[int] = None
        self.offset_val: Optional[int] = None

    def filter_eq(self, field_name: str, value: Any) -> "ContactsQueryFilter":
        self.conditions.append({"op": "eq", "field": field_name, "val": value})
        return self

    def filter_neq(self, field_name: str, value: Any) -> "ContactsQueryFilter":
        self.conditions.append({"op": "neq", "field": field_name, "val": value})
        return self

    def filter_gt(self, field_name: str, value: Any) -> "ContactsQueryFilter":
        self.conditions.append({"op": "gt", "field": field_name, "val": value})
        return self

    def filter_lt(self, field_name: str, value: Any) -> "ContactsQueryFilter":
        self.conditions.append({"op": "lt", "field": field_name, "val": value})
        return self

    def filter_in(self, field_name: str, values: List[Any]) -> "ContactsQueryFilter":
        self.conditions.append({"op": "in", "field": field_name, "val": values})
        return self

    def filter_like(self, field_name: str, pattern: str) -> "ContactsQueryFilter":
        self.conditions.append({"op": "like", "field": field_name, "val": pattern})
        return self

    def order_by(self, field_name: str, ascending: bool = True) -> "ContactsQueryFilter":
        self.sort_fields.append((field_name, ascending))
        return self

    def paginate(self, offset: int, limit: int) -> "ContactsQueryFilter":
        self.offset_val = offset
        self.limit_val = limit
        return self

    def build_predicate(self) -> Dict[str, Any]:
        return {
            "service": "contacts",
            "conditions": self.conditions,
            "sort": self.sort_fields,
            "offset": self.offset_val,
            "limit": self.limit_val
        }

class ContactsQueryBuilder:
    @staticmethod
    def construct_query(filters: ContactsQueryFilter) -> str:
        parts = [f"SELECT * FROM contacts_records"]
        if filters.conditions:
            cond_str = " AND ".join([f"{c['field']} {c['op']} '{c['val']}'" for c in filters.conditions])
            parts.append(f"WHERE {cond_str}")
        if filters.sort_fields:
            sort_str = ", ".join([f"{f[0]} {'ASC' if f[1] else 'DESC'}" for f in filters.sort_fields])
            parts.append(f"ORDER BY {sort_str}")
        if filters.limit_val is not None:
            parts.append(f"LIMIT {filters.limit_val}")
        if filters.offset_val is not None:
            parts.append(f"OFFSET {filters.offset_val}")
        return " ".join(parts)
