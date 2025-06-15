#!/bin/bash
kubectl delete secret ecr-creds --namespace dda
kubectl create secret docker-registry ecr-creds \
  --docker-server=977098986372.dkr.ecr.us-west-2.amazonaws.com \
  --docker-username=AWS \
  --docker-password=$(login-aws) \
  --docker-email=austingraham731@gmail.com \
  --namespace dda
