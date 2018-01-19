#! /bin/bash
#if [ "$TRAVIS_BRANCH" = "master" ] && [ "$TRAVIS_PULL_REQUEST" = "false" ]; then
  echo "gcloud --quiet components update kubectl"
  gcloud --quiet components update kubectl
  # Push to Google container registry
  echo "gcloud docker -- push gcr.io/nordforseti/forseti > /dev/null"
  gcloud docker -- push gcr.io/nordforseti/forseti
  # Deploy to the cluster
  echo "gcloud container clusters get-credentials nordforseti"
  gcloud container clusters get-credentials $CLUSTER --zone $CLUSTER_ZONE
  echo "kubectl apply -f scripts/k8s/forseti.yml"
  kubectl apply -f scripts/k8s/forseti.yml
#fi