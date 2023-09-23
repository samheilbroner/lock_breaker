from google.cloud import storage

TEMP = '/tmp'
IMAGE_FILE_NAME = 'text.png'
IMAGE_PATH = f'{TEMP}/{IMAGE_FILE_NAME}'
TEXT_LENGTH = 10 # 2500
PUZZLE_URL = 'puzzle'
PUZZLE_START_TIME = 'PUZZLE_START_TIME'
PUZZLE_TEXT = 'PUZZLE_TEXT'
MAX_MINUTES_TO_COMPLETE = 25

ENCRYPTION_KEY_NAME = 'encryption_key'
TEXT_GENERATION_KEY_NAME = 'text_generation_key'
IGLOO_API_KEY = 'igloo_api_key'
DEFAULT_PASSWORD_LENGTH = 8

POSTGRES_PASSWORD_LABEL = 'psql_password'
REGION = 'us-west1'
APP_SECRET_KEY_NAME = 'app_secret_key'


def get_current_project_id():
    # Initialize the Google Cloud Storage client
    storage_client = storage.Client()

    # Your default bucket is often in the format <project_id>.appspot.com
    project_id = storage_client.project
    return project_id


PROJECT_ID = get_current_project_id()
def get_default_bucket_name():

    # Your default bucket is often in the format <project_id>.appspot.com
    default_bucket_name = f"{PROJECT_ID}.appspot.com"
    return default_bucket_name

GCS_BUCKET = get_default_bucket_name()

IGLOO_API_URL = 'https://api.igloodeveloper.co/v2'
PST = 'PST8PDT'
PIN = 'pin'
DOOR_LOCK_ID = 'IGK308b7207d'
PADLOCK_ID = 'IGP113808443'
TAOS_ID = 'IGK316f121ef'
IGLOO_LOCK_IDS = [DOOR_LOCK_ID,
                  PADLOCK_ID,
                  TAOS_ID]
