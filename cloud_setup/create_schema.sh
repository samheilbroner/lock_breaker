#!/bin/bash

# Connect to the PostgreSQL instance and create the schema if it doesn't exist
echo "Connecting to PostgreSQL database..."
password="$(gcloud secrets versions access latest --secret=$PSQL_PASSWORD)"
psql "host=localhost port=${PROXY_PORT} dbname=${DATABASE_NAME} user=postgres password=$password sslmode=disable" <<EOF
  CREATE SCHEMA IF NOT EXISTS ${SCHEMA_NAME};
EOF

echo "If the schema did not exist, it has been created as '${SCHEMA_NAME}'. Otherwise, no action was taken."