from pydantic import BaseModel


class Message(BaseModel):
    message: str


class Token(BaseModel):
    access_token: str
    token_type: str
