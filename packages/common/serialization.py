import json
from datetime import datetime, date
from decimal import Decimal

class DistributedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, set):
            return list(obj)
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        return super().default(obj)

def serialize_json(data: any) -> str:
    return json.dumps(data, cls=DistributedJSONEncoder, separators=(',', ':'))

def deserialize_json(payload: str) -> any:
    return json.loads(payload)
