from fastapi import APIRouter

router = APIRouter(prefix="/get-parameter", tags=["get-parameter"])


@router.get("/schema")
async def schema():
    return {
        "activity": "get-parameter",
        "arguments": [
            {
                "argument": "target",
                "type": "list",
                "lookup": {
                    "url": "/get-parameter/targets",
                },
                "default": "",
            },
            {
                "argument": "parameter",
                "type": "list",
                "lookup": {
                    "url": "/get-parameter/parameters",
                    "dependencies": ["target"],
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


from pydantic import BaseModel


class Request(BaseModel):
    target: str
    parameter: str
    timeout: int


@router.post("")
async def get_parameter(request: Request) -> str:
    return f"{request.target}.{request.parameter}"
