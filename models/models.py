from typing import List

from pydantic import BaseModel

class CredItem(BaseModel):
    username: str
    password: str
class detectfaceitem(BaseModel):
    path: str

class redactfaceitem(BaseModel):
    data: str

class Image_URL(BaseModel):
    url: str

class downloadVideo(BaseModel):
    user_id: str
    video_id: str
    video_name: str
    video_url:str
    image_url:List[Image_URL]
    readctiontype: str
    level_simple:str
    level_pixelate: str

class downloadRedactedVideo(BaseModel):
    user_id: str
    video_id: str
    video_name: str
    bucket_name: str







