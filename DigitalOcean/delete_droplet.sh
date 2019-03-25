#############################################################
# Delete a droplet                                          #
#############################################################

#
# Parse parameters
#
while getopts d:t:h option
do
  case "${option}"
    in
      h) echo "Usage: ./delete_droplet.sh -d <droplet-id> -t <token>"; exit;;
      t) bearerToken=${OPTARG};;
      d) dropletId=${OPTARG};;
  esac
done

echo "Deleting droplet with ID $dropletId"
echo "Using bearer token $bearerToken"



#
# Delete droplet
#
curl -s -X DELETE "https://api.digitalocean.com/v2/droplets/$dropletId" \
	-H "Authorization: Bearer $bearerToken" \
	-H "Content-Type: application/json" 
echo "Done"


