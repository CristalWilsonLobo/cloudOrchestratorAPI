#!/bin/bash
docker build -f Dockerfile.test -t rest-api-test .
docker run rest-api-test