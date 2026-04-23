from pydantic import BaseModel

class ReviewRequest(BaseModel):
    result: str