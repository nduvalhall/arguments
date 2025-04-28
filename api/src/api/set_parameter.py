from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any

router = APIRouter(prefix="/set-parameter", tags=["set-parameter"])


@router.get("/schema")
async def schema():
    return {
        "activity": "set-parameter",
        "endpoint": "POST /set-parameter",
        "arguments": [
            {
                "argument": "target",
                "type": "list",
                "lookup": {
                    "endpoint": "GET /set-parameter/targets",
                },
                "default": "",
            },
            {
                "argument": "parameter",
                "type": "list",
                "lookup": {
                    "endpoint": "GET /set-parameter/parameters",
                    "dependencies": ["target"],
                },
                "default": "",
            },
            {
                "argument": "value",
                "type": "input",
                "validation": {
                    "url": "POST /set-parameter/validate-value",
                    "dependencies": ["target", "parameter", "value"],
                },
                "default": "",
            },
            {
                "argument": "timeout",
                "type": "number",
                "default": 30,
            },
        ],
    }


@router.get("/targets")
async def targets() -> list[str]:
    return ["target 1", "target 2"]


@router.get("/parameters")
async def parameters(target: str) -> list[str]:
    if target == "target 1":
        return ["parameter 1"]
    elif target == "target 2":
        return ["parameter 2"]
    else:
        return []


class ValidateValue(BaseModel):
    target: str
    parameter: str
    value: Any


@router.post("/validate-value")
async def validate_value(request: ValidateValue) -> None | str:
    if request.value == "bad":
        return "Invalid."
    else:
        return None


class Request(BaseModel):
    target: str
    parameter: str
    timeout: int


class Response(BaseModel):
    value: list[int | float | str]
    kind: str


@router.post("")
async def set_parameter(request: Request) -> Response:
    return Response(value=[f"{request.target}.{request.parameter}"], kind="list[str]")
