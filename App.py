import json
import os
import shutil
import time
import bleedfacedetector as fd
import boto3
import cv2
import face_recognition
import requests, sys
from fastapi import FastAPI, File, UploadFile, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware




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

def Errorlines(error):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split( exc_tb.tb_frame.f_code.co_filename )[1]
    error = "Exception occured :- " + str( error ) + str(
        exc_type ) + str( fname ), str( exc_tb.tb_lineno )
    print(error)

def get_uniqueimage():
    try:
        if os.path.exists( 'Media/unique'):
            print( 'find' )
        else:
            os.makedirs( 'Media/unique' )
    except:pass


    for subdir, dirs, files in os.walk('Media/converted'):
        for data in os.listdir(subdir):
            # print(data)
            if '.png' in data:
                print(data)
                print(subdir)
                os.rename( subdir+'/'+data, r'Media/unique/' + data )
                break
                # if 'unique' not in str(subdir):
                #     shutil.rmtree(subdir)
                #     break

def compare_images():
    i = 0
    try:
        for img in os.listdir(r"Media/faces"):
            try:
                knownface = face_recognition.load_image_file( r"Media/faces/"+img)
                print('new loop started')
                try:
                    person_face_encoding = face_recognition.face_encodings(knownface)[0]
                    for image in os.listdir(r'Media/faces'):
                        newPic = face_recognition.load_image_file( 'Media/faces/'+image)
                        try:
                            face_encodings = face_recognition.face_encodings( newPic)[0]
                        except:continue
                        results = face_recognition.compare_faces( [person_face_encoding], face_encodings )
                        if not os.path.exists('Media/converted'):
                            os.mkdir('Media/converted')
                        if os.path.exists('Media/converted/'+str(i)):
                            print('sub dir in Media/converted')
                        else:
                            os.makedirs('Media/converted/'+str(i))
                        if results[0] == True:
                            os.rename('Media/faces/'+image,r'Media/converted/'+str(i)+'/'+image)
                except Exception as error:
                    print(Errorlines(error))

                    i = i + 1
                    continue
            except Exception as error:
                print(Errorlines(error))
    except Exception as error:
        print(Errorlines(error))

def getUniqueface(videopath, user_id, video_id, path, s3, videofilename):
    # try:
    #     s3.upload_file(videopath, 'original-video', user_id + f'/video/{video_id}/{videofilename}')
    # except Exception as e:
    #     print(e)
    try:
        vs = cv2.VideoCapture(videopath)

        frame_number = vs.get( cv2.CAP_PROP_FRAME_COUNT )
        fps = int( vs.get( cv2.CAP_PROP_FPS ) )
        seconds = int( frame_number / fps )
        print( seconds )
        count = 0

        while 1:
            start_time = time.time()
            ret, img = vs.read()
            # cv2.putText( img, 'FPS: {:.2f}'.format( fps ), (20, 20), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.7,
            #              color=(0, 0, 255) )
            # faces = fd.haar_detect(img)
            faces = fd.ssd_detect( img )
            # faces = fd.hog_detect( img )
            # faces = fd.cnn_detect( img )
            # faces = fd.hog_detect( img, upsample=0, height=0 )

            for (x, y, w, h) in faces:
                try:

                    # cv2.rectangle( img, (x, y), (x + w, y + h), (0, 0, 255), 2 )
                    crop_img = img[y:y + h, x:x + w]
                    # count += 4
                    count += 5  # i.e. at 30 fps, this advances one second
                    vs.set( 1, count )
                    frametime = count / fps
                    # print( math.ceil( frametime * 100 ) / 100 )
                    # print( faces )
                    if not os.path.exists('Media/faces'):
                        os.mkdir('Media/faces')
                    cv2.imwrite( f'Media/faces/{str( frametime )}.png', crop_img )
                    # cv2.waitKey( 1 )
                    # if 'simple' == "simple":
                    #     face = anonymize_face_simple( crop_img, factor=3.0 )
                    #
                    # img[y:y + h, x:x + w] = face
                    # cv2.putText(img,'Face Detected',(x,y+h+15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2, cv2.LINE_AA)
                except Exception as error:
                    print(Errorlines(error))
                    continue
            count += 5  # i.e. at 30 fps, this advances one second
            vs.set( 1, count )
            fps = (1.0 / (time.time() - start_time))
            #if cv2.waitKey( 1 ) == ord( 'q' ):
                #break

        vs.release()
        cv2.destroyAllWindows()



    except Exception as e:
        print(Errorlines(e))
    compare_images()
    try:
        shutil.rmtree( 'Media/faces' )
    except:
        print('go ahead')
    get_uniqueimage()
    try:
        shutil.rmtree( 'Media/converted' )
    except:
        print('go ahead')

    try:
        s3.upload_file(videopath, 'original-video', user_id + f'/video/{video_id}/{videofilename}')
    # except Exception as e:
    #     print(e)
    # try:
        for images in os.listdir('Media/unique'):
            s3.upload_file( f'Media/unique/{images}', 'original-video', user_id + f'/faces/{video_id}/{images}' )

        body = {
            "data_id": 68,
            "video_id": video_id,
            "message": "Video upload success"
        }
        headers = {"x-api-key": "3loi6egfa0g04kgwg884oo88sgccgockg0o"}
        data = requests.post(f'http://63.142.254.143/GovQuest/api/Redactions/edit_video/{user_id}', data=body,
                             headers=headers)
        print(data.text)
    except Exception as e:
        print(e)
        body = {
            "data_id": 68,
            "video_id": video_id,
            "message": "Video upload error"
        }
        headers = {"x-api-key": "3loi6egfa0g04kgwg884oo88sgccgockg0o"}
        data = requests.post(f'http://63.142.254.143/GovQuest/api/Redactions/edit_video/{user_id}', data=body,
                             headers=headers)
        print(data.text)


    shutil.rmtree('Media/unique')
    if os.path.exists( path ):
        os.remove( path )


@app.get("/")
def read_root():
    return {"Hello": "This is home"}


@app.post("/uploadfile")
async def create_upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...), user_id: str = Form(...)):
    Aws_access_key_id = 'AKIAIFWF3UATSC6JEWBA'
    Aws_secret_access_key = '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'

    s3 = boto3.client('s3',
                      aws_access_key_id=Aws_access_key_id,
                      aws_secret_access_key=Aws_secret_access_key,
                      )
    
    try:
        if os.path.exists( 'Media'):
            print( 'find Media' )
        else:
            os.makedirs( 'Media' )
    except:pass

    path = f"Media/{file.filename}"
    #
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    body = {
        "data_id": 68,
        "video_name": file.filename,
        "video_url": "response_url",
        "message": "Video uploading"
    }
    headers = {"x-api-key": "3loi6egfa0g04kgwg884oo88sgccgockg0o"}
    data = requests.post(f'http://63.142.254.143/GovQuest/api/Redactions/add_video/{user_id}',data=body,headers=headers)
    print(data.text)
    response_op=json.loads(data.text)
    # getUniqueface(path)
    # if os.path.exists( path ):
    #     os.remove( path )
    bucket = s3.list_objects( Bucket='original-video' )

    bucket_name = 'original-video'
    if 'Contents' in bucket:
        if not any(d['Key'] == str(user_id) for d in bucket.get('Contents')):
            s3.put_object( Bucket=bucket_name, Key=(user_id + '/video/') )
            s3.put_object( Bucket=bucket_name, Key=(user_id + '/faces/') )
    else:
        s3.put_object( Bucket=bucket_name, Key=(user_id +'/') )
        s3.put_object( Bucket=bucket_name, Key=(user_id + '/video/') )
        s3.put_object( Bucket=bucket_name, Key=(user_id + '/faces/') )

    videoid=response_op['response'][0]['video_id']
    s3.put_object( Bucket=bucket_name, Key=(user_id + f'/video/{videoid}') )
    s3.put_object( Bucket=bucket_name, Key=(user_id + f'/faces/{videoid}') )


    background_tasks.add_task(getUniqueface, f'Media/{file.filename}', user_id, videoid, path, s3, file.filename)
    
#     uploadBlobToAWS(path, user_id, videoid)

    videoData = { "message": "Sucess",
                "data": response_op,
                }

    return videoData


# @app.post("/detecthead")
# def upload_detectface(item: models.detectfaceitem):
#     path = item.path
#     print(path)
#     vs = cv2.VideoCapture( path )
#     frame_width = int( vs.get( 3 ) )
#     frame_height = int( vs.get( 4 ) )
#     frame_number = vs.get( cv2.CAP_PROP_FRAME_COUNT )
#     h = int( vs.get( cv2.CAP_PROP_FRAME_HEIGHT ) )
#     w = int( vs.get( cv2.CAP_PROP_FRAME_WIDTH ) )
#     fps = int( vs.get( cv2.CAP_PROP_FPS ) )
#     print( 'frame count', frame_number )
#     print( 'frame per second', fps )
#     seconds = int( frame_number / fps )
#     print( seconds )
#     count = 0
#     video_time = str( datetime.timedelta( seconds=seconds ) )
#     print( video_time )
#     list = []
#     AllList = []
#     size = (frame_width, frame_height)
#     result = cv2.VideoWriter( 'filename.avi',
#                               cv2.VideoWriter_fourcc( *'MJPG' ),
#
#                               10, size )
#     while True:
#         # grab the frame from the threaded video stream and resize it
#         # to have a maximum width of 400 pixels
#         ret, frame = vs.read()
#         try:
#             frame = imutils.resize( frame, width=500 )
#
#             # grab the dimensions of the frame and then construct a blob
#             # from it
#             (h, w) = frame.shape[:2]
#             blob = cv2.dnn.blobFromImage( frame, 1.0, (300, 300),
#                                           (104.0, 177.0, 123.0) )
#
#             # pass the blob through the network and obtain the face detections
#             net.setInput( blob )
#             detections = net.forward()
#
#             # loop over the detections
#             for i in range( 0, detections.shape[2] ):
#                 # extract the confidence (i.e., probability) associated with
#                 # the detection
#                 confidence = detections[0, 0, i, 2]
#
#                 # filter out weak detections by ensuring the confidence is
#                 # greater than the minimum confidence
#                 if confidence > 0.5:
#                     # compute the (x, y)-coordinates of the bounding box for
#                     # the object
#                     count += 10
#                     vs.set( 1, count )
#                     frametime = count / fps
#                     box = detections[0, 0, i, 3:7] * np.array( [w, h, w, h] )
#                     (startX, startY, endX, endY) = box.astype( "int" )
#
#                     # extract the face ROI
#                     face = frame[startY:endY, startX:endX]
#
#                     resized = cv2.resize(face, (36, 44), interpolation=cv2.INTER_AREA)
#
#                     cv2.imwrite( r'C:/Users/Ajinkya/Desktop/All Data/Recovered data 01-07 07_46_29/GitProject/VideoRedact/public/assets/header_img/' + str( math.ceil( frametime * 100 ) / 100 ) + '.png', resized )
#                     data = {
#                         "id": uuid.uuid4(),
#                         "object": 'C:/Users/Ajinkya/Desktop/All Data/Recovered data 01-07 07_46_29/GitProject/VideoRedact/public/assets/header_img/' + str( math.ceil( frametime * 100 ) / 100 ) + '.png',
#                         "time": math.ceil( frametime * 100 ) / 100,
#                         "auto": True,
#                         "Manual": None
#
#                     }
#                     list.append( data )
#                     # cv2.waitKey( 1 )
#
#                     # check to see if we are applying the "simple" face
#                     # blurring method
#                     if 'simple' == "simple":
#                         face = anonymize_face_simple( face, factor=3.0 )
#                     # otherwise, we must be applying the "pixelated" face
#                     # anonymization method
#                     else:
#                         face = anonymize_face_pixelate( face,
#                                                         blocks=20 )
#
#                     # store the blurred face in the output image
#                     frame[startY:endY, startX:endX] = face
#
#             count += 10  # i.e. at 30 fps, this advances one second
#             vs.set( 1, count )
#         except:
#             print( 'error' )
#             break
#
#     # do a bit of cleanup
#     vs.release()
#     result.release()
#     cv2.destroyAllWindows()
#
#     # subprocess.run(f"C:/Users/Ajinkya/Desktop/All Data/Recovered data 01-07 07_46_29/GitProject/VideoRedactAPI/ffmpeg-N-100581-ga454a0c14f-win64-gpl-shared-vulkan/bin/ffmpeg.exe -i test-1_2.mp4 -vn audio_only.wav")
#
#     ffmpeg_extract_audio(path, "test.wav", bitrate=3000, fps=44100)
#
#     framerate = 0.1
#
#     r = sr.Recognizer()
#     with sr.AudioFile("test.wav") as source:
#         # reads the audio file. Here we use record instead of
#         # listen
#         audio = r.record(source)
#
#         # decoder = r.recognize_sphinx(audio, show_all=False)
#         #
#         # print([(seg.word, seg.start_frame / framerate) for seg in decoder.seg()])
#
#     try:
#         print("The audio file contains: " + r.recognize_google(audio))
#         transcript = r.recognize_google(audio)
#         videoData = {
#             "id": uuid.uuid4(),
#             "faces": list,
#             "transcript": transcript,
#             "editedVideoPath": ""
#         }
#
#     except sr.UnknownValueError:
#         print("Google Speech Recognition could not understand audio")
#         videoData = {
#             "id": uuid.uuid4(),
#             "faces": list,
#             "transcript": "Google Speech Recognition could not understand audio",
#             "editedVideoPath": "",
#         }
#
#     except sr.RequestError as e:
#         print("Could not request results from Google Speech Recognition service; {0}".format(e))
#         videoData = {
#             "id": uuid.uuid4(),
#             "faces": list,
#             "transcript": "Could not request results from Google Speech Recognition service; {0}".format(e),
#             "editedVideoPath": ""
#         }
#
#     # AllList.append(videoData)
#
#     # with open('FaceData.json') as file:
#     #     file.write(AllList)
#
#
#     return videoData
#
# @app.post("/redactfaces")
# async def redact_face_audio(item: models.redactfaceitem):
#     print(item.data)
#     time.sleep(5)
#     return {"message": "success"}
#
# @app.get("/myAllVideos/{user_id}")
# def myAllVideos(user_id: str):
#     time.sleep(2)
#     if user_id == "abc":
#         # data = [
#         #     {
#         #         "id": uuid.uuid4(),
#         #         "user_id": user_id,
#         #         "video_name": "RRR Trailer",
#         #         "video_url": "./assets/UploadedVideo/rrr.mp4",
#         #         "upload_datetime": datetime.datetime.now(),
#         #         "thumbnail": "./assets/VideoCover/videocover.png",
#         #         "is_head_detect": True,
#         #         "is_transcription": True,
#         #         "is_edited": True,
#         #         "is_download": True,
#         #         "message": "processing"
#         #     },
#         #     {
#         #         "id": uuid.uuid4(),
#         #         "user_id": user_id,
#         #         "video_name": "Motivation video",
#         #         "video_url": "./assets/UploadedVideo/test-1_4.mp4",
#         #         "upload_datetime": datetime.datetime.now(),
#         #         "thumbnail": "./assets/VideoCover/videocover1.png",
#         #         "is_head_detect": True,
#         #         "is_transcription": True,
#         #         "is_edited": True,
#         #         "is_download": True,
#         #         "message": "success"
#         #     }
#         # ]
#
#         with open('videoData.json') as f:
#             data = json.load(f)
#
#         return data
#     else:
#         data = [
#             {
#                 "message": "Invalid user"
#             }
#         ]
#         return data
#
#
# @app.post('/getFaceData')
# def get_face_data(item: models.redactfaceitem):
#     time.sleep(2)
#     print(item.data)
#     with open('FaceData.json') as f:
#         data = json.load(f)
#
#     return data


@app.get('/getVideoData/{user_id}')
async def get_video_data(user_id: str, video_id: str):
    Aws_access_key_id = 'AKIAIFWF3UATSC6JEWBA'
    Aws_secret_access_key = '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'
    # bucketName = 'original-video'
    #
    # region = 'us-east-2'
    s3 = boto3.client('s3',
                      aws_access_key_id=Aws_access_key_id,
                      aws_secret_access_key=Aws_secret_access_key,
                      )
    Headers = {"x-api-key": "3loi6egfa0g04kgwg884oo88sgccgockg0o"}

    # message = ""
    # response_data = {}

    # while message == None or message == "" or message == "Video uploading":
        # time.sleep(2)
    response_data = requests.get(
        f'http://63.142.254.143/GovQuest/api/Redactions/video_details/{video_id}',
        headers=Headers
    )
    response_data = json.loads(response_data.text)

    message = response_data['response'][0]['message']

    videoID = response_data['response'][0]['video_id']
    videoName = response_data['response'][0]['video_name']

    faces_list = []
    video_url = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={'Bucket': 'original-video', 'Key': f'{user_id}/video/{videoID}/{videoName}'},
        ExpiresIn=3600,
    )
    List_object = s3.list_objects( Bucket='original-video', Prefix=f'{user_id}/faces/{videoID}/' )

    if 'Contents' in List_object:
        # print('%###################################################3')
        # print(List_object['Contents'])
        # print( '%###################################################3' )
        for item in List_object['Contents']:
            # print( '%###################################################3' )
            # print(item)
            # print( '%###################################################3' )
            face_url = s3.generate_presigned_url(
                ClientMethod='get_object',
                Params={'Bucket': 'original-video', 'Key': item['Key']},
                ExpiresIn=3600,
            )
            faces_list.append(
                {
                    "object": face_url,
                    "starttime": 0,
                    "endtime": 19000,
                    "auto": True,
                    "Manual": False
                }
            )
    data = response_data['response'][0]
    data['video_url'] = video_url
    data['faces'] = faces_list

    return data
