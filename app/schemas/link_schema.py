from pydantic import BaseModel, HttpUrl

class LinkCreate(BaseModel):
    original_url: str
    
class LinkResponse(BaseModel):
    id: int
    original_url: str
    short_code: str
    clicks: int
    class Config:
        orm_mode = True