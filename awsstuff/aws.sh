# https://hub.docker.com/_/postgres/

# ssh -i "awsstuff/two" ubuntu@54.191.10.239

# Deployment:
# ON AN EC2 Box...
# install docker on ubuntu
# clone rookie repo
# cd to Docker in rookie rep
# run $docker build -t webapp . to build the webapp
# on ubuntu ec2 box, set up ufw to allow ssh and port 80
# add new server to rookie security group in aws. aws has servers off internet by default

# POSTGRES ...
# Then you need to build another docker image to runpostgres. 
# I followed this tutorial: https://docs.docker.com/engine/examples/postgresql_service/
# once you are "in" the postgres container, you can setup db="rookie" pw="rookie" user="rookie"
# see instructions.sh in awsstuff for details on the postgres db.

# SENDING FILES:
# On your local machine run...
# run awsstuff/send_to_server.sh

# RUN THE APP: run a web app container that links to the postgres container 
# Some of the requirements.txt hit errors and need to be manually installed w/ pip
# sudo docker run -i -t -v /home/ubuntu/data/lens_processed/:/home/ubuntu/data/lens_processed/  -p 80:80 --link some-postgres:localhost webapp:latest /bin/bash


# VARIOUS LINKS
# http://stackoverflow.com/questions/19688314/how-do-you-attach-and-detach-from-dockers-process
# http://stackoverflow.com/questions/29956500/docker-public-registry-push-fails-repository-does-not-exist
