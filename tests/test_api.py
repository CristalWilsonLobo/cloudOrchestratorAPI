import os
import sys
import pytest
from flask import Flask
import boto3
from unittest import TestCase

# Ensure the app module is included in the Python path
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from app import restapp

@pytest.fixture
def client():
def client():
    dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:4566')
    s3 = boto3.client('s3', endpoint_url='http://localhost:4566')
    table = dynamodb.Table('GuestTable')  
    bucket = 'guest-bucket' 

    restapp.config['TESTING'] = True

    with restapp.test_client() as client:

        client.dynamodb = dynamodb
        client.table = table
        client.s3 = s3
        client.bucket = bucket
        yield client

def test_welcome(client):
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'<h3>Guest List</h3>' in rv.data

# Sending a GET request with appropriate parameters returns expected JSON from the database
def test_get_with_valid_parameters():
    response = client.get('/items?item_id=1')
    assert response.status_code == 200
    assert response.json == {'id': '1', 'name': 'Test User 1'}

# Sending a GET request that finds no results returns the appropriate response
def test_get_no_results():
    response = client.get('/items?item_id=0')
    assert response.status_code == 404
    assert response.data == b'Guest number not found'

#Sending a GET request with no parameters returns the appropriate response
def test_get_no_parameters():
    response = client.get('/items')
    assert response.status_code == 400
    assert response.data == b'Missing item_id parameter'

#Sending a GET request with incorrect parameters returns the appropriate response
def test_get_incorrect_parameters():
    response = client.get('/items?guest=1')
    assert response.status_code == 404
    assert response.data == b'Guest number not found'

#Sending a POST request results in the JSON body being stored as an item in the database, and an object in an S3 bucket
def test_post_create_item(self):
    # JSON data for the POST request
    item_id = '5'
    json_data = {'id': item_id, 'name': 'Test User 5'}

    # POST request to create a new item
    response = self.app.post('/item/item_id', json=json_data)
    assert response.status_code == 201

    # Check if item was created in DynamoDB
    db_response = self.table.get_item(Key={'item_id': item_id})
    self.assertIn('Item', db_response)
    self.assertEqual(db_response['Item']['data'], json_data['data'])

    # Check if item was created in S3
    s3_response = self.s3.get_object(Bucket=self.bucket, Key=item_id)
    s3_data = s3_response['Body'].read().decode('utf-8')
    self.assertEqual(s3_data, json_data['data'])

- Sending a duplicate POST request returns the appropriate response
- Sending a PUT request that targets an existing resource results in updates to the appropriate item in the database and object in the S3 bucket
- Sending a PUT request with no valid target returns the appropriate response
- Sending a DELETE request results in the appropriate item being removed from the database and object being removed from the S3 bucket
- Sending a DELETE request with no valid target returns the appropriate response
def test_get_items(client):
    rv = client.get('/items')
    assert rv.status_code == 200
    assert b'Test User 1' in rv.data

def test_get_item(client):
    rv = client.get('/item/1')
    assert rv.status_code == 200
    assert b'Test User 1' in rv.data

def test_get_item_not_found(client):
    rv = client.get('/item/99')
    assert rv.status_code == 404
    assert b'Guest number not found' in rv.data

def test_create_item(client):
    rv = client.post('/item', json={'id': 5, 'name': 'Test User 5'})
    assert rv.status_code == 201
    assert b'Test User 5' in rv.data

def test_create_existing_item(client):
    rv = client.post('/item', json={'id': 1, 'name': 'Test User 1'})
    assert rv.status_code == 400
    assert b'Guest already exists' in rv.data

def test_update_item(client):
    rv = client.put('/item/1', json={'name': 'Updated User 1'})
    assert rv.status_code == 200
    assert b'Updated User 1' in rv.data

def test_update_item_not_found(client):
    rv = client.put('/item/99', json={'name': 'Updated User 99'})
    assert rv.status_code == 404
    assert b'Guest not found' in rv.data

def test_delete_item(client):
    rv = client.delete('/item/1')
    assert rv.status_code == 204

def test_delete_item_not_found(client):
    rv = client.delete('/item/99')
    assert rv.status_code == 404
    assert b'Guest not found' in rv.data
