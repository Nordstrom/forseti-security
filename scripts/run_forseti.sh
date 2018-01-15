#/bin/bash

echo "gsutil cp gs://$BUCKET_NAME/configs/forseti_conf.yaml /configs/forseti_conf.yaml"
echo "gsutil cp -r gs://$BUCKET_NAME/rules rules/"

echo "pwd"

sleep 30s;

gcloud auth activate-service-account "$ACCOUNT" --key-file /key/credentials.json --project "$PROJECT" -q

# Copy latest config and rules
gsutil cp gs://$BUCKET_NAME/configs/forseti_conf.yaml /configs/forseti_conf.yaml
gsutil cp -r gs://$BUCKET_NAME/rules rules/

echo "/usr/local/bin/forseti_inventory --forseti_config /configs/forseti_conf.yaml"

# Forseti Inventory
/usr/local/bin/forseti_inventory --forseti_config /configs/forseti_conf.yaml

echo "/usr/local/bin/forseti_scanner --forseti_config /configs/forseti_conf.yaml"

# Forseti Scanner
/usr/local/bin/forseti_scanner --forseti_config /configs/forseti_conf.yaml

echo "/usr/local/bin/forseti_notifier --forseti_config /configs/forseti_conf.yaml"

# Forseti Notifier
/usr/local/bin/forseti_notifier --forseti_config /configs/forseti_conf.yaml