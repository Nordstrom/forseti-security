#/bin/bash

# Activate service account
echo "executing gcloud auth activate-service-account..."
gcloud auth activate-service-account "$ACCOUNT" --key-file /key/credentials.json --project "$PROJECT" -q

# Copy latest config and rules
echo "gsutil cp gs://$BUCKET_NAME/configs/forseti_conf.yaml /configs/forseti_conf.yaml"
gsutil cp gs://$BUCKET_NAME/configs/forseti_conf.yaml /configs/forseti_conf.yaml
echo "gsutil cp -r gs://$BUCKET_NAME/rules rules/"
gsutil cp -r gs://$BUCKET_NAME/rules rules/

# Forseti Inventory
echo "executing forseti_inventory..."
/usr/local/bin/forseti_inventory --forseti_config /configs/forseti_conf.yaml

# Forseti Scanner
echo "executing forseti_scanner..."
/usr/local/bin/forseti_scanner --forseti_config /configs/forseti_conf.yaml

# Forseti Notifier
echo "executing forseti_notifier..."
/usr/local/bin/forseti_notifier --forseti_config /configs/forseti_conf.yaml