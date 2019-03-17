##########################################################################################
# This script will spin up EC2 nodes for our cluster                                     #
# It assumes that:                                                                       #
# - you have a working AWS CLI (of which we will use the  credentials)                   #
# - the AWS CLI credentials refer to an admin user                                       #
# - you have set up a role, a VPC and a security group                                   #
#   using the instructions on the Getting started page                                   #
#   https://docs.aws.amazon.com/eks/latest/userguide/getting-started.html                #
# - you have initiated a cluster before                                                  #
#                                                                                        #
# Parameters:                                                                            #
# --clusterName         name of the cluster, default myCluster                           #
# --stackName           CloudFormation stack for VPC and security group, default eks-vpc #
# --instanceType        used instance type, default t2.small                             #
#                                                                                        #
# At this point, we use Kubernetes version 1.11                                          #
##########################################################################################


import boto3
import yaml
import argparse
from os.path import expanduser
k8Version="1.11"


##########################################################################################
# Parse parameters                                                                       #
##########################################################################################

parser = argparse.ArgumentParser()
parser.add_argument("--clusterName",
                    type=str,
                    default="myCluster",
                    help="Name of the cluster that we will create")


parser.add_argument("--stackName",
                    type=str,
                    default="eks-vpc",
                    help="Name of the cloud formation stack containing VPC and security group")


parser.add_argument("--instanceType",
                    type=str,
                    default="t2.small",
                    help="Name of instance type we use")


args = parser.parse_args()
clusterName = args.clusterName
stackName = args.stackName
instanceType = args.instanceType

print("working with cluster ", clusterName)
print("Using CloudFormation stack ", stackName)

##########################################################################################
# Collect data                                                                           #
##########################################################################################



cloudFormation = boto3.client('cloudformation')
response = cloudFormation.describe_stack_resources(StackName = stackName, LogicalResourceId="VPC")
vpcId = response['StackResources'][0]['PhysicalResourceId']
print("Found VPC ID: ", vpcId)


response = cloudFormation.describe_stack_resources(StackName = stackName, LogicalResourceId="ControlPlaneSecurityGroup")
secGroupId = response['StackResources'][0]['PhysicalResourceId']
print("Found security group ID: ", secGroupId)


ec2 = boto3.resource('ec2')
vpc = ec2.Vpc(vpcId)
subnets = [subnet.id for subnet in vpc.subnets.all()]
print("Found subnets: ", subnets)

##########################################################################################
# Define remaining parameters                                                            #
##########################################################################################

nodeGroupName = "eksNodeGroup"
sshKeyPair = "eksNodeKey"
# This AMI works for eu-central-1 with Kubernetes v1.11
amiId = "ami-032ed5525d4df2de3"
stackName = "eks-auto-scaling-group-" + clusterName
templateURL = 'https://amazon-eks.s3-us-west-2.amazonaws.com/cloudformation/2019-02-11/amazon-eks-nodegroup.yaml'

##########################################################################################
# Create auto-scaling group                                                              #
##########################################################################################


params = [
  {'ParameterKey' : 'KeyName' , 
   'ParameterValue' : sshKeyPair },
  {'ParameterKey' : 'NodeImageId' , 
   'ParameterValue' : amiId },
  {'ParameterKey' : 'NodeInstanceType' , 
   'ParameterValue' : instanceType },
  {'ParameterKey' : 'NodeAutoScalingGroupMinSize' , 
   'ParameterValue' : '1' },
  {'ParameterKey' : 'NodeAutoScalingGroupMaxSize' , 
   'ParameterValue' : '3' },
  {'ParameterKey' : 'NodeAutoScalingGroupDesiredCapacity' , 
   'ParameterValue' : '2' },
  {'ParameterKey' : 'ClusterName' , 
   'ParameterValue' : clusterName },
  {'ParameterKey' : 'NodeGroupName' , 
   'ParameterValue' : nodeGroupName },
  {'ParameterKey' : 'ClusterControlPlaneSecurityGroup' , 
   'ParameterValue' : secGroupId },
  {'ParameterKey' : 'VpcId' , 
   'ParameterValue' : vpcId },
  {'ParameterKey' : 'Subnets' , 
   'ParameterValue' : ",".join(subnets) },
]

cloudFormation.create_stack(
  StackName = stackName, 
  TemplateURL = templateURL,
  Parameters = params,
  Capabilities = ['CAPABILITY_IAM'])

print("Submitted creation request for auto-scaling group stack, now waiting for completion")
waiter = cloudFormation.get_waiter('stack_create_complete')
waiter.wait(StackName=stackName)

# Extract node instance role 
resource = boto3.resource('cloudformation')
stack = resource.Stack(stackName)
for i in stack.outputs:
  if (i['OutputKey'] == "NodeInstanceRole"):
    nodeInstanceRole = i['OutputValue']

print("Using node instance role ", nodeInstanceRole)

##########################################################################################
# Inform Kubernetes about node instance role                                             #
##########################################################################################


from kubernetes import client, config
from kubernetes.client.rest import ApiException
config.load_kube_config()
v1 = client.CoreV1Api() 

# 
# We need to create a config map in the namespace kube-system
# 
namespace = "kube-system"
configMapName = "aws-auth"


#
# Delete old config maps in case it exists
#
body = client.V1DeleteOptions()
body.api_version="v1"
try:
  v1.delete_namespaced_config_map(name="aws-auth", namespace="kube-system", body = body)
except ApiException as e:
  pass

#
# Create new config map
#
body = client.V1ConfigMap()
body.api_version="v1"
body.metadata = {}
body.metadata['name'] = configMapName
body.metadata['namespace'] = namespace

body.data = {}
body.data['mapRoles'] = "- rolearn: " + nodeInstanceRole +  "\n  username: system:node:{{EC2PrivateDNSName}}\n  groups:\n    - system:bootstrappers\n    - system:nodes\n"

print("Submitting request to create config map")
response = v1.create_namespaced_config_map(namespace, body)
print("Done")



