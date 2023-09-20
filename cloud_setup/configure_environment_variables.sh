export DATABASE_NAME="user_info"
export INSTANCE_NAME="lockbreaker"
PROJECT_ID=$(gcloud config get-value project)
export PROJECT_ID
export REGION="us-west1"
export SCHEMA_NAME="user_info"
ACCESS_TOKEN="$(gcloud auth print-access-token)"
export ACCESS_TOKEN
export SQL_SERVICE_NAME="sql-component.googleapis.com"
export PROXY_PORT="5432"
export SQL_CREDENTIALS_FILE="./secrets/sql-editor-sa-key.json"
export PSQL_PASSWORD="psql_password"
export APP_SECRET_KEY="app_secret_key"