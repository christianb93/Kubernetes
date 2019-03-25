#############################################################
# Delete a cluster                                          #
#############################################################

#
# Parse parameters
#
while getopts c:t:h option
do
  case "${option}"
    in
      h) echo "Usage: ./delete_cluster.sh -c <cluster-id> -t <token>"; exit;;
      t) bearerToken=${OPTARG};;
      c) clusterId=${OPTARG};;
  esac
done

echo "Deleting cluster with ID $clusterId"
echo "Using bearer token $bearerToken"



#
# Delete cluster
#
curl -s -X DELETE "https://api.digitalocean.com/v2/kubernetes/clusters/$clusterId" \
	-H "Authorization: Bearer $bearerToken" \
	-H "Content-Type: application/json" 
echo "Done"


