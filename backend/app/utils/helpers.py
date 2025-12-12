from typing import Dict, Any, List, Optional
from bson import ObjectId


def convert_id_to_string(obj: Dict[str, Any]) -> Dict[str, Any]:
    if "_id" in obj and obj["_id"]:
        obj["_id"] = str(obj["_id"])
    return obj


def convert_ids_in_list(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    for item in items:
        convert_id_to_string(item)
    return items


def is_valid_object_id(id_string: str) -> bool:
    try:
        ObjectId(id_string)
        return True
    except Exception:
        return False

