from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from lock_breaker import IMAGE_PATH
from lock_breaker.string import add_returns_to_text


def get_size(txt, font):
    testImg = Image.new('RGB', (1, 1))
    testDraw = ImageDraw.Draw(testImg)
    return testDraw.textsize(txt, font)


def get_size(text, font):
    d = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    return d.textsize(text, font)


def image_from_text(text: str, image_destination: str):
    fontname = "arial.ttf"  # Make sure this font is available on your system
    fontsize = 15

    colorText = "black"
    colorOutline = "black"
    colorBackground = "white"

    font = ImageFont.truetype(font=fontname, size=fontsize)
    width, height = get_size(text, font)

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


def render_text(text):
    text_to_render = add_returns_to_text(text)
    image_from_text(text_to_render, IMAGE_PATH)
