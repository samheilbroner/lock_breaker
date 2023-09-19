import os

from google.cloud import storage, client

TEMP = '/tmp'
IMAGE_FILE_NAME = 'text.png'
IMAGE_PATH = f'{TEMP}/{IMAGE_FILE_NAME}'
TEXT_LENGTH = 10 # 2500
PUZZLE_URL = 'puzzle'
PUZZLE_START_TIME = 'PUZZLE_START_TIME'
PUZZLE_TEXT = 'PUZZLE_TEXT'
MAX_MINUTES_TO_COMPLETE = 25

PASSWORD_PATH = 'key.txt'
TEXT_GENERATION_KEY_PATH = 'text_generation_key.txt'
IGLOO_API_KEY_PATH = 'igloo_api_key.txt'
DEFAULT_PASSWORD_LENGTH = 8

LOCAL_CREDENTIALS_PATH = 'local-access.json'


def get_default_bucket_name():
    # Initialize the Google Cloud Storage client
    storage_client = storage.Client()

    # Your default bucket is often in the format <project_id>.appspot.com
    project_id = storage_client.project
    default_bucket_name = f"{project_id}.appspot.com"
    return default_bucket_name


def get_current_project_id():
    # Initialize the Google Cloud Storage client
    storage_client = storage.Client()

    # Your default bucket is often in the format <project_id>.appspot.com
    project_id = storage_client.project
    return project_id


def get_bq_uri():
    if os.environ.get('GAE_APPLICATION'):
        # App is running on Google Cloud, credentials are automatically available
        return f"bigquery://{PROJECT_ID}"
    else:
        # Load the service account info and set the credentials
        return f"bigquery://{PROJECT_ID}?credentials_path={LOCAL_CREDENTIALS_PATH}"


PROJECT_ID = get_current_project_id()
GCS_BUCKET = get_default_bucket_name()
BQ_URI = get_bq_uri()

IGLOO_API_URL = 'https://api.igloodeveloper.co/v2'
PST = 'PST8PDT'
PIN = 'pin'
DOOR_LOCK_ID = 'IGK308b7207d'
PADLOCK_ID = 'IGP113808443'
TAOS_ID = 'IGK316f121ef'
IGLOO_LOCK_IDS = [DOOR_LOCK_ID,
                  PADLOCK_ID,
                  TAOS_ID]
