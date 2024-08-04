#!/bin/bash
docker build -f dockerapi -t rest-api .
docker run -p 5000:5000 rest-api