from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from lock_breaker import TEMP
from lock_breaker.string import add_returns_to_text

import os


def get_size(txt, font):
    testImg = Image.new('RGB', (1, 1))
    testDraw = ImageDraw.Draw(testImg)
    return testDraw.textsize(txt, font)


def get_image_size(text, font):
    d = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    return d.textsize(text, font)


def image_from_text(text: str, image_destination: str):
    fontname = "arial.ttf"  # Make sure this font is available on your system
    fontsize = 20

    colorText = "black"
    colorOutline = "black"
    colorBackground = "white"

    font = ImageFont.truetype(font=fontname, size=fontsize)
    width, height = get_image_size(text, font)

    # Adding padding
    padding = 10
    frame_width, frame_height = width + 2 * padding, height + 2 * padding

    img = Image.new('RGB', (frame_width, frame_height), colorBackground)
    d = ImageDraw.Draw(img)

    # Draw text at padded position
    d.text((padding, padding), text, fill=colorText, font=font)

    # Draw rectangle around the border
    d.rectangle((0, 0, frame_width - 1, frame_height - 1), outline=colorOutline)

    img.save(image_destination)

def clear_files(path):
    # Clear all the images in the given directory
    for file in os.listdir(path):
        os.remove(os.path.join(path, file))

def create_image_input_pairs(text):
    # Create temp directory if it doesn't exist
    if not os.path.exists(TEMP):
        os.makedirs(TEMP)
    clear_files(TEMP)
    text_to_render = add_returns_to_text(text)
    texts = text_to_render.split('\n')
    # get rid of empty strings
    texts = [text for text in texts if text]
    input_names = [f'input{i}' for i in range(len(texts))]
    image_file_names = [f'{name}.png' for name in input_names]
    image_paths = [os.path.join(TEMP, name) for name in image_file_names]
    for text, path in zip(texts, image_paths):
        image_from_text(text, path)
    return list(zip(image_file_names, input_names))
