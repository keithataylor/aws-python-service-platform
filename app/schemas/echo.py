from pydantic import BaseModel


class EchoRequest(BaseModel):
    text: str


class EchoResponse(BaseModel):
    text: str