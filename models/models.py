from pydantic import BaseModel

class CredItem(BaseModel):
    username: str
    password: str
class detectfaceitem(BaseModel):
    path: str

class redactfaceitem(BaseModel):
    data: str