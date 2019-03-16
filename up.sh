# 
# Bring up the cluster
# 
python3 create_cluster.py
#
# and the nodes
#
python3 create_nodes.py

#
# Open security group for incoming SSH connections from my IP
#
SEC_GROUP_ID=$(aws ec2 describe-instances --output text --query Reservations[0].Instances[0].SecurityGroups[0].GroupId)
myIP=$(wget -q -O- https://ipecho.net/plain)
aws ec2 authorize-security-group-ingress --group-id $SEC_GROUP_ID --port 22 --protocol tcp --cidr "$myIP/32"

#
# Open terminals to log into the two nodes
NODE=0
IP=$(aws ec2 describe-instances --filters Name=key-name,Values=eksNodeKey --output text --query Reservations[$NODE].Instances[0].PublicIpAddress)
gnome-terminal -e "ssh -i ~/eksNodeKey.pem ec2-user@$IP" &
NODE=1
IP=$(aws ec2 describe-instances --filters Name=key-name,Values=eksNodeKey --output text --query Reservations[$NODE].Instances[0].PublicIpAddress)
gnome-terminal -e "ssh -i ~/eksNodeKey.pem ec2-user@$IP" &




