def patch_content(content: str) -> dict:
    """
    클라이언트에게 전달할 명령을 만들어 반환
    클라이언트가 patch_content 를 요구할 경우,
    설명 없이 컨텐츠의 결과값을 반환
    """
    return {"name": "patch_content", "action": "patch_content", "content": content}

