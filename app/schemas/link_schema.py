from pydantic import BaseModel, HttpUrl

class LinkCreate(BaseModel):
    user_id: int
    original_url: HttpUrl

class LinkResponse(BaseModel):
    id: int
    user_id: int
    original_url: HttpUrl
    short_code: str
    clicks: int
    class Config:
        orm_mode = True
