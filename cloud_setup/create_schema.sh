PROJECT_ID=$(gcloud config get-value project)

# Check if the 'lock_breaker' dataset exists
bq ls --project_id="$PROJECT_ID" | grep 'lock_breaker' &> /dev/null

# Create the 'lock_breaker' dataset if it doesn't exist
if [ $? -ne 0 ]; then
    bq mk --dataset "$PROJECT_ID":lock_breaker
    echo "Dataset 'lock_breaker' created."
else
    echo "Dataset 'lock_breaker' already exists."
fi

# Connect to the database and create a schema if it doesn't exist
gcloud sql connect $INSTANCE_NAME --user=postgres <<EOF
  SELECT 'CREATE SCHEMA IF NOT EXISTS $SCHEMA_NAME;' WHERE NOT EXISTS (SELECT schema_name FROM information_schema.schemata WHERE schema_name = '$SCHEMA_NAME') \gexec
EOF

echo "If the schema did not exist, it has been created as '$SCHEMA_NAME'. Otherwise, no action was taken."