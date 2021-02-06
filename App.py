import json
import os
import time
import bleedfacedetector as fd
import boto3
import cv2
import face_recognition
import requests, sys
import shutil
from fastapi import FastAPI, File, UploadFile, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_audio

from FaceDetection.pyimagesearch.face_blurring import anonymize_face_simple, anonymize_face_pixelate
from models import models
import speech_recognition as sr

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

try:
    if os.path.exists( 'Media' ):
        print( 'find' )
    else:
        os.makedirs( 'Media' )
except:
    pass


def Errorlines(error):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split( exc_tb.tb_frame.f_code.co_filename )[1]
    error = "Exception occured :- " + str( error ) + str(
        exc_type ) + str( fname ), str( exc_tb.tb_lineno )
    print( error )


def get_uniqueimage():
    try:
        if os.path.exists( 'Media/unique' ):
            print( 'find' )
        else:
            os.makedirs( 'Media/unique' )
    except:
        pass

    for subdir, dirs, files in os.walk( 'Media/converted' ):
        for data in os.listdir( subdir ):
            # print(data)
            if '.png' in data:
                print( data )
                print( subdir )
                os.rename( subdir + '/' + data, r'Media/unique/' + data )
                break
    return True
def compare_images():
    i = 0
    if not os.path.exists( 'Media/converted' ):
        os.mkdir( 'Media/converted' )
        print( 'created in Media/converted' )
    try:
        for img in os.listdir( r"Media/faces" ):
            try:
                knownface = face_recognition.load_image_file( r"Media/faces/" + img )

                try:
                    person_face_encoding = face_recognition.face_encodings( knownface )[0]
                    for image in os.listdir( r'Media/faces' ):
                        newPic = face_recognition.load_image_file( 'Media/faces/' + image )
                        try:
                            face_encodings = face_recognition.face_encodings( newPic )[0]
                        except:
                            continue
                        results = face_recognition.compare_faces( [person_face_encoding], face_encodings )
                        if os.path.exists( 'Media/converted/' + str( i ) ):
                            print( 'sub dir in Media/converted' )
                        else:
                            os.makedirs( 'Media/converted/' + str( i ) )
                        if results[0] == True:
                            os.rename( 'Media/faces/' + image, r'Media/converted/' + str( i ) + '/' + image )
                except Exception as error:

                    # print( Errorlines( error ) )

                    i = i + 1
                    continue
            except Exception as error:
                print( Errorlines( error ) )
    except Exception as error:
        print( Errorlines( error ) )
    return 'True'
async def getUniqueface(videopath, user_id, video_id, path, s3, videofilename, agency_id):
    try:
        vs = cv2.VideoCapture( videopath )

        frame_number = vs.get( cv2.CAP_PROP_FRAME_COUNT )
        fps = int( vs.get( cv2.CAP_PROP_FPS ) )
        seconds = int( frame_number / fps )
        print( seconds )
        count = 0
        if not os.path.exists( 'Media/faces' ):
            os.mkdir( 'Media/faces' )

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

                    cv2.imwrite( f'Media/faces/{str( frametime )}.png', crop_img )
                    # cv2.waitKey( 1 )
                    # if 'simple' == "simple":
                    #     face = anonymize_face_simple( crop_img, factor=3.0 )
                    #
                    # img[y:y + h, x:x + w] = face
                    # cv2.putText(img,'Face Detected',(x,y+h+15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2, cv2.LINE_AA)
                except Exception as error:
                    # print( Errorlines( error ) )
                    continue
            count += 5  # i.e. at 30 fps, this advances one second
            vs.set( 1, count )
            fps = (1.0 / (time.time() - start_time))
            # if cv2.waitKey( 1 ) == ord( 'q' ):
            # break

        vs.release()
        cv2.destroyAllWindows()



    except Exception as e:
        print( Errorlines( e ) )
    result_compare_images = compare_images()
    print(result_compare_images)
    try:
        shutil.rmtree( 'Media/faces' )
    except:
        print( 'go ahead' )

    result_get_uniqueimage = get_uniqueimage()
    print(result_get_uniqueimage)

    try:
        shutil.rmtree( 'Media/converted' )
    except:
        print( 'go ahead' )

    try:
        s3.upload_file( videopath, 'original-video', user_id + f'/video/{video_id}/{videofilename}' )
        # except Exception as e:
        #     print(e)
        # try:
        for images in os.listdir( 'Media/unique' ):
            s3.upload_file( f'Media/unique/{images}', 'original-video', user_id + f'/faces/{video_id}/{images}' )

        body = {
            "video_id": video_id,
            "agency_id": agency_id,
            "message": "Video upload success"
        }
        headers = {"x-api-key": "3loi6egfa0g04kgwg884oo88sgccgockg0o"}
        data = requests.post( f'http://63.142.254.143/GovQuest/api/Redactions/edit_video/{user_id}', data=body,
                              headers=headers )
        print( data.text )
    except Exception as e:
        print( Errorlines( e ) )
        body = {
            "video_id": video_id,
            "agency_id": agency_id,
            "message": "Video upload error"
        }
        headers = {"x-api-key": "3loi6egfa0g04kgwg884oo88sgccgockg0o"}
        data = requests.post( f'http://63.142.254.143/GovQuest/api/Redactions/edit_video/{user_id}', data=body,
                              headers=headers )
        print( data.text )

    shutil.rmtree( 'Media/unique' )
    # if os.path.exists( path ):
    #     os.remove( path )


@app.get( "/" )
def read_root():
    return {"Hello": "This is home"}

@app.post( "/uploadfile" )
async def create_upload_file(background_tasks: BackgroundTasks, file: UploadFile = File( ... ),
                             user_id: str = Form( ... ), agency_id: str = Form( ... )):
    Aws_access_key_id = 'AKIAIFWF3UATSC6JEWBA'
    Aws_secret_access_key = '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'

    s3 = boto3.client( 's3',
                       aws_access_key_id=Aws_access_key_id,
                       aws_secret_access_key=Aws_secret_access_key,
                       )
    try:
        if os.path.exists( 'Media' ):
            print( 'Media folder found' )
        else:
            os.makedirs( 'Media' )
            print("Media Folder created")
    except:
        pass
    path = f"Media/{file.filename}"
    #
    with open( path, "wb" ) as buffer:
        shutil.copyfileobj( file.file, buffer )

    body = {
        "video_name": file.filename,
        "video_url": "response_url",
        "agency_id": agency_id,
        "message": "Video uploading"
    }
    headers = {"x-api-key": "3loi6egfa0g04kgwg884oo88sgccgockg0o"}
    data = requests.post( f'http://63.142.254.143/GovQuest/api/Redactions/add_video/{user_id}', data=body,
                          headers=headers )
    print( data.text )
    response_op = json.loads( data.text )
    bucket = s3.list_objects( Bucket='original-video' )

    bucket_name = 'original-video'
    if 'Contents' in bucket:
        if not any( d['Key'] == str( user_id ) for d in bucket.get( 'Contents' ) ):
            s3.put_object( Bucket=bucket_name, Key=(user_id + '/video/') )
            s3.put_object( Bucket=bucket_name, Key=(user_id + '/faces/') )
    else:
        s3.put_object( Bucket=bucket_name, Key=(user_id + '/') )
        s3.put_object( Bucket=bucket_name, Key=(user_id + '/video/') )
        s3.put_object( Bucket=bucket_name, Key=(user_id + '/faces/') )

    videoid = response_op['response'][0]['video_id']
    s3.put_object( Bucket=bucket_name, Key=(user_id + f'/video/{videoid}') )
    s3.put_object( Bucket=bucket_name, Key=(user_id + f'/faces/{videoid}') )

    background_tasks.add_task( getUniqueface, f'Media/{file.filename}', user_id, videoid, path, s3, file.filename,
                               agency_id )

    #     uploadBlobToAWS(path, user_id, videoid)

    videoData = {"message": "Sucess",
                 "data": response_op,
                 }

    return videoData


@app.get( '/getVideoData/{user_id}' )
async def get_video_data(user_id: str, video_id: str):
    try:
        if os.path.exists( 'Media' ):
            print( 'Media folder found' )
        else:
            os.makedirs( 'Media' )
            print("Media Folder created")
    except:
        pass
    Aws_access_key_id = 'AKIAIFWF3UATSC6JEWBA'
    Aws_secret_access_key = '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'
    s3 = boto3.client( 's3',
                       aws_access_key_id=Aws_access_key_id,
                       aws_secret_access_key=Aws_secret_access_key,
                       )
    Headers = {"x-api-key": "3loi6egfa0g04kgwg884oo88sgccgockg0o"}
    response_data = requests.get(
        f'http://63.142.254.143/GovQuest/api/Redactions/video_details/{video_id}',
        headers=Headers
    )
    response_data = json.loads( response_data.text )

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
        for item in List_object['Contents']:
            face_url = s3.generate_presigned_url(
                ClientMethod='get_object',
                Params={'Bucket': 'original-video', 'Key': item['Key']},
                ExpiresIn=3600,
            )
            starttime = str( item['Key'] ).split( '/' )[3].split( '.' )[0]
            starttime = float( starttime ) * 100
            starttime = str( starttime ).split( '.' )[0]

            endtime = str( item['Key'] ).split( '/' )[3].split( '.' )[0]
            endtime = float( endtime ) * 100
            endtime = str( starttime ).split( '.' )[0]

            faces_list.append(
                {
                    "faceName": item['Key'],
                    "object": face_url,
                    "starttime": starttime,
                    "endtime": endtime,
                    "auto": True,
                    "Manual": False
                }
            )
    data = response_data['response'][0]
    data['video_url'] = video_url
    data['faces'] = faces_list
    ffmpeg_extract_audio( f'Media/{videoName}', "test.wav", bitrate=3000, fps=44100 )
    r = sr.Recognizer()
    with sr.AudioFile( "test.wav" ) as source:
        audio = r.record( source )
    try:
        print( "The audio file contains: " + r.recognize_google( audio ) )
        transcript = r.recognize_google( audio )
        data['transcript'] = transcript
    except sr.UnknownValueError:
        print( "Google Speech Recognition could not understand audio" )
        data['transcript'] = "Google Speech Recognition could not understand audio"
    except sr.RequestError as e:
        print( f"Could not request results from Google Speech Recognition service; {e}" )
        data['transcript'] = f"Could not request results from Google Speech Recognition service; {e}"
    if os.path.exists( f'Media/{videoName}' ):
        os.remove( f'Media/{videoName}' )
    return data


@app.post( '/downloadRedactedVideo' )
async def download_redacted_video(item: models.downloadVideo):
    Aws_access_key_id = 'AKIAIFWF3UATSC6JEWBA'
    Aws_secret_access_key = '4Jd0MizjQFaJJamOuEsGsouEMQOfTLBqWsPeK9L9'
    s3 = boto3.client( 's3',
                       aws_access_key_id=Aws_access_key_id,
                       aws_secret_access_key=Aws_secret_access_key,
                       )

    try:
        video_url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': item.bucket_name, 'Key': f'{item.user_id}/video/{item.video_id}/{item.video_name}'},
            ExpiresIn=3600,
        )
    except:
        video_url = ''

    return {'video_url': video_url}


# def combine_audio(vidname, audname, outname, fps=25):
#     import moviepy.editor as mpe
#     my_clip = mpe.VideoFileClip( vidname )
#     audio_background = mpe.AudioFileClip( audname )
#     final_clip = my_clip.set_audio( audio_background )
#     final_clip.write_videofile( outname, fps=fps )

def processVideo(item):
    vs = cv2.VideoCapture( f'Media/{item.video_name}' )
    # else:
    # data =os.listdir('D:\VideoRedactAPI\VideoRedactAPI\Media')
    #
    # print( data[0] )
    # os.rename(f'D:\VideoRedactAPI\VideoRedactAPI\Media\{data[0]}',f'D:\VideoRedactAPI\VideoRedactAPI\Media\{item.video_name}' )
    # vs = cv2.VideoCapture( f'D:\VideoRedactAPI\VideoRedactAPI\Media\{data[0]}' )
    # print( data[0] )

    frame_number = vs.get( cv2.CAP_PROP_FRAME_COUNT )
    fps = int( vs.get( cv2.CAP_PROP_FPS ) )
    seconds = int( frame_number / fps )
    print( seconds )
    count = 0
    writer = None
    # Load a sample picture and learn how to recognize it.
    # listofimages = item.image_url
    # print( listofimages )
    i = 0

    # print( img )

    # knownface = face_recognition.load_image_file( f'D:/VideoRedactAPI/videos/{img}' )
    # knownface_encoding = face_recognition.face_encodings( knownface )[0]
    #
    # known_face_encodings = [
    #     knownface_encoding
    # ]

    # Initialize some variables
    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True
    try:
        while True:
            # Grab a single frame of video
            ret, frame = vs.read()
            faces = fd.ssd_detect( frame )

            for (x, y, w, h) in faces:
                try:
                    # image = np.uint8( faces )
                    count += 1  # i.e. at 30 fps, this advances one second
                    vs.set( 1, count )

                    # cv2.rectangle( img, (x, y), (x + w, y + h), (0, 0, 255), 2 )
                    crop_img = frame[y:y + h, x:x + w]

                    # try:
                    #     unknown_encoding = face_recognition.face_encodings( crop_img )[0]
                    # except:
                    #     continue
                    # matches = face_recognition.compare_faces( known_face_encodings, unknown_encoding )
                    # face_distances = face_recognition.face_distance( known_face_encodings, unknown_encoding )

                    # if face_distances >.50:
                    #     print( 'face distance',+face_distances )
                    #     print( 'matched' )
                    # cv2.rectangle( frameq, (x-40, y-50), (x + w, y + h), (0, 0, 255), 2 )
                    # redcationtype='simple'
                    if item.readctiontype == "simple":
                        face = anonymize_face_simple( crop_img, factor=float( item.level_simple ) )
                        # cv2.imshow('test',face)
                        # cv2.waitKey(1)

                    elif item.readctiontype == 'pixelate':

                        face = anonymize_face_pixelate( crop_img,
                                                        blocks=int( item.level_pixelate ) )
                    # cv2.imshow('tes',crop_img)
                    frame[y:y + h, x:x + w] = face
                    # cv2.waitKey(1)


                except:
                    continue
            count += 1  # i.e. at 30 fps, this advances one second
            vs.set( 1, count )
            frametime = count / fps
            if writer is None:
                fourcc = cv2.VideoWriter_fourcc( *"MP4V" )
                writer = cv2.VideoWriter( 'Media/Converted.mp4', fourcc, 20,
                                          (frame.shape[1], frame.shape[0]), True )
                # if the writer is not None, write the frame with recognized
                # faces to disk
            if writer is not None:
                writer.write( frame )

            writer.write( frame )
            # cv2.imshow( 'Video', frame )
            # cv2.waitKey( 1 )

            # Hit 'q' on the keyboard to quit!
            # if cv2.waitKey( 1 ) & 0xFF == ord( 'q' ):
            #     break
        vs.release()
        cv2.destroyAllWindows()

        return fps


    except Exception as e:
        print( e )
        return False


async def read_video(item, s3):
    result = processVideo( item )

    vs = cv2.VideoCapture(f'Media/{item.video_name}' )
    print(item.video_name)
    fps = int( vs.get( cv2.CAP_PROP_FPS ) )
    print(fps)
    vs.release()

    ffmpeg_extract_audio( f'Media/{item.video_name}', 'Media/audio.wav', bitrate=3000, fps=4400 )
    # import moviepy.editor as mp
    # my_clip = mp.VideoFileClip( f'Media/{item.video_name}' )
    # my_clip.audio.write_audiofile( 'Media/audio.wav', fps=fps )



    def combine_audio(vidname, audname, outname, fps):
        import moviepy.editor as mpe
        my_clip = mpe.VideoFileClip( vidname )
        audio_background = mpe.AudioFileClip( audname )
        final_clip = my_clip.set_audio( audio_background )
        final_clip.write_videofile( outname, fps=fps )

    combine_audio( f'Media/Converted.mp4', 'Media/audio.wav', 'Media/Audio_video.mp4', fps )

    print( f'Video Redacted {result}' )

    Aws_access_key_id = 'AKIAIFWF3UATSC6JEWBA'
    Aws_secret_access_key = '4Jd0MizjQFaJJamOuEsGsouEMQOfTLBqWsPeK9L9'
    # bucketName = 'original-video'
    #
    # region = 'us-east-2'
    s3 = boto3.client( 's3',
                       aws_access_key_id=Aws_access_key_id,
                       aws_secret_access_key=Aws_secret_access_key,
                       )

    try:
        print( 'uploading in progress' )
        s3.upload_file( 'Media/Audio_video.mp4', 'redacted-video',
                        item.user_id + f'/video/{item.video_id}/{item.video_name}' )

        body = {
            "data_id": 68,
            "video_id": item.video_id,
            "message": "Reacted Video upload success"
        }
        headers = {"x-api-key": "3loi6egfa0g04kgwg884oo88sgccgockg0o"}
        data = requests.post( f'http://63.142.254.143/GovQuest/api/Redactions/edit_video/{item.user_id}', data=body,
                              headers=headers )
        print( data.text )
    except Exception as er:
        print( er, 'file not uploded' )
    if os.path.exists( 'Media' ):
        shutil.rmtree( 'Media' )


#             vs.release()
#             cv2.destroyAllWindows()

# video_stream = ffmpeg.input( f'Media/{item.video_name}.mp4' )
# audio_stream = ffmpeg.input( 'test.wav' )
# ffmpeg.output( audio_stream, video_stream, 'out.mp4' ).run()
# combine_audio( 'Media/Converted.mp4', 'test.wav', f'Media/{item.video_name}.mp4', fps=25 )


@app.post( '/getEditedVideo' )
async def get_edited_video(background_tasks: BackgroundTasks, item: models.getEditedVideo):
    Aws_access_key_id = 'AKIAIFWF3UATSC6JEWBA'
    Aws_secret_access_key = '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'
    s3 = boto3.client( 's3',
                       aws_access_key_id=Aws_access_key_id,
                       aws_secret_access_key=Aws_secret_access_key,
                       )
    print( f'Media/{item.video_name}' )
    with open( f'Media/{item.video_name}', 'wb' ) as f:
        s3.download_fileobj( 'original-video', f'{item.user_id}/video/{item.video_id}/{item.video_name}', f )
        f.close()
    background_tasks.add_task( read_video, item, s3 )
    body = {
        "data_id": 68,
        "video_id": item.video_id,
        "redact_video_name": item.video_name,
        "redact_video_url": "response_url",
        "message": "Redacted video uploading"
    }
    headers = {"x-api-key": "3loi6egfa0g04kgwg884oo88sgccgockg0o"}
    data = requests.post( f'http://63.142.254.143/GovQuest/api/Redactions/edit_video/{item.user_id}', data=body,
                          headers=headers )
    print( data.text )
    response_redacted = json.loads( data.text )

    return response_redacted
    # h = 0
    # for img in os.listdir( r'D:\VideoRedactAPI\videos' ):
    # if h==0:


@app.get( '/getRedactedVideoData/{user_id}' )
async def getRedactedVideoData(user_id: str, video_id: str):
    Aws_access_key_id = 'AKIAIFWF3UATSC6JEWBA'
    Aws_secret_access_key = '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'
    # bucketName = 'original-video'
    #
    # region = 'us-east-2'
    s3 = boto3.client( 's3',
                       aws_access_key_id=Aws_access_key_id,
                       aws_secret_access_key=Aws_secret_access_key,
                       )

    Headers = {"x-api-key": "3loi6egfa0g04kgwg884oo88sgccgockg0o"}

    response_redact_data = requests.get(
        f'http://63.142.254.143/GovQuest/api/Redactions/video_details/{video_id}',
        headers=Headers
    )
    response_redact_data = json.loads( response_redact_data.text )
    videoID = response_redact_data['response'][0]['video_id']
    message = response_redact_data['response'][0]['message']
    videoName = response_redact_data['response'][0]['video_name']
    video_upload_dt = response_redact_data['response'][0]['uploaded_dt']
    if message != 'Redacted video uploading':

        video_redcated_url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': 'redacted-video', 'Key': f'{user_id}/video/{video_id}/{videoName}'},
            ExpiresIn=3600,
        )
        data = {"redacted_url": video_redcated_url,
                "video_name": videoName,
                "video_upload_dt": video_upload_dt
                }
    else:
        data = {"redacted_url": 'video_redcated_url',
                "video_name": videoName,
                "video_upload_dt": video_upload_dt
                }

    return data
