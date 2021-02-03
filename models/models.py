from pydantic import BaseModel

class CredItem(BaseModel):
    username: str
    password: str
class detectfaceitem(BaseModel):
    path: str

class redactfaceitem(BaseModel):
    data: str

class downloadVideo(BaseModel):
    user_id: str
    video_id: str
    video_name: str
    bucket_name: str
