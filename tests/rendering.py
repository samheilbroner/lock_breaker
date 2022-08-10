import os

from lock_breaker.rendering import image_from_text


def test_image_from_text():
    image_from_text('test_text\n'*50, 'images/test.png')
    assert os.path.exists('images/test.png')