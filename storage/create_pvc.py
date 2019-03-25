###########################################################################################
# This script will create a persistent volume claim using a default storage class and     #
# bring up a Pod using it                                                                 #
###########################################################################################


k8Version="1.11"

from kubernetes import client, config

#
# Load config as usual
#
config.load_kube_config()


#
# Create a PVC object and populate standard fields
#
pvc=client.V1PersistentVolumeClaim()
pvc.api_version="v1"
pvc.metadata=client.V1ObjectMeta(name="my-pvc")

#
# Create volume claim specification. We leave the storage class
# name as None to make sure that we pick up the default storage
# class
#
spec=client.V1PersistentVolumeClaimSpec()
spec.access_modes=["ReadWriteOnce"]
spec.resources=client.V1ResourceRequirements(requests={"storage" : "32Gi"})
pvc.spec=spec

#
# Submit creation request
#
api=client.CoreV1Api()
api.create_namespaced_persistent_volume_claim(namespace="default", body=pvc)


#
# Now create a deployment for a Pod using this as persistent volume. We start with the container
# Here we need a section 
#
container = client.V1Container(
              name="alpine-ctr",
              image="httpd:alpine",
              volume_mounts=[client.V1VolumeMount(mount_path="/test",name="my-volume")])

#
# Now we need to create the Pod specification, making sure that
# we include the volumes that we refer to in the container definition
#
pvcSource=client.V1PersistentVolumeClaimVolumeSource(claim_name="my-pvc")
podVolume=client.V1Volume(name="my-volume",persistent_volume_claim=pvcSource)
podSpec=client.V1PodSpec(containers=[container], 
                         volumes=[podVolume])

#
# Now finalize deployment with this data
#
template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(
                   labels={"app": "alpine"}),
        spec=podSpec)

selector = client.V1LabelSelector(match_labels={"app" : "alpine"})
spec = client.V1DeploymentSpec(
        replicas=1,
        template=template, 
        selector=selector)

deployment = client.V1Deployment(
       api_version="apps/v1",
       kind="Deployment",
       metadata=client.V1ObjectMeta(name="pvc-test"),
       spec=spec)

apps = client.AppsV1Api() 
apps.create_namespaced_deployment(namespace="default", body=deployment)



