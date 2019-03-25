#############################################################
# Delete a droplet                                          #
#############################################################


dropletId=$1
echo "Deleting droplet with ID $dropletId"
echo "Using bearer token $bearerToken"



#
# Delete droplet
#
curl -s -X DELETE "https://api.digitalocean.com/v2/droplets/$dropletId" \
	-H "Authorization: Bearer $bearerToken" \
	-H "Content-Type: application/json" 
echo "Done"


