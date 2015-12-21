# Deployment:
# install docker
# clone rookie
# cd to Docker
# run $docker build .
# run awsstuff/send_to_server.sh
# set up ufw to allow ssh and port 80
# add new server to rookie securit group. aws has servers off internet by defualt

ssh -i "awsstuff/two" ubuntu@54.191.10.239

# sudo docker run -i -t -v /home/ubuntu/data/lens_processed/:/home/ubuntu/data/lens_processed/  -p 80:80 d328fc0d4cbe /bin/bash

# http://stackoverflow.com/questions/19688314/how-do-you-attach-and-detach-from-dockers-process

#create security group
#aws ec2 create-security-group --group-name rookie --description "Rookie security group"

#authorize IPs. Should limit when I have a set IP
#aws ec2 authorize-security-group-ingress --group-name rookie --protocol tcp --port 22 --cidr 0.0.0.0/0

#Create a key pair
#aws ec2 create-key-pair --key-name devenv-key --query 'KeyMaterial' --output text > /Users/abramhandler/research/rookie/awsstuff/devenv-key.pem

#Limit permissions
#chmod 400 /Users/abramhandler/research/rookie/awsstuff/devenv-key.pem

#Create a micro instance
#aws ec2 run-instances --image-id ami-29ebb519 --count 1 --instance-type t2.micro --key-name devenv-key --security-groups rookie --query 'Instances[0].InstanceId'

#Get the IP for the instance
#aws ec2 describe-instances --instance-ids i-5c24d5aa --query 'Reservations[0].Instances[0].PublicIpAddress'

# ssh -i "awsstuff/two" ec2-user@52.88.14.189
# aws ec2 terminate-instances --instance-ids i-5c24d5aa
