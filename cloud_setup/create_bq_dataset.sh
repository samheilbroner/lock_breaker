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
