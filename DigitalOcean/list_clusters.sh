#############################################################
# List all clusters                                         #
# Add -l to get full JSON output                            #
#############################################################


#
# Parse parameters
#
longOutput=0
while getopts t:hl option
do
  case "${option}"
    in
      h) echo "Usage: ./list_clusters.sh -t <token> , use -l to toggle full JSON output"; exit;;
      t) bearerToken=${OPTARG};;
      l) longOutput=1
  esac
done

echo "Using bearer token $bearerToken"



#
# Get all clusters
#
all=$(curl -s -X GET "https://api.digitalocean.com/v2/kubernetes/clusters" \
	-H "Authorization: Bearer $bearerToken" \
	-H "Content-Type: application/json")
count=$(echo $all | jq '.meta.total') 
echo "Found $count clusters in total"
clusters=$(echo $all | jq '.kubernetes_clusters')


if [ $longOutput -eq 1 ]; 
then
  echo $all | jq '.'
fi

i=0
while [  $i -lt $count ]; do
   cluster=$(echo $clusters | jq ".[$i]")
   id=$(echo $cluster | jq -r '.id')
   name=$(echo $cluster | jq -r '.name')
   status=$(echo $cluster | jq -r '.status.state')
   let i=i+1 
   echo "Cluster $i[$status]: ID = $id , name = $name " 

done

