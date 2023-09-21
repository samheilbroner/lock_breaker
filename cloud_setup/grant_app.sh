#!/bin/bash

# Check if App Engine is already enabled and an app exists
app_exist=$(gcloud app describe --format="get(id)" 2>/dev/null)

# Get the current user's email
CURRENT_USER_EMAIL=$(gcloud config get-value account)

# Check if the email was fetched successfully
if [ -z "$CURRENT_USER_EMAIL" ]; then
  echo "Failed to get the current user's email. Make sure you are authenticated with gcloud."
  exit 1
fi

# Grant roles/cloudsql.instanceUser role to the current user
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="user:$CURRENT_USER_EMAIL" \
  --role="roles/cloudsql.instanceUser"

# Grant roles/cloudsql.client role to the current user
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="user:$CURRENT_USER_EMAIL" \
  --role="roles/cloudsql.client"

echo "IAM roles granted successfully to $CURRENT_USER_EMAIL."

# Check for errors and existence of App Engine app
if [ $? -eq 0 ] && [ ! -z "$app_exist" ]; then
    echo "App Engine already exists for project $PROJECT_ID."
else
    echo "App Engine does not exist for project $PROJECT_ID. Creating..."
    gcloud app create --region=$REGION
    if [ $? -eq 0 ]; then
        echo "Successfully created App Engine application."
    else
        echo "Failed to create App Engine application. Exiting."
        exit 1
    fi
fi

SERVICE_ACCOUNT_EMAIL=$(gcloud iam service-accounts list \
    --filter="email~^$PROJECT_ID@appspot.gserviceaccount.com$" \
    --format="get(email)")

# Check if the service account exists
if [ -z "$SERVICE_ACCOUNT_EMAIL" ]; then
    echo "App Engine default service account not found. Exiting."
    exit 1
else
    echo "Found App Engine default service account: $SERVICE_ACCOUNT_EMAIL."
fi

# Grant the "Secret Manager Secret Accessor" role to the service account
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/secretmanager.secretAccessor"

# Check if the command was successful
if [ $? -eq 0 ]; then
    echo "Successfully granted access to Secrets Manager for $SERVICE_ACCOUNT_EMAIL."
else
    echo "Failed to grant access to Secrets Manager. Exiting."
    exit 1
fi

# Add the 'Cloud SQL Client' role to the App Engine default service account
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/cloudsql.client"

# Check if the command was successful
if [ $? -eq 0 ]; then
    echo "Successfully added the 'Cloud SQL Client' role to $SERVICE_ACCOUNT_EMAIL."
else
    echo "Failed to add the 'Cloud SQL Client' role. Exiting."
    exit 1
fi