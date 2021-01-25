import math, json, time
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import shutil
import datetime
import uuid
import cv2
import imutils
import numpy as np
from FaceDetection.pyimagesearch.face_blurring import anonymize_face_simple, anonymize_face_pixelate
import subprocess
import speech_recognition as sr
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_audio
from models import models
import boto3
from botocore.exceptions import ClientError
# import face_recognition



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


@app.get("/")
def read_root():
    return {"Hello": "This is home"}


@app.post("/uploadfile")
async def create_upload_file(file: UploadFile = File(...)):
    Aws_access_key_id = 'AKIAIFWF3UATSC6JEWBA'
    Aws_secret_access_key = '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'

    bucketName = 'original-video'

    region = 'us-east-2'

    # s3_client = boto3.resource(
    #         service_name='s3',
    #         region_name=region,
    #         aws_access_key_id=Aws_access_key_id,
    #         aws_secret_access_key=Aws_secret_access_key
    #     )

    s3 = boto3.client('s3',
                      aws_access_key_id=Aws_access_key_id,
                      aws_secret_access_key=Aws_secret_access_key,
                      )

    # for bucket in s3_client.buckets.all():
    #     print(bucket.name)

    with open('videoData.json') as f:
        data = json.load(f)

    # print(data)
    #
    path = f"C:/Users/Ajinkya/Desktop/All Data/Recovered data 01-07 07_46_29/GitProject/VideoRedact/public/assets/UploadedVideo/{file.filename}"
    #
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # s3_client.Bucket('original-video').upload_file(Filename=path, Key=file.filename)

    try:
        upload_response = s3.upload_file(path, 'original-video', file.filename)
        print(upload_response)
    except ClientError as e:
        print(e)

    # for obj in s3_client.Bucket('original-video').objects.all():
    #     print(obj)

    response = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={'Bucket': 'original-video', 'Key': file.filename},
        ExpiresIn=3600,
    )

    print(response)


    videoData = {
            "id": str(uuid.uuid4()),
            "user_id": "user_id",
            "video_name": "Motivation video",
            "video_url": response,
            "upload_datetime": str(datetime.datetime.now()),
            "thumbnail": "./assets/VideoCover/videocover1.png",
            "is_head_detect": True,
            "is_transcription": True,
            "is_edited": False,
            "is_download": False,
            "message": "success"
        }
    data.append(videoData)

    with open('videoData.json', 'w') as f:
        json.dump(data, f)

    return upload_response


@app.post("/detecthead")
def upload_detectface(item: models.detectfaceitem):
    path = item.path
    print(path)
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
    AllList = []
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
                    box = detections[0, 0, i, 3:7] * np.array( [w, h, w, h] )
                    (startX, startY, endX, endY) = box.astype( "int" )

                    # extract the face ROI
                    face = frame[startY:endY, startX:endX]

                    resized = cv2.resize(face, (36, 44), interpolation=cv2.INTER_AREA)

                    cv2.imwrite( r'C:/Users/Ajinkya/Desktop/All Data/Recovered data 01-07 07_46_29/GitProject/VideoRedact/public/assets/header_img/' + str( math.ceil( frametime * 100 ) / 100 ) + '.png', resized )
                    data = {
                        "id": uuid.uuid4(),
                        "object": 'C:/Users/Ajinkya/Desktop/All Data/Recovered data 01-07 07_46_29/GitProject/VideoRedact/public/assets/header_img/' + str( math.ceil( frametime * 100 ) / 100 ) + '.png',
                        "time": math.ceil( frametime * 100 ) / 100,
                        "auto": True,
                        "Manual": None

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

            count += 10  # i.e. at 30 fps, this advances one second
            vs.set( 1, count )
        except:
            print( 'error' )
            break

    # do a bit of cleanup
    vs.release()
    result.release()
    cv2.destroyAllWindows()

    # subprocess.run(f"C:/Users/Ajinkya/Desktop/All Data/Recovered data 01-07 07_46_29/GitProject/VideoRedactAPI/ffmpeg-N-100581-ga454a0c14f-win64-gpl-shared-vulkan/bin/ffmpeg.exe -i test-1_2.mp4 -vn audio_only.wav")

    ffmpeg_extract_audio(path, "test.wav", bitrate=3000, fps=44100)

    framerate = 0.1

    r = sr.Recognizer()
    with sr.AudioFile("test.wav") as source:
        # reads the audio file. Here we use record instead of
        # listen
        audio = r.record(source)

        # decoder = r.recognize_sphinx(audio, show_all=False)
        #
        # print([(seg.word, seg.start_frame / framerate) for seg in decoder.seg()])

    try:
        print("The audio file contains: " + r.recognize_google(audio))
        transcript = r.recognize_google(audio)
        videoData = {
            "id": uuid.uuid4(),
            "faces": list,
            "transcript": transcript,
            "editedVideoPath": ""
        }

    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
        videoData = {
            "id": uuid.uuid4(),
            "faces": list,
            "transcript": "Google Speech Recognition could not understand audio",
            "editedVideoPath": "",
        }

    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
        videoData = {
            "id": uuid.uuid4(),
            "faces": list,
            "transcript": "Could not request results from Google Speech Recognition service; {0}".format(e),
            "editedVideoPath": ""
        }

    # AllList.append(videoData)

    # with open('FaceData.json') as file:
    #     file.write(AllList)


    return videoData

@app.post("/redactfaces")
async def redact_face_audio(item: models.redactfaceitem):
    print(item.data)
    time.sleep(5)
    return {"message": "success"}

@app.get("/myAllVideos/{user_id}")
def myAllVideos(user_id: str):
    time.sleep(2)
    if user_id == "abc":
        # data = [
        #     {
        #         "id": uuid.uuid4(),
        #         "user_id": user_id,
        #         "video_name": "RRR Trailer",
        #         "video_url": "./assets/UploadedVideo/rrr.mp4",
        #         "upload_datetime": datetime.datetime.now(),
        #         "thumbnail": "./assets/VideoCover/videocover.png",
        #         "is_head_detect": True,
        #         "is_transcription": True,
        #         "is_edited": True,
        #         "is_download": True,
        #         "message": "processing"
        #     },
        #     {
        #         "id": uuid.uuid4(),
        #         "user_id": user_id,
        #         "video_name": "Motivation video",
        #         "video_url": "./assets/UploadedVideo/test-1_4.mp4",
        #         "upload_datetime": datetime.datetime.now(),
        #         "thumbnail": "./assets/VideoCover/videocover1.png",
        #         "is_head_detect": True,
        #         "is_transcription": True,
        #         "is_edited": True,
        #         "is_download": True,
        #         "message": "success"
        #     }
        # ]

        with open('videoData.json') as f:
            data = json.load(f)

        return data
    else:
        data = [
            {
                "message": "Invalid user"
            }
        ]
        return data


@app.post('/getFaceData')
def get_face_data(item: models.redactfaceitem):
    time.sleep(2)
    print(item.data)
    with open('FaceData.json') as f:
        data = json.load(f)

    return data
