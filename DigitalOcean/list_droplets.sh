#############################################################
# List all droplets                                         #
# Add -l to get full JSON output                            ä
#############################################################


#
# Parse parameters
#
longOutput=0
while getopts t:hl option
do
  case "${option}"
    in
      h) echo "Usage: ./list_droplets.sh -t <token> , use -l to toggle full JSON output"; exit;;
      t) bearerToken=${OPTARG};;
      l) longOutput=1
  esac
done

echo "Using bearer token $bearerToken"



#
# Get all droplets
#
all=$(curl -s -X GET "https://api.digitalocean.com/v2/droplets/" \
	-H "Authorization: Bearer $bearerToken" \
	-H "Content-Type: application/json")
count=$(echo $all | jq '.meta.total') 
echo "Found $count droplets in total"
if [ $longOutput -eq 1 ]; 
then
  echo $all | jq '.'
fi

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

