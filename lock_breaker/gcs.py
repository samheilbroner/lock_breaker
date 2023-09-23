import os
from abc import abstractmethod, ABC
from pathlib import Path
from sys import platform
from typing import ByteString, Union

import google.api_core.exceptions
from cryptography.fernet import Fernet
from google.cloud import storage, secretmanager

from lock_breaker import ENCRYPTION_KEY_NAME, TEXT_GENERATION_KEY_NAME, \
    IGLOO_API_KEY, PROJECT_ID

class SecretManager(ABC):
    def __init__(self, project_id, secret_id):
        self.project_id = project_id
        self.secret_id = secret_id
        self.client = secretmanager.SecretManagerServiceClient()

    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass

class SecretReader(SecretManager):
    def __init__(self, project_id, secret_id):
        super().__init__(project_id, secret_id)

    def __call__(self):
        return self.read_secret()

    def read_secret(self):
        name = f"projects/{self.project_id}/secrets/{self.secret_id}/versions/latest"
        response = self.client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")

class SecretWriter(SecretManager):
    def __init__(self, project_id, secret_id):
        super().__init__(project_id, secret_id)

    def __call__(self, value):
        return self.write_secret(value)

    def write_secret(self, value):
        parent = f"projects/{self.project_id}"
        payload = value.encode("UTF-8")

        secret = self.client.create_secret(
            request={
                "parent": parent,
                "secret_id": self.secret_id,
                "secret": {
                    "replication": {
                        "automatic": {}
                    }
                }
            }
        )

        version = self.client.add_secret_version(
            request={
                "parent": secret.name,
                "payload": {"data": payload}
            }
        )

        return version.name


class SecretUpdater(SecretManager):
    def __init__(self, project_id, secret_id):
        super().__init__(project_id, secret_id)
        self.writer = SecretWriter(
            project_id=project_id, secret_id=secret_id
        )

    def __call__(self, *args, **kwargs):
        key = Fernet.generate_key()
        self.writer(key.decode('utf-8'))

class RobustSecretReader(SecretManager):
    def __init__(self, project_id, secret_id):
        super().__init__(project_id, secret_id)
        self.reader = SecretReader(
            project_id=project_id, secret_id=secret_id
        )
        self.secret_updater = SecretUpdater(
            project_id=project_id, secret_id=secret_id
        )

    def _update_secret(self):
        self.secret_updater()
        answer = self.reader()
        return answer

    def __call__(self):
        try:
            answer = self.reader()
        except google.api_core.exceptions.NotFound:
            answer = self._update_secret()
        return answer

update_encryption_key = SecretUpdater(
    PROJECT_ID, ENCRYPTION_KEY_NAME
)

read_encryption_key = RobustSecretReader(
    PROJECT_ID, ENCRYPTION_KEY_NAME
)

read_text_generation_key = RobustSecretReader(
    PROJECT_ID,
    TEXT_GENERATION_KEY_NAME
)

igloo_api_key_reader = SecretReader(
    project_id=PROJECT_ID,
    secret_id=IGLOO_API_KEY
)

igloo_api_key_writer = SecretWriter(
    project_id=PROJECT_ID,
    secret_id=IGLOO_API_KEY
)

def _download_blob(bucket_name: str, blob_name: str) -> str:
    bucket = storage.Client().get_bucket(bucket_name)
    blob = bucket.blob(blob_name)

    return blob.download_as_string()

