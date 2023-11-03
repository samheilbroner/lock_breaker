#!/bin/bash

# Check if SQL service is enabled, enable if not
SERVICE_ENABLED=$(gcloud services list --enabled --format="value(config.name)" | grep -w $SQL_SERVICE_NAME)
if [ -z "$SERVICE_ENABLED" ]; then
  echo "SQL service is not enabled. Enabling now."
  gcloud services enable $SQL_SERVICE_NAME
else
  echo "SQL service is already enabled."
fi

# List instances and check if the target instance exists
INSTANCE_EXIST=$(gcloud sql instances list --format="value(name)" | grep -w $INSTANCE_NAME)

# Check if the instance exists
if [ -z "$INSTANCE_EXIST" ]; then
  # Instance does not exist, create it
  echo "SQL instance '$INSTANCE_NAME' does not exist. Creating now."
  gcloud sql instances create $INSTANCE_NAME \
    --database-version=POSTGRES_13 \
    --tier=db-f1-micro \
    --region=$REGION
else
  # Instance exists
  echo "SQL instance '$INSTANCE_NAME' already exists. Doing nothing."
fi

# List databases and check if the target database exists
DATABASE_EXIST=$(gcloud sql databases list --instance=$INSTANCE_NAME --format="value(name)" | grep -w $DATABASE_NAME)

# Check if the database exists
if [ -z "$DATABASE_EXIST" ]; then
  # Database does not exist, create it
  echo "Database '$DATABASE_NAME' does not exist in instance '$INSTANCE_NAME'. Creating now."
  gcloud sql databases create $DATABASE_NAME --instance=$INSTANCE_NAME
else
  # Database exists
  echo "Database '$DATABASE_NAME' already exists in instance '$INSTANCE_NAME'. Doing nothing."
fi

echo 'Setting password for user postgres...'

# Set password for user postgres, get from gcloud secrets manager.
SQL_PASSWORD_VALUE="$(gcloud secrets versions access latest --secret=$PSQL_PASSWORD)"
export SQL_PASSWORD_VALUE
gcloud sql users set-password postgres --instance=$INSTANCE_NAME --password="$SQL_PASSWORD_VALUE"
