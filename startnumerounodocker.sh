!#/bin/bash

#sudo systemctl stop docker
#dockerd --userns-remap=default &
#sudo systemctl start docker
docker build -t numerounodocker .
docker run -dit --name numerounodocker -p 8080:80 numerounodocker
docker update --cpu-shares 512 numerounodocker
