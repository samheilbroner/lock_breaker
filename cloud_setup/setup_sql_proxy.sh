#!/bin/bash

# Check if Cloud SQL Proxy is present, if not, download
if [ ! -f "cloud_sql_proxy" ]; then
  echo "Cloud SQL Proxy is not found. Downloading now."
  wget https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.6.1/cloud-sql-proxy.darwin.amd64 -O cloud_sql_proxy
  chmod +x cloud_sql_proxy
else
  echo "Cloud SQL Proxy is already present."
fi

# Run Cloud SQL Proxy

echo "Starting Cloud SQL Proxy..."

kill "$(pgrep 'cloud_sql_proxy')"

# You must configure the ADC before launching the cloud sql proxy.
gcloud auth application-default login

#Launch the proxy.
./cloud_sql_proxy ${PROJECT_ID}:${REGION}:${INSTANCE_NAME} -p $PROXY_PORT &
