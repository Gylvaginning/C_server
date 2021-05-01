#!/bin/bash

docker stop numerounodocker

docker rm numerounodocker

docker build -t numerounodocker .

docker run -dit --name numerounodocker -p 8081:80 numerounodocker

docker update --cpu-shares 512 numerounodocker
