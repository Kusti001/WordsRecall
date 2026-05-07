from pydantic import BaseModel

class AddOrDeleteWordRequest(BaseModel):
    word_id: int