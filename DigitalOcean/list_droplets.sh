#############################################################
# List all droplets                                         #
#############################################################


echo "Using bearer token $bearerToken"



#
# Get all droplets
#
all=$(curl -s -X GET "https://api.digitalocean.com/v2/droplets/" \
	-H "Authorization: Bearer $bearerToken" \
	-H "Content-Type: application/json")
count=$(echo $all | jq '.meta.total') 
echo "Found $count droplets in total"

i=0
while [  $i -lt $count ]; do
   droplet=$(echo $all | jq ".droplets[$i]")
   id=$(echo $droplet | jq  -r '.id')
   name=$(echo $droplet | jq -r '.name')
   status=$(echo $droplet | jq -r '.status')
   publicIp=$(echo $droplet | jq -r '.networks[] | select(.[].type="public")[0].ip_address' )
   publicIp=$(echo $publicIp | awk '{print $1}')
   let i=i+1 
   echo "Droplet $i[$status]: ID = $id , IP = $publicIp , name = $name " 
done

