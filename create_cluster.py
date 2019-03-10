##########################################################################################
# This script will create a EKS cluster and set up kubectl to  connect to it.            #
# It assumes that:                                                                       #
# - you have a working AWS CLI (of which we will use the  credentials)                   #
# - the AWS CLI credentials refer to an admin user                                       #
# - you have set up a role, a VPC and a security group                                   #
#   using the instructions on the Getting started page                                   #
#   https://docs.aws.amazon.com/eks/latest/userguide/getting-started.html                #
#                                                                                        #
# Parameters:                                                                            #
# --clusterName         name of the cluster, default myCluster                           #
# --eksRoleName         name of the IAM role for the cluster, default EKSEC2UserRole     #
# --stackName           CloudFormation stack for VPC and security group, default eks-vpc #
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

parser.add_argument("--eksRoleName",
                    type=str,
                    default="EKSEC2UserRole",
                    help="Name of the EKS service IAM role")


parser.add_argument("--stackName",
                    type=str,
                    default="eks-vpc",
                    help="Name of the cloud formation stack containing VPC and security group")


args = parser.parse_args()
clusterName = args.clusterName
eksRoleName = args.eksRoleName
stackName = args.stackName

print("Creating cluster ", clusterName)
print("Using IAM role ", eksRoleName)
print("Using CloudFormation stack ", stackName)

##########################################################################################
# Collect data                                                                           #
##########################################################################################


# Create IAM client
iam = boto3.client('iam')

# Get role information
response = iam.get_role(RoleName=eksRoleName)
roleArn = response['Role']['Arn']
print("Found role ARN: ", roleArn)


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
# Create cluster                                                                         #
##########################################################################################


eks = boto3.client("eks")
r = eks.create_cluster(name=clusterName, version=k8Version, roleArn = roleArn, resourcesVpcConfig = {'subnetIds' : subnets, 'securityGroupIds' : [secGroupId]})
print("Submitted create command, response status is : ", r['cluster']['status'])
print("Now waiting for cluster creation to be completed - be patient, this can take up to ten minutes")
waiter = eks.get_waiter("cluster_active")
waiter.wait(name=clusterName)

##########################################################################################
# Update kubectl configuration                                                           #
##########################################################################################


print("Cluster available, now creating config file")
cluster = eks.describe_cluster(name=clusterName)
cluster_cert = cluster["cluster"]["certificateAuthority"]["data"]
cluster_ep = cluster["cluster"]["endpoint"]
cluster_arn = cluster["cluster"]["arn"]

cluster_config = {
        "apiVersion": "v1",
        "kind": "Config",
        "clusters": [
            {
                "cluster": {
                    "server": str(cluster_ep),
                    "certificate-authority-data": str(cluster_cert)
                },
                "name": cluster_arn
            }
        ],
        "contexts": [
            {
                "context": {
                    "cluster": cluster_arn,
                    "user": cluster_arn,
                },
                "name": cluster_arn
            }
        ],
        "current-context": cluster_arn,
        "preferences": {},
        "users": [
            {
                "name": cluster_arn,
                "user": {
                    "exec": {
                        "apiVersion": "client.authentication.k8s.io/v1alpha1",
                        "command": "aws-iam-authenticator",
                        "args": [
                            "token", "-i", clusterName
                        ]
                    }
                }
	    }
        ]
}

config_text=yaml.dump(cluster_config, default_flow_style=False)
config_file = expanduser("~") + "/.kube/config"
print("Writing kubectl configuration to ", config_file)
open(config_file, "w").write(config_text)
print("Done")

