import os
import uuid
import ibm_boto3
from ibm_botocore.client import Config
from ibm_botocore.exceptions import ClientError
import ibm_s3transfer.manager
import json
from flask import request


def log_done():
    print("DONE!\n")


def log_client_error(e):
    print("CLIENT ERROR: {0}\n".format(e))


def log_error(msg):
    print("UNKNOWN ERROR: {0}\n".format(msg))


def get_uuid():
    return str(uuid.uuid4().hex)


# Create new file
def create_file(bucket_name, item_name, item_content, credentials):
    print("Creating new item: {0} in bucket: {1}".format(item_name, bucket_name))
    credentials_1 = get_credentials(credentials)
    cos = get_cos(credentials_1)
    try:
        cos.put_object(
            Bucket=bucket_name,
            Key=item_name,
            Body=item_content
        )
        print("Item: {0} created!".format(item_name))
        log_done()
    except ClientError as be:
        log_client_error(be)
    except Exception as e:
        log_error("Unable to create text file: {0}".format(e))


def get_file(filename, credentials):
    credentials_1 = get_credentials(credentials)
    cos = get_cos(credentials_1)
    """Retrieve file from Cloud Object Storage"""
    fileobject = cos.get_object(Bucket=credentials_1['BUCKET'], Key=filename)['Body']
    return fileobject


def load_dict(fileobject):
    """Load the file contents into a Python dict"""
    text = fileobject.read()
    dictformat = json.loads(text)
    return dictformat


def get_credentials(credentials):
    credentials_1 = credentials
    return credentials_1


def get_cos(credentials_1):
    cos = ibm_boto3.client('s3',
                           ibm_api_key_id=credentials_1['IBM_API_KEY_ID'],
                           ibm_service_instance_id=credentials_1['IAM_SERVICE_ID'],
                           ibm_auth_endpoint=credentials_1['IBM_AUTH_ENDPOINT'],
                           config=Config(signature_version='oauth'),
                           endpoint_url=credentials_1['ENDPOINT'])
    return cos
