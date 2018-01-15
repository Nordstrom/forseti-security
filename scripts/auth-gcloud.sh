#! /bin/bash
echo "GCLOUD_KEY > /tmp/gcs_key.json"
echo $GCLOUD_KEY > /tmp/gcs_key.json
echo "gcloud config set project nordforseti"
gcloud config set project nordforseti
echo "gcloud auth activate-service-account --key-file /tmp/gcs_key.json"
gcloud auth activate-service-account --key-file /tmp/gcs_key.json
# echo "ssh-keygen -f ~/.ssh/google_compute_engine -N "
# ssh-keygen -f ~/.ssh/google_compute_engine -N ""