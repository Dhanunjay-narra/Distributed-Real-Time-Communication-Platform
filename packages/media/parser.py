from typing import Dict

def parse_media_metadata(file_name: str, file_bytes: bytes, mime_type: str) -> Dict[str, any]:
    size_bytes = len(file_bytes)
    return {
        "file_name": file_name,
        "size_bytes": size_bytes,
        "mime_type": mime_type,
        "is_image": mime_type.startswith("image/"),
        "is_audio": mime_type.startswith("audio/"),
        "is_video": mime_type.startswith("video/")
    }
