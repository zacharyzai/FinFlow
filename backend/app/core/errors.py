from fastapi import HTTPException


def app_error(status_code: int, code: str, message: str) -> HTTPException:
    """
    HTTPException whose detail carries a machine-readable `code` alongside the
    human message, so the frontend can react to error *type* (rate limited vs
    AI provider down vs bad input) instead of pattern-matching English text.
    """
    return HTTPException(status_code=status_code, detail={"code": code, "message": message})
