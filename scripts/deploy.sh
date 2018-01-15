#! /bin/bash
#if [ "$TRAVIS_BRANCH" = "master" ] && [ "$TRAVIS_PULL_REQUEST" = "false" ]; then
  gcloud --quiet components update kubectl
  # Push to Google container registry
  gcloud docker -- push gcr.io/nordforseti/forseti > /dev/null
  # Deploy to the cluster
  gcloud container clusters get-credentials nordforseti
  kubectl apply -f scripts/k8s/forseti.yml
#fi