from pydantic import BaseModel, HttpUrl

class LinkCreate(BaseModel):
    original_url: HttpUrl

class LinkCreateCustom(LinkCreate):
    original_url: HttpUrl
    custom_code: str

class LinkResponse(BaseModel):
    id: int
    user_id: int
    original_url: HttpUrl
    short_code: str
    clicks: int
    class ConfigDict:
        from_attributes = True

class LinkDelete(BaseModel):
    id: int