# 
# Bring up the cluster
# 
python3 create_cluster.py
#
# and the nodes
#
amiId=$(aws ec2 describe-images  --filters Name=name,Values=\*eks-node-1.11\* --query 'reverse(sort_by(Images, &CreationDate))[0].ImageId' --output text)
echo "AMI $amiId seems to be the latest version"
python3 create_nodes.py --amiId=$amiId

#
# Install nginx ingress controller following the instructions on
# https://kubernetes.github.io/ingress-nginx/deploy/
#
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/master/deploy/mandatory.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/master/deploy/provider/aws/service-l4.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/master/deploy/provider/aws/patch-configmap-l4.yaml


#
# Open security group for incoming SSH connections from my IP
#
SEC_GROUP_ID=$(aws ec2 describe-instances --output text --filters Name=tag-key,Values=kubernetes.io/cluster/myCluster Name=instance-state-name,Values=running --query Reservations[0].Instances[0].SecurityGroups[0].GroupId)
myIP=$(wget -q -O- https://ipecho.net/plain)
aws ec2 authorize-security-group-ingress --group-id $SEC_GROUP_ID --port 22 --protocol tcp --cidr "$myIP/32"

#
# Open terminals to log into the two nodes. We assume that the key we are using is ~/.keys/eksNodeKey, replace this in 
# the ssh command below by your specific location
#
for NODE in `seq 0 1`; 
do 
  echo "Creating SSH session for node $NODE" 
  IP=$(aws ec2 describe-instances --filters Name=key-name,Values=eksNodeKey Name=instance-state-name,Values=running --output text --query Reservations[$NODE].Instances[0].PublicIpAddress)
  gnome-terminal -e "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i ~/.keys/eksNodeKey.pem ec2-user@$IP" &
done






