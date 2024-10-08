# Docker Compose for Multiple Containers 
The project serves the purpose to run two containers, one for rest-based application and other for localstack.

### Project Description
The project serves the purpose to view the guest list and add/update/remove a guest.
This project contains a Dockerized REST API built with Flask. The API includes endpoints for GET, POST, PUT, and DELETE operations on a guest list. The project also includes automated tests for each endpoint.
<BR>



## REST API for Guest List

The REST API is built using Flask, and it includes the following endpoints that perform specific functions on the guest list:

- GET /api/items: Retrieves all guests.
- GET /api/item/<item_id>: Retrieves a specific guest by ID.
- POST /api/item: Creates a new guest if it doesn't already exists.
- PUT /api/item/<item_id>: Updates an existing guest by ID if it already exists.
- DELETE /api/item/<item_id>: Deletes an existing guest by ID.

## Running the API

### CURL commands for executing each endpoint
<BR>
GET all guests

```sh
curl -X GET http://127.0.0.1:5001/items
```

GET specific guest
```sh
curl -X GET http://127.0.0.1:5001/item/3
```
POST add new guest
```sh
curl -X POST http://127.0.0.1:5001/item -H "Content-Type: application/json" -d '{"id": 5, "name": "Test User 5"}'
```
PUT update specific guest
```sh
curl -X PUT http://127.0.0.1:5001/item/5 -H "Content-Type: application/json" -d '{"name": "Updated Test User 5"}'
```
DELETE remove specific guest
```sh
curl -X DELETE http://127.0.0.1:5001/item/5
```
<BR>
To run the application, execute the docker build and run commands or use the provided `runapi.sh` script:

### Using Docker Commands
#### Docker Build
```sh
docker-compose build
```
#### Docker Run
```sh
docker-compose up 
```
### Using Script
```sh
./runapi.sh
```
<BR>

## Testing REST API for Guest List
The project includes automated tests for each REST API endpoint.
These tests are implemented using pytest.
<BR>
The tests cover the following scenarios:
<BR>
GET /api/items: Verifies status code 200 for retrieving all guests. 
<BR>
GET /api/item/<item_id>: Verifies status code 200 for retrieving a specific guest by ID and 404 for non-existent guests. 
<BR>
POST /api/item: Verifies status code 201 for creating a new guest and 400 for already existing guests.
<BR> 
PUT /api/item/<item_id>: Verifies status code 200 for updating an existing guest and 404 for non-existent guests. 
<BR>
DELETE /api/item/<item_id>: Verifies status code 204 for deleting a guest and 404 for non-existent guests.

## Running the Tests

To run the tests for each endpoint, execute the docker build and run commands or use the provided `runtest.sh` script:

### Using Docker Commands
#### Docker Build
```sh
docker-compose -f docker-compose.test.yml build test
```
#### Docker Run
```sh
docker-compose -f docker-compose.test.yml up test
```
### Using Script
```sh
./runtest.sh
```

## Storage
### DynamoDB Table Structure
The DynamoDB table, GuestTable, has the following schema:

id (Number): The unique identifier for each guest (Partition Key).
<br>
name (String): The name of the guest.
<br>
### S3 Bucket Structure
The S3 bucket, guest-bucket, stores objects with the following structure:

The key is the id of the guest.<br>
The value is the name of the guest.