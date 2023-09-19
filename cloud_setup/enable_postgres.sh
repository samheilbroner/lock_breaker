#!/bin/bash

INSTANCE_NAME="lockbreaker"
REGION="us-west1"

# List instances and check if the target instance exists
INSTANCE_EXIST=$(gcloud sql instances list --format="value(name)" | grep -w $INSTANCE_NAME)

# Check if the instance exists
if [ -z "$INSTANCE_EXIST" ]; then
  # Instance does not exist, create it
  echo "SQL instance '$INSTANCE_NAME' does not exist. Creating now."
  gcloud sql instances create $INSTANCE_NAME \
    --database-version=POSTGRES_13 \
    --cpu=1 \
    --memory=4GiB \
    --region=$REGION
else
  # Instance exists
  echo "SQL instance '$INSTANCE_NAME' already exists. Doing nothing."
fi
