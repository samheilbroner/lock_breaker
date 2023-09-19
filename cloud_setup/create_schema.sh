#!/bin/bash

# Run Cloud SQL Proxy
echo "Starting Cloud SQL Proxy..."
./cloud_sql_proxy ${PROJECT_ID}:${REGION}:${INSTANCE_NAME} -p $PROXY_PORT &


# Allow some time for the proxy to start
sleep 5
echo "Cloud SQL Proxy started."

# Connect to the PostgreSQL instance and create the schema if it doesn't exist
echo "Connecting to PostgreSQL database..."
password=$(gcloud secrets versions access latest --secret=$PSQL_PASSWORD)
psql "host=localhost port=${PROXY_PORT} dbname=${DATABASE_NAME} user=postgres password=$password" <<EOF
  CREATE SCHEMA IF NOT EXISTS ${SCHEMA_NAME};
EOF

echo "If the schema did not exist, it has been created as '${SCHEMA_NAME}'. Otherwise, no action was taken."

kill $(pgrep -f 'cloud_sql_proxy')