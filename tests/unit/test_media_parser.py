from packages.media.parser import parse_media_metadata

def test_media_metadata_parsing():
    meta = parse_media_metadata("sample.png", b"\x89PNG\r\n\x1a\n" + b"\x00"*20, "image/png")
    assert meta["is_image"] is True
    assert meta["size_bytes"] == 28
