#!/bin/bash

docker-compose -f docker-compose.test.yml up --abort-on-container-exit --exit-code-from test

#docker build -f Dockerfile.test -t rest-api-test .
#docker run rest-api-test