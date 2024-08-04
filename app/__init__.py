from flask import Flask
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

restapp = Flask(__name__)

# Configure AWS clients
dynamodb = boto3.resource('dynamodb', region_name='us-east-1', endpoint_url='http://localstack:4566')
s3 = boto3.client('s3', region_name='us-east-1', endpoint_url='http://localstack:4566')

# Guest table in DynamoDB 
table_name = 'GuestTable'
try:
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'
            },
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'N'
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
    table.wait_until_exists()
except dynamodb.meta.client.exceptions.ResourceInUseException:
    table = dynamodb.Table(table_name)

# S3 bucket for storing guest list
bucket_name = 'guest-bucket'
try:
    s3.create_bucket(Bucket=bucket_name)
except s3.exceptions.BucketAlreadyExists:
    pass
except s3.exceptions.BucketAlreadyOwnedByYou:
    pass

from app import api
