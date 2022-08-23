from lock_breaker import GCS_BUCKET
from lock_breaker.gcs import write_string_to_storage, read_string_from_storage


def test_write_string_to_gcs():
    TEST_STRING = b'test_string'
    TEST_PATH = 'test_data/test.txt'
    write_string_to_storage(TEST_STRING, TEST_PATH, GCS_BUCKET)
    assert read_string_from_storage(GCS_BUCKET, TEST_PATH) == TEST_STRING
