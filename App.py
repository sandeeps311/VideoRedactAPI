from pydantic import BaseModel
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import cv2
import shutil


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CredItem(BaseModel):
    username: str
    password: str

@app.get("/")
def read_root():
    return {"Hello": "This is home"}


@app.post("/login")
def read_item(Item: CredItem):
    username = Item.username
    password = Item.password
    return {"username": username, "password": password}


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    # contents = await file.read()
    # VideoFile = base64.b64encode(contents)
    # cnopts = pysftp.CnOpts()
    # cnopts.hostkeys = None
    # with pysftp.Connection('63.142.254.143', username='root', password='mysportseat@84484', cnopts=cnopts) as sftp:
    #     f = sftp.open(f'/root/VideoUpload/{file.filename}', 'wb')
    #     f.write(VideoFile)
    #     sftp.close()
    path = f"C:/Users/Ajinkya/Desktop/All Data/Recovered data 01-07 07_46_29/VideoRedact/UploadedVideos/{file.filename}"

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"filename": file.filename}