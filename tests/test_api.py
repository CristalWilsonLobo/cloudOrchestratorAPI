import os
import sys
import pytest
from flask import Flask

# Ensure the app module is included in the Python path
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from app import restapp

@pytest.fixture
def client():
    restapp.config['TESTING'] = True
    with restapp.test_client() as client:
        yield client

def test_welcome(client):
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'<h3>Guest List</h3>' in rv.data

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
