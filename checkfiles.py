import datetime
import json
import math
import os
import shutil
import time
import uuid
import bleedfacedetector as fd
import boto3

Aws_access_key_id = 'AKIAIFWF3UATSC6JEWBA'
Aws_secret_access_key = '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'

bucketName = 'original-video'

region = 'us-east-2'
s3 = boto3.client('s3',
              aws_access_key_id=Aws_access_key_id,
              aws_secret_access_key=Aws_secret_access_key,
              )



#
# s3_client = boto3.resource(
#         service_name='s3',
#         region_name=region,
#         aws_access_key_id=Aws_access_key_id,
#         aws_secret_access_key=Aws_secret_access_key
#     )
# bucket = s3_client.Bucket('original-video')
# bucket.objects.all().delete()
List_object = s3.list_objects(Bucket='original-video', Prefix=f'{165}/faces/{64}/' )
print(List_object)




# print(s3.list_objects(Bucket=bucketName))