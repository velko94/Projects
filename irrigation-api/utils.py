from fastapi import Request

def dummy_request_use(request: Request) -> None:
    """gloabal helper for pydantic wanrings"""
    _ = request