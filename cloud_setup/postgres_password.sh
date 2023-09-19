#!/bin/bash

# Enable Google Secret Manager API if not already enabled
api_status=$(gcloud services list --enabled --filter="config.name:secretmanager.googleapis.com" --format="value(config.name)")
if [ -z "$api_status" ]; then
  echo "Enabling Google Secret Manager API..."
  gcloud services enable secretmanager.googleapis.com
else
  echo "Google Secret Manager API is already enabled."
fi

# Check if the secret called 'psql_password' already exists
secret_exist=$(gcloud secrets list --filter="name:$PSQL_PASSWORD" --format="value(name)")
if [ -z "$secret_exist" ]; then
  echo "Creating secret $PSQL_PASSWORD..."

  # Generate a random password
  random_password=$(openssl rand -base64 32)

  # Create a new secret called 'psql_password'
  gcloud secrets create "$PSQL_PASSWORD" --replication-policy="automatic"

  # Add the random password as a version of the secret
  echo -n "$random_password" | gcloud secrets versions add "$PSQL_PASSWORD" --data-file=-

  echo "psql_password has been created and stored in Secret Manager."
else
  echo "psql_password already exists in Secret Manager."
fi
