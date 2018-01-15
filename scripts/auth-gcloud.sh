#! /bin/bash
echo $GCLOUD_KEY > /tmp/gcloud_key.json
gcloud config set project nordforseti
gcloud auth activate-service-account --key-file /tmp/gcloud_key.json
ssh-keygen -f ~/.ssh/google_compute_engine -N ""