###########################################################################################
# This script will create a deployment of two httpd daemons                               #
# It assumes that you have a working kubectl configuration                                #
# At this point, we use Kubernetes version 1.11                                           #
# Most of this is taken from                                                              # 
# https://github.com/kubernetes-client/python/blob/master/examples/deployment_examples.py #
#                                                                                         #
# However, this seems to be slightly outdated, and I have adapted based on the output     #
# of dir(client)                                                                          #
###########################################################################################


k8Version="1.11"

from kubernetes import client, config

config.load_kube_config()
apps = client.AppsV1Api() 

#
# Create container specification
#
container = client.V1Container(
              name="alpine-ctr",
              image="httpd:alpine")

#
# Now we fill the spec section
#
template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(
                   labels={"app": "alpine"}),
        spec=client.V1PodSpec(containers=[container]))

selector = client.V1LabelSelector(match_labels={"app" : "alpine"})
spec = client.V1DeploymentSpec(
        replicas=2,
        template=template, 
        selector=selector)

#
# Create the actual deployment object
#
deployment = client.V1Deployment(
       api_version="apps/v1",
       kind="Deployment",
       metadata=client.V1ObjectMeta(name="alpine"),
       spec=spec)

apps.create_namespaced_deployment(namespace="default", body=deployment)
