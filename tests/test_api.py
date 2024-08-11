import os
import sys
import pytest
from flask import Flask
import boto3
from botocore.exceptions import ClientError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import restapp


@pytest.fixture(scope='module')
def client():
    localstack_url = 'http://localhost:7777'
    
    session = boto3.Session(
        aws_access_key_id='test',
        aws_secret_access_key='test',
        region_name='us-east-1'
    )

# Configure AWS clients 
    dynamodb = session.resource('dynamodb', region_name='us-east-1', endpoint_url='http://localstack:7777')
    s3 = session.client('s3', region_name='us-east-1', endpoint_url='http://localstack:7777')

    
    # DynamoDB table
    table_name = 'GuestTable'
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'
                }
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
    
    # S3 bucket
    bucket_name = 'guest-bucket'
    try:
        s3.create_bucket(Bucket=bucket_name)
    except ClientError as e:
        if e.response['Error']['Code'] != 'BucketAlreadyExists':
            raise

    restapp.config['TESTING'] = True

    with restapp.test_client() as client:
        client.dynamodb = dynamodb
        client.table = table
        client.s3 = s3
        client.bucket = bucket_name
        yield client

def test_welcome(client):
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'<h3>Guest List</h3>' in rv.data




#For each test, the database item and S3 object should match.

# Sending a GET request with appropriate parameters returns expected JSON from the database
def test_get_with_valid_parameters(client):
    client.table.put_item(Item={'id': 1, 'name': 'Test User 1'})
    response = client.get('/item/1')
    assert response.status_code == 200
    assert response.json == [{'id': '1', 'name': 'Test User 1'}]

# Sending a GET request that finds no results returns the appropriate response
def test_get_no_results(client):
    response = client.get('/item/0')
    assert response.status_code == 404
    assert response.json == {'error': 'Guest number not found'}

# Sending a GET request with no parameters returns all items
def test_get_no_parameters(client):
    client.table.put_item(Item={'id': 1, 'name': 'Test User 1'})
    client.table.put_item(Item={'id': 2, 'name': 'Test User 2'})
    response = client.get('/items')
    assert response.status_code == 200
    assert len(response.json) >= 2  # Adjust based on setup

#- Sending a GET request with incorrect parameters returns the appropriate response
def test_get_incorrect_parameters(client):
    response = client.get('/item?name=1')
    assert response.status_code == 405

# Sending a POST request results in the JSON body being stored as an item in the database, and an object in an S3 bucket
def test_post_create_item(client):
    item_id = 9
    json_data = {'id': item_id, 'name': 'Test User 9'}

    response = client.post('/item', json=json_data)
    assert response.status_code == 201

    db_response = client.table.get_item(Key={'id': item_id})
    assert 'Item' in db_response
    assert db_response['Item']['name'] == json_data['name']

    s3_response = client.s3.get_object(Bucket=client.bucket, Key=str(item_id))
    s3_data = s3_response['Body'].read().decode('utf-8')
    assert s3_data == json_data['name']

# Sending a duplicate POST request returns the appropriate response
def test_create_existing_item(client):
    client.table.put_item(Item={'id': 1, 'name': 'Test User 1'})
    response = client.post('/item', json={'id': 1, 'name': 'Test User 1'})
    assert response.status_code == 400
    assert response.json == {'error': 'Guest already exists'}

# Sending a PUT request that targets an existing resource results in updates to the appropriate item in the database and object in the S3 bucket
def test_update_item(client):
    client.table.put_item(Item={'id': 1, 'name': 'Test User 1'})
    response = client.put('/item/1', json={'name': 'Updated Test User 1'})
    assert response.status_code == 200
    assert response.json == {'id': 1, 'name': 'Updated Test User 1'}

    db_response = client.table.get_item(Key={'id': 1})
    assert db_response['Item']['name'] == 'Updated Test User 1'

    s3_response = client.s3.get_object(Bucket=client.bucket, Key='1')
    s3_data = s3_response['Body'].read().decode('utf-8')
    assert s3_data == 'Updated Test User 1'

# Sending a PUT request with no valid target returns the appropriate response
def test_update_item_not_found(client):
    response = client.put('/item/99', json={'name': 'Updated User 99'})
    assert response.status_code == 404
    assert response.json == {'error': 'Guest not found'}

# Sending a DELETE request results in the appropriate item being removed from the database and object being removed from the S3 bucket
def test_delete_item(client):
    client.table.put_item(Item={'id': 1, 'name': 'Test User 1'})
    response = client.delete('/item/1')
    assert response.status_code == 204

    db_response = client.table.get_item(Key={'id': 1})
    assert 'Item' not in db_response

    try:
        client.s3.get_object(Bucket=client.bucket, Key='1')
    except ClientError as e:
        assert e.response['Error']['Code'] == 'NoSuchKey'

# Sending a DELETE request with no valid target returns the appropriate response
def test_delete_item_not_found(client):
    response = client.delete('/item/99')
    assert response.status_code == 404
    assert response.json == {'error': 'Guest not found'}
