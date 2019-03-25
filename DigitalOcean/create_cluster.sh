################################################################################
# Create a cluster                                                             #
# We will use the following defaults                                           #
# name "myCluster"                                                             #
# region "fra1"                                                                #
# size "s-1vcpu-2gb"                                                           #
# Usage:                                                                       #
# ./create_droplet.sh -n <name> -r <region> -s <size>  -t <token>              #
################################################################################


name="myCluster"
region="fra1"
size="s-1vcpu-2gb"
k8_version="1.13"

#
# Parse parameters
#
while getopts t:n:r:s:h option
do
  case "${option}"
    in
      n) name=${OPTARG};;
      r) region=${OPTARG};;
      s) size=${OPTARG};;
      h) echo "Usage: ./create_cluster.sh -n <name> -r <region> -s <size> -t <token>"; exit;;
      t) bearerToken=${OPTARG};;
  esac
done


echo "Creating cluster $name with node size $size in region $region"
echo "Using bearer token $bearerToken"


#
# Get the Kubernetes version matching 1.11
#
version=$(curl -X GET "https://api.digitalocean.com/v2/kubernetes/options"\
                      -H "Content-Type: application/json"\
                      -H "Authorization: Bearer $bearerToken" | jq -r ".options.versions[] | select(.kubernetes_version | contains(\"$k8_version\")).slug")
echo "Using version $version"


#
# Assemble node pool
#
nodePool="{\"size\":\"$size\",\"count\":"2", \"name\":\"default-pool\"}"
#
# and full request body
#
body="{\"name\":\"$name\", \"region\":\"$region\", \"version\":\"$version\",\"node_pools\": [ $nodePool ]}"
echo "Request body"
echo $body | jq '.'

#
# Post this
#
results=$(curl -X POST  "https://api.digitalocean.com/v2/kubernetes/clusters"\
                        -H "Content-Type: application/json"\
                        -H "Authorization: Bearer $bearerToken"\
                        -d "$body")
#
# Retrieve clusterId
#
clusterId=$(echo $results | jq -r '.kubernetes_cluster.id')
echo "Cluster $clusterId in creation"

#
# Get the status of the cluster and wait until it is active
#
echo "Waiting for completion of request"
status=X
while [ "$status" != "running" ];
do
sleep 15
status=$(curl -s -X GET "https://api.digitalocean.com/v2/kubernetes/clusters/$clusterId" \
	-H "Authorization: Bearer $bearerToken" \
	-H "Content-Type: application/json" \
        | jq -r '.kubernetes_cluster.status.state')
echo "Cluster is currently in status $status"
done


#
# Now download kubeconfig file and clean up cache
#
rm -rf ~/.kube/cache/
rm -rf ~/.kube/http-cache/
curl -s -X GET "https://api.digitalocean.com/v2/kubernetes/clusters/$clusterId/kubeconfig" \
               	-H "Authorization: Bearer $bearerToken" \
	        -H "Content-Type: application/json" > ~/.kube/config  
echo "Stored kubeconfig file at ~/.kube/config"


