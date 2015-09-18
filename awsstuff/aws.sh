#aws cloudsearch create-domain --domain-name rookie > created
#cat created | jsawk 'return this.DomainStatus.DomainId'
#"DomainId": "878503168987/rookie" 
#aws cloudsearch describe-domains --domain-names rookie
ENDPOINT=$(aws cloudsearch describe-domains --domain-names rookieversion3 | jsawk 'return this.DomainStatusList[0].DocService.Endpoint')
aws cloudsearchdomain --endpoint-url 'http://'$ENDPOINT upload-documents --content-type application/json --documents data/aws/0.json
aws cloudsearchdomain --endpoint-url 'http://'$ENDPOINT upload-documents --content-type application/json --documents data/aws/1.json
aws cloudsearchdomain --endpoint-url 'http://'$ENDPOINT upload-documents --content-type application/json --documents data/aws/2.json
aws cloudsearchdomain --endpoint-url 'http://'$ENDPOINT upload-documents --content-type application/json --documents data/aws/3.json
aws cloudsearchdomain --endpoint-url 'http://'$ENDPOINT upload-documents --content-type application/json --documents data/aws/4.json
aws cloudsearchdomain --endpoint-url 'http://'$ENDPOINT upload-documents --content-type application/json --documents data/aws/5.json

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

#ssh -i awsstuff/devenv-key.pem ubuntu@52.27.242.183

# aws ec2 terminate-instances --instance-ids i-5c24d5aa
