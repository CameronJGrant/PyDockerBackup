import logging
import boto3
from botocore.exceptions import ClientError
import os
from pathlib import Path

bucket = boto3.resource(
    service_name='s3',
    endpoint_url=os.environ['S3_ENDPOINT_URL'],
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY']
).Bucket(os.environ['S3_BUCKET_NAME'])


def s3_logging(function):
    def wrap(*args, **kwargs):
        try:
            output = function(*args, **kwargs)
        except ClientError as e:
            logging.error(e)
            return False
        return output
    return wrap


@s3_logging
def upload_file(file_name, object_name=None):
    file_name = Path(file_name)

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name.name

    response = bucket.upload_file(str(file_name), object_name)

    return True


@s3_logging
def delete_folder(folder_name):
    response = bucket.objects.filter(Prefix=f"{folder_name}/").delete()
    return True


@s3_logging
def delete_file(file_name):
    response = bucket.objects.filter(Prefix=f"{file_name}").delete()
    return True


@s3_logging
def get_bucket_contents(path=''):
    if path:
        files = bucket.objects.filter(Prefix=f"{path}/")
    else:
        files = bucket.objects.all()
    file_list = []
    for obj in files:
        file_list.append(obj)
    return file_list
