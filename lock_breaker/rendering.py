import os

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from lock_breaker import IMAGE_PATH
from lock_breaker.string import add_returns_to_text


def get_size(txt, font):
    testImg = Image.new('RGB', (1, 1))
    testDraw = ImageDraw.Draw(testImg)
    return testDraw.textsize(txt, font)

def image_from_text(text:str, image_destination: str):
    fontname = "arial.ttf"
    fontsize = 15

    colorText = "black"
    colorOutline = "black"
    colorBackground = "white"

    font = ImageFont.truetype(font=fontname, size=fontsize)
    width, height = get_size(text, font)
    frame_width, frame_height = int(1.1*width), int(1*height)
    img = Image.new('RGB', (frame_width, frame_height), colorBackground)
    d = ImageDraw.Draw(img)
    d.text((2, 2), text, fill=colorText, font=font)
    d.rectangle((0, 0, frame_width - 2, frame_height - 2), outline=colorOutline)

    img.save(image_destination)


def render_text(text):
    text_to_render = add_returns_to_text(text)
    image_from_text(text_to_render, IMAGE_PATH)
