
#
# Get cluster name
#
clusterName=$1
if [ "X$clusterNameX" = "X" ]
then
  clusterName="myCluster"
fi
echo "Bringing down cluster $clusterName"


#
# First bring down nginx ingress controller to make sure that
# the ELB is deleted as well. This will also destroy the 
# associated security group
#
echo "Shutting down ingress controller"
kubectl delete svc ingress-nginx --namespace=ingress-nginx
sleep 5

#
# Next bring down the CloudFormation stack that we did use
# for our auto scaling group
#
stackName="eks-auto-scaling-group-$clusterName"
echo "Deleting CloudFormation stack $stackName"
aws cloudformation delete-stack --stack-name $stackName

#
# and finally delete cluster
#
echo "Now submitting cluster deletion request"
aws eks delete-cluster --name $clusterName --output json
echo "Done, now waiting for completion - if you want, hit Ctrl-C to exit"

status="DELETING"
while [ "$status" = "DELETING" ]
do
  status=$(aws eks describe-cluster --name $clusterName --output text --query "cluster.status" 2>/dev/null )
  sleep 5
done

