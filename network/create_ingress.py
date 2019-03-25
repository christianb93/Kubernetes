###########################################################################################
# This script will create an ingress rule                                                 #
# It assumes that you have a service tomcat-service and a service httpd-service, both     #
# listening on port 8080                                                                  #
#                                                                                         #
###########################################################################################


k8Version="1.11"

from kubernetes import client, config

config.load_kube_config()


#
# First we create an ingress object and populate its metadata
# see https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1beta1Ingress.md
# 
ingress=client.V1beta1Ingress()
ingress.api_version="extensions/v1beta1"
ingress.kind="Ingress"
metadata=client.V1ObjectMeta()
metadata.name="test-ingress"
metadata.annotations={"nginx.ingress.kubernetes.io/rewrite-target" : "/"}
ingress.metadata=metadata

#
# Now assemble the actual ingress specification. We start with the two backends
#
tomcat_backend=client.V1beta1IngressBackend(service_name="tomcat-service", service_port=8080)
httpd_backend=client.V1beta1IngressBackend(service_name="httpd-service", service_port=8080)
#
# and the corresponding paths
#
tomcat_path=client.V1beta1HTTPIngressPath(backend=tomcat_backend, path="/tomcat")
httpd_path=client.V1beta1HTTPIngressPath(backend=httpd_backend, path="/httpd")
#
# Now we can set up our rule
# 
rule=client.V1beta1IngressRule(http=client.V1beta1HTTPIngressRuleValue(paths=[tomcat_path, httpd_path]))

#
# We now assemble everything into the specification
#
spec=client.V1beta1IngressSpec()
spec.rules=[rule]
ingress.spec=spec

#
# and submit
#
apiv1beta1=client.ExtensionsV1beta1Api()
apiv1beta1.create_namespaced_ingress(namespace="default",body=ingress)






