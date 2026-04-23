from pydantic import BaseModel

class AddWordRequest(BaseModel):
    id: str