#!/bin/bash

# Check if the secret called 'psql_password' already exists
secret_exist=$(gcloud secrets list --filter="name:$APP_SECRET_KEY" --format="value(name)")
if [ -z "$secret_exist" ]; then
  echo "Creating secret $APP_SECRET_KEY..."

  # Generate a random password
  random_password=$(openssl rand -base64 24 | tr -d '/+' | cut -c -32)

  # Create a new secret
  gcloud secrets create "$APP_SECRET_KEY" --replication-policy="automatic"

  # Add the random password as a version of the secret
  echo -n "$random_password" | gcloud secrets versions add "$APP_SECRET_KEY" --data-file=-

  echo "psql_password has been created and stored in Secret Manager."
else
  echo "psql_password already exists in Secret Manager."
fi