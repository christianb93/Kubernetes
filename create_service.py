###########################################################################################
# This script will create a service for our httpd daemons                                 #
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


#
# First we create a service object and populate its metadata
# see https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1Service.md
# 
service = client.V1Service()
service.api_version = "v1"
service.kind = "Service"
metadata = client.V1ObjectMeta(name="alpine-service")
service.metadata = metadata
service.type="LoadBalancer"


#
# Now assemble the service specification
# see https://github.com/kubernetes-client/python/blob/master/examples/notebooks/create_service.ipynb
#
spec = client.V1ServiceSpec()
selector = {"app": "alpine"}
spec.selector = selector
spec.type="LoadBalancer"
port = client.V1ServicePort(
              port = 8080, 
              protocol = "TCP", 
              target_port = 80 )
spec.ports = [port]
service.spec = spec

#
# and submit
#
api = client.CoreV1Api()
api.create_namespaced_service(namespace="default", body=service)






