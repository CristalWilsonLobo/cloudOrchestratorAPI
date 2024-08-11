#!/bin/bash
docker-compose -f docker-compose.test.yml build test
docker-compose -f docker-compose.test.yml up test

#docker build -f Dockerfile.test -t rest-api-test .
#docker run rest-api-test