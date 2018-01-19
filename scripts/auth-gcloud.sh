#! /bin/bash
openssl aes-256-cbc -K $encrypted_cae2a5d5fb7d_key -iv $encrypted_cae2a5d5fb7d_iv -in gcloud-service-key.json.enc -out gcloud-service-key.json -d
echo "gcloud config set project nordforseti"
gcloud config set project nordforseti
echo "gcloud auth activate-service-account --key-file gcloud-service-key.json"
gcloud auth activate-service-account --key-file gcloud-service-key.json