#!/bin/bash

# Initialize variables
ROLE_ID="custom.sqlEditor"
ROLE_TITLE="Custom SQL Editor"
SERVICE_ACCOUNT_NAME="sql-editor-sa"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
SECRET_FOLDER="./secrets"

# Create custom IAM role with SQL editor permissions
gcloud iam roles create $ROLE_ID \
  --project $PROJECT_ID \
  --title "$ROLE_TITLE" \
  --permissions cloudsql.instances.update,cloudsql.instances.get,cloudsql.instances.list,cloudsql.databases.update,cloudsql.databases.get,cloudsql.databases.list \
  --description "Custom role with permissions to edit SQL databases."

# Create a service account
gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
  --description "Service Account to edit SQL databases" \
  --display-name "SQL Editor Service Account"

# Bind the custom role to the service account
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member "serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role "projects/${PROJECT_ID}/roles/${ROLE_ID}"

# Create secrets folder if it doesn't exist
mkdir -p $SECRET_FOLDER

# Generate and download the service account key, save it in the secrets folder
gcloud iam service-accounts keys create "${SECRET_FOLDER}/sql-editor-sa-key.json" \
  --iam-account $SERVICE_ACCOUNT_EMAIL

echo "Service account key has been saved in the ${SECRET_FOLDER} directory."
