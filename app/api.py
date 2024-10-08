from flask import Flask, jsonify, request
from app import restapp, table, s3, bucket_name
import boto3

@restapp.route('/')
def welcome():
    table.put_item(
            Item={
                "id": 1,
                "name": "Test User 1"
            }
        )
    table.put_item(
            Item={
                "id": 2,
                "name": "Test User 2"
            }
        )
    table.put_item(
            Item={
                "id": 3,
                "name": "Test User 3"
            }
        )        
    return '<h3>Guest List</h3>'

@restapp.route('/items', methods=['GET'])
def get_items():
    response = table.scan()
    items = response['Items']
    return jsonify(items), 200

@restapp.route('/item/<int:item_id>', methods=['GET'])
def get_item(item_id):

    response = table.query(KeyConditionExpression=boto3.dynamodb.conditions.Key('id').eq(item_id))
    item = response['Items']
    if item:
        return jsonify(item), 200
    return jsonify({'error': 'Guest number not found'}), 404


@restapp.route('/item', methods=['POST'])
def create_item():
    data = request.get_json()
    item_id = data.get('id')
    name = data.get('name')
    try:
        response = table.query(KeyConditionExpression=boto3.dynamodb.conditions.Key('id').eq(item_id))
        if response.get('Items'):
            return jsonify({'error': 'Guest already exists'}), 400
        
        table.put_item(Item={'id': item_id, 'name': name})
        s3.put_object(Bucket=bucket_name, Key=str(item_id), Body=name)
        return jsonify({'id': item_id, 'name': name}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@restapp.route('/item/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    data = request.get_json()
    name = data.get('name')
    try:
        response = table.query(KeyConditionExpression=boto3.dynamodb.conditions.Key('id').eq(item_id))
        if not response.get('Items'):
            return jsonify({'error': 'Guest not found'}), 404  
    #response = table.get_item(Key={'id': item_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    table.update_item(
        Key={'id': item_id},
        UpdateExpression="set #nm = :n",
        ExpressionAttributeNames={'#nm': 'name'},
        ExpressionAttributeValues={':n': name}
    )
    s3.put_object(Bucket=bucket_name, Key=str(item_id), Body=name)
    return jsonify({'id': item_id, 'name': name}), 200

@restapp.route('/item/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    response = table.query(KeyConditionExpression=boto3.dynamodb.conditions.Key('id').eq(item_id))
    if not response.get('Items'):
        return jsonify({'error': 'Guest not found'}), 404

    table.delete_item(Key={'id': item_id})
    s3.delete_object(Bucket=bucket_name, Key=str(item_id))
    return '', 204

if __name__ == '__main__':
    restapp.run(debug=True)
