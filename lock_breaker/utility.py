from flask import request, redirect, url_for
from google.cloud import secretmanager

from lock_breaker.gcs import read_encryption_key
from lock_breaker.password import encrypt
from lock_breaker.validation import input_is_valid


def _impute_empty_string(string: str) -> str:
    if len(string) == 0:
        return '_'
    else:
        return string


def handle_encryption_request(text, current_time, copied_text):
    to_decrypt = _impute_empty_string(request.form['decrypt'])
    to_encrypt = _impute_empty_string(request.form['encrypt'])
    key = read_encryption_key()
    code = encrypt(current_time, key)
    if input_is_valid(copied_text, text, current_time):
        return redirect(url_for('password',
                                code=code,
                                to_encrypt=to_encrypt,
                                to_decrypt=to_decrypt))
    else:
        return redirect(url_for('index'))


def get_gcp_secret(project_id, secret_name, version="latest"):
    """
    Retrieve a secret value from Google Cloud Secret Manager.

    Parameters:
    - project_id (str): Google Cloud Project ID where the Secret Manager is located.
    - secret_name (str): Name of the secret to retrieve.
    - version (str): Version of the secret (default is "latest").

    Returns:
    - str: The secret value as a string.
    """
    # Initialize the Secret Manager client
    client = secretmanager.SecretManagerServiceClient()

    # Create the resource name of the secret
    name = f"projects/{project_id}/secrets/{secret_name}/versions/{version}"

    # Retrieve the secret
    response = client.access_secret_version(request={"name": name})
    secret_data = response.payload.data.decode("UTF-8")

    return secret_data
