from pydantic import BaseModel
from dataStruct.requestModels import Message


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int

class queryResponse(BaseModel):
    messages: list[Message]


