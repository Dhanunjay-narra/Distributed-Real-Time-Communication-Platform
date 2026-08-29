import base64, json
from typing import Generic, TypeVar, List, Optional, Any
from pydantic import BaseModel, Field

T = TypeVar("T")

class Page(BaseModel, Generic[T]):
    items: List[T]
    next_cursor: Optional[str] = None
    prev_cursor: Optional[str] = None
    has_more: bool = False
    total_count: Optional[int] = None

class CursorPagination:
    @staticmethod
    def encode_cursor(data: dict) -> str:
        return base64.urlsafe_b64encode(json.dumps(data).encode()).decode()
    @staticmethod
    def decode_cursor(cursor: Optional[str]) -> Optional[dict]:
        if not cursor: return None
        try: return json.loads(base64.urlsafe_b64decode(cursor.encode()).decode())
        except Exception: return None

class CursorPaginationParams(BaseModel):
    cursor: Optional[str] = Field(None, description="Opaque cursor token")
    limit: int = Field(50, ge=1, le=100, description="Items per page")
    direction: str = Field("forward", description="forward or backward")

PaginatedResult = Page
