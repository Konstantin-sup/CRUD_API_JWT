from fastapi import HTTPException
from fastapi.responses import JSONResponse, Response

def validator_err(request, ex):
    return JSONResponse({"detail": ex.errors(), "your_input": ex.body})

def not_found_response(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"Status": exc.status_code, "message": exc.message,
                         "detail": exc.detail})

def access_not_allowed(request, ex):
    return JSONResponse({"detail": ex.detail, "status_code": ex.status_code,
                         "message": ex.message, "users_role": ex.access_role,
                         "required_role": ex.required_role})


class WasNotFound(HTTPException):
    def __init__(self, detail: str, status_code: int, message: str, er_code: str):
        super().__init__(status_code=status_code, detail=detail)
        self.message = message
        self.er_code = er_code


class NoEnter(HTTPException):
    def __init__(self, detail: str, status_code: int, message: str, users_role: str, required_role: list[str], er_code: str):
        super().__init__(status_code=status_code, detail=detail)
        self.message = message
        self.users_role = users_role
        self.required_role = required_role
        self.er_code = er_code


class EmptyRequest(HTTPException):
    def __init__(self, detail: str, status_code: int, er_code: str):
        super().__init__(status_code=status_code, detail=detail)
        self.er_code = er_code


