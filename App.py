import math

from pydantic import BaseModel
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import cv2
import shutil
import datetime

import cv2
import imutils
import numpy as np
from FaceDetection.pyimagesearch.face_blurring import anonymize_face_simple, anonymize_face_pixelate

prototxtPath = 'FaceDetection/face_detector/deploy.prototxt'
weightsPath = 'FaceDetection/face_detector/res10_300x300_ssd_iter_140000.caffemodel'
net = cv2.dnn.readNet( prototxtPath, weightsPath )


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
class detectfaceitem(BaseModel):
    path: str

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


@app.post("/detecthead/")
def upload_detectface(Item:detectfaceitem):
    path=Item.path
    vs = cv2.VideoCapture( path )
    frame_width = int( vs.get( 3 ) )
    frame_height = int( vs.get( 4 ) )
    frame_number = vs.get( cv2.CAP_PROP_FRAME_COUNT )
    h = int( vs.get( cv2.CAP_PROP_FRAME_HEIGHT ) )
    w = int( vs.get( cv2.CAP_PROP_FRAME_WIDTH ) )
    fps = int( vs.get( cv2.CAP_PROP_FPS ) )
    print( 'frame count', frame_number )
    print( 'frame per second', fps )
    seconds = int( frame_number / fps )
    print( seconds )
    count = 0
    video_time = str( datetime.timedelta( seconds=seconds ) )
    print( video_time )
    list = []
    size = (frame_width, frame_height)
    result = cv2.VideoWriter( 'filename.avi',
                              cv2.VideoWriter_fourcc( *'MJPG' ),

                              10, size )
    while True:
        # grab the frame from the threaded video stream and resize it
        # to have a maximum width of 400 pixels
        ret, frame = vs.read()
        try:
            frame = imutils.resize( frame, width=500 )

            # grab the dimensions of the frame and then construct a blob
            # from it
            (h, w) = frame.shape[:2]
            blob = cv2.dnn.blobFromImage( frame, 1.0, (300, 300),
                                          (104.0, 177.0, 123.0) )

            # pass the blob through the network and obtain the face detections
            net.setInput( blob )
            detections = net.forward()

            # loop over the detections
            for i in range( 0, detections.shape[2] ):
                # extract the confidence (i.e., probability) associated with
                # the detection
                confidence = detections[0, 0, i, 2]

                # filter out weak detections by ensuring the confidence is
                # greater than the minimum confidence
                if confidence > 0.5:
                    # compute the (x, y)-coordinates of the bounding box for
                    # the object
                    count += 10
                    vs.set( 1, count )
                    frametime = count / fps
                    # print( math.ceil( frametime * 100 ) / 100 )
                    # list.append( math.ceil( frametime * 100 ) / 100 )



                    print( "time stamp current frame:", count / fps )

                    box = detections[0, 0, i, 3:7] * np.array( [w, h, w, h] )
                    (startX, startY, endX, endY) = box.astype( "int" )

                    # extract the face ROI
                    face = frame[startY:endY, startX:endX]
                    # cv2.imshow( 'test', face )
                    # print(startY)

                    cv2.imwrite( r'E:/VideoProject/images/' + str( math.ceil( frametime * 100 ) / 100 ) + '.png', face )
                    data = {
                        "object":'E:/VideoProject/images/' + str( math.ceil( frametime * 100 ) / 100 ) + '.png',
                        "time":math.ceil( frametime * 100 ) / 100,
                        "auto":True,
                        "Manual":None

                    }
                    list.append( data )
                    # cv2.waitKey( 1 )

                    # check to see if we are applying the "simple" face
                    # blurring method
                    if 'simple' == "simple":
                        face = anonymize_face_simple( face, factor=3.0 )

                    # otherwise, we must be applying the "pixelated" face
                    # anonymization method
                    else:
                        face = anonymize_face_pixelate( face,
                                                        blocks=20 )

                    # store the blurred face in the output image
                    frame[startY:endY, startX:endX] = face

            # show the output frame

            # result.write( frame )
            # cv2.imshow( "Frame", frame )
            # key = cv2.waitKey( 1 ) & 0xFF
            # if key == 'p':
            #     cv2.waitKey()
            # #
            # # if the `q` key was pressed, break from the loop
            # if key == ord( "q" ):
            #     break
            count += 10  # i.e. at 30 fps, this advances one second
            vs.set( 1, count )
            frametime = count / fps
            print( list )
        except:
            print( 'error' )
            break

    # do a bit of cleanup
    vs.release()
    result.release()
    cv2.destroyAllWindows()
    # print(list)
    return list

