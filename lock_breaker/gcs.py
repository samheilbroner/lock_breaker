import logging
import os
from abc import abstractmethod
from pathlib import Path
from sys import platform
from tempfile import mkdtemp, mktemp
from typing import ByteString, Union

import google.api_core.exceptions
from cryptography.fernet import Fernet
from google.cloud import storage

from lock_breaker import PASSWORD_PATH, GCS_BUCKET, TEXT_GENERATION_KEY_PATH, \
    IGLOO_API_KEY_PATH


def _make_local_tmp_path(bucket_name, gcs_path):
    path = Path(f'/tmp/{bucket_name}')
    file_path = path.joinpath(gcs_path)
    folder = file_path.parent
    if not os.path.exists(folder):
        folder.mkdir(parents=True)
    return file_path


def write_string_to_storage(
        string: Union[str, ByteString],
        gcs_path: str,
        bucket_name: str,
        type='wb'
):
    """Write a string to a specific gcs location.

    :param string: String to write.
    :param gcs_path: GCS path to write string to.
    :return: None
    """
    if platform == 'darwin':
        file_path = _make_local_tmp_path(bucket_name, gcs_path)
        with open(file_path, type) as f:
            f.write(string)
    else:
        bucket = storage.Client().get_bucket(bucket_name)
        blob = bucket.blob(gcs_path)

        blob.upload_from_string(string)


def read_string_from_storage(bucket_name: str, gcs_path: str,
                             type='rb') -> str:
    """Read string from a gcs path.

    :param gcs_path: gcs path of file where string is stored as .txt.
    :return: string stored at gcs path.
    """
    if platform == 'darwin':
        file_path = _make_local_tmp_path(bucket_name, gcs_path)
        with open(file_path, type) as f:
            answer = f.read()
    else:
        answer = _download_blob(bucket_name, gcs_path)
    return answer

class GCSManager:
    def __init__(self, bucket_name,
                 gcs_path,
                 type='b'):
        self.bucket_name = bucket_name
        self.gcs_path = gcs_path
        self.type=type

    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass

class GCSReader(GCSManager):

    def __init__(self, bucket_name, gcs_path, type='b'):
        super().__init__(bucket_name, gcs_path, type)
        self.type = 'r' + self.type

    def __call__(self):
        return read_string_from_storage(
            bucket_name=self.bucket_name,
            gcs_path=self.gcs_path,
            type=self.type
        )


class GCSWriter(GCSManager):
    def __init__(self, bucket_name, gcs_path, type='b'):
        super().__init__(bucket_name, gcs_path, type)
        self.type = 'w' + self.type

    def __call__(self, key: Union[ByteString, str]):
        """Write encryption key to project gcs bucket."""
        write_string_to_storage(
            key,
            gcs_path=self.gcs_path,
            bucket_name=self.bucket_name,
            type=self.type
        )


class KeyUpdater(GCSManager):

    def __init__(self, bucket_name, gcs_path, type='b'):
        super().__init__(bucket_name, gcs_path, type=type)
        self.writer = GCSWriter(
            bucket_name=bucket_name, gcs_path=gcs_path,
            type=self.type
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

    def _update_key(self):
        self.key_updater()
        answer = self.gcs_reader()
        return answer

    def __call__(self):
        try:
            answer = self.gcs_reader()
        except google.api_core.exceptions.NotFound:
            answer = self._update_key()
        except FileNotFoundError:
            answer = self._update_key()
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
igloo_api_key_reader = GCSReader(
    bucket_name=GCS_BUCKET,
    gcs_path=IGLOO_API_KEY_PATH,
    type=''
)
igloo_api_key_writer = GCSWriter(
    bucket_name=GCS_BUCKET,
    gcs_path=IGLOO_API_KEY_PATH,
    type=''
)


def _download_blob(bucket_name: str, blob_name: str) -> str:
    bucket = storage.Client().get_bucket(bucket_name)
    blob = bucket.blob(blob_name)

    return blob.download_as_string()

