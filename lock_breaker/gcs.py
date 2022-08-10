import logging
from abc import abstractmethod
from sys import platform
from tempfile import mkdtemp, mktemp
from typing import ByteString, Union

import google.api_core.exceptions
from cryptography.fernet import Fernet
from google.cloud import storage

from lock_breaker import PASSWORD_PATH, GCS_BUCKET, TEXT_GENERATION_KEY_PATH


def make_client():
    if platform == 'darwin':
        return storage.Client.from_service_account_json(
            '/Users/samuel.heilbroner/credentials/service_account_credentials.json'
        )
    else:
        return storage.Client()


storage_client = make_client()


def write_string_to_gcs(
        string: Union[str, ByteString],
        gcs_path: str,
        bucket_name: str
):
    """Write a string to a specific gcs location.

    :param string: String to write.
    :param gcs_path: GCS path to write string to.
    :return: None
    """
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(gcs_path)

    blob.upload_from_string(string)


def read_string_from_gcs(bucket_name: str, gcs_path: str) -> str:
    """Read string from a gcs path.

    :param gcs_path: gcs path of file where string is stored as .txt.
    :return: string stored at gcs path.
    """
    answer = _download_blob(bucket_name, gcs_path)
    return answer

class GCSManager:
    def __init__(self, bucket_name,
                 gcs_path):
        self.bucket_name = bucket_name
        self.gcs_path = gcs_path

    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass

class GCSReader(GCSManager):
    def __call__(self):
        return read_string_from_gcs(
            bucket_name=self.bucket_name,
            gcs_path=self.gcs_path
        )


class GCSWriter(GCSManager):
    def __call__(self, key: Union[ByteString, str]):
        """Write encryption key to project gcs bucket."""
        write_string_to_gcs(
            key,
            gcs_path=self.gcs_path,
            bucket_name=self.bucket_name
        )


class KeyUpdater(GCSManager):

    def __init__(self, bucket_name, gcs_path):
        super().__init__(bucket_name, gcs_path)
        self.writer = GCSWriter(
            bucket_name=bucket_name, gcs_path=gcs_path
        )

    def __call__(self, *args, **kwargs):
        key = Fernet.generate_key()
        self.writer(key)


class RobustGCSReader(GCSManager):
    def __init__(self, bucket_name,
                 gcs_path):
        super().__init__(bucket_name, gcs_path)
        self.gcs_reader = GCSReader(
            self.bucket_name,
            self.gcs_path
        )
        self.key_updater = KeyUpdater(
            self.bucket_name,
            self.gcs_path
        )

    def __call__(self):
        try:
            answer = self.gcs_reader()
        except google.api_core.exceptions.NotFound:
            self.key_updater()
            answer = self.gcs_reader()
        return answer


update_encryption_key = KeyUpdater(
    GCS_BUCKET, PASSWORD_PATH
)
read_encryption_key = RobustGCSReader(
    bucket_name=GCS_BUCKET,
    gcs_path=PASSWORD_PATH
)

read_text_generation_key = RobustGCSReader(
    bucket_name=GCS_BUCKET,
    gcs_path=TEXT_GENERATION_KEY_PATH
)


def _download_blob(bucket_name: str, blob_name: str) -> str:
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)

    return blob.download_as_string()

