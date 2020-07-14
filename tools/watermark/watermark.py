import cv2 as cv
import numpy as np
import os
import time
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm

SUPPORTED_IMAGE_FORMATS = ["jpg", "JPG", "jpeg", "JPEG", "png", "PNG"]

FONT_PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "../fonts/ttf-bitstream-vera-1.10/VeraMono.ttf",
)
FONT_SIZE = 16

WATERMARK_FILE_PREFIX = "watermarked_"

# Don't change this one
FSOCO_IMPORT_BORDER_THICKNESS = 140
FSOCO_IMPORT_LOGO_HEIGHT = 100

"""
    Small script for dry-running watermarking.
    Based on the FSOCO Image Import plugin for supervisely.
"""


def watermark(img, logo, last_modified):
    # Resize logo
    logo = resize_logo(logo)

    # Dimension stuff
    img_width = img.shape[1]
    logo_width = logo.shape[1]
    width_diff = img_width - logo_width
    logo_border_diff = FSOCO_IMPORT_BORDER_THICKNESS - FSOCO_IMPORT_LOGO_HEIGHT

    # Border dimensions
    top = bottom = left = right = FSOCO_IMPORT_BORDER_THICKNESS
    # Make borders
    img = cv.copyMakeBorder(img, top, bottom, left, right, cv.BORDER_ISOLATED)
    # Pad logo for easier concatenating
    logo = cv.copyMakeBorder(
        logo, 0, 0, 0, (width_diff + FSOCO_IMPORT_BORDER_THICKNESS), cv.BORDER_ISOLATED
    )

    # Update image shape after borders have been updated
    img_height = img.shape[0]
    # Insert logo into image
    img[
        (img_height - FSOCO_IMPORT_BORDER_THICKNESS) : img_height - logo_border_diff,
        FSOCO_IMPORT_BORDER_THICKNESS:,
    ] = logo
    # Length of this static text (Arial) in pixel
    # See https://www.math.utah.edu/~beebe/fonts/afm-widths.html
    txt_len = 180
    # Add text for creation and modification time
    # Text's anchor is its bottom left corner
    text_anchor_top = (FSOCO_IMPORT_BORDER_THICKNESS, img_height - 30)
    text_anchor_bot = (FSOCO_IMPORT_BORDER_THICKNESS + txt_len, img_height - 30)

    anchors = [text_anchor_top, text_anchor_bot]
    texts = ["Created on:", last_modified]
    img = draw_text_on_img(img, anchors, texts)

    return img


def resize_logo(img_logo):
    # Add black border to the top side to introduce a gap between the logo and the image
    img_logo = cv.copyMakeBorder(
        img_logo, 10, 0, 0, 0, cv.BORDER_CONSTANT, value=[0, 0, 0]
    )

    # FSOCO_IMPORT_LOGO_HEIGHT / Height
    scale_pct = FSOCO_IMPORT_LOGO_HEIGHT / float(img_logo.shape[0])
    resized_width = int(img_logo.shape[1] * scale_pct)

    resized_img_logo = cv.resize(img_logo, (resized_width, FSOCO_IMPORT_LOGO_HEIGHT))

    return resized_img_logo


def draw_text_on_img(cv_img, anchors, texts):
    pil_img = cvmat_to_pil(cv_img)
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

    pil_draw = ImageDraw.Draw(pil_img)

    for anchor, text in zip(anchors, texts):
        pil_draw.text(anchor, text, font=font, fill=(255, 255, 255))

    cv_img = pil_to_cvmat(pil_img)
    return cv_img


def pil_to_cvmat(pil_img):
    # From https://stackoverflow.com/questions/43232813/convert-opencv-image-format-to-pil-image-format
    # use numpy to convert the pil_image into a numpy array
    np_img = np.array(pil_img)

    # convert to an opencv image, notice the COLOR_RGB2BGR which means that
    # the color is converted from RGB to BGR format
    cv_img = cv.cvtColor(np_img, cv.COLOR_RGB2BGR)

    return cv_img


def cvmat_to_pil(cv_img):
    # From https://stackoverflow.com/questions/43232813/convert-opencv-image-format-to-pil-image-format
    # convert from opencv to PIL. Notice the COLOR_BGR2RGB which means that
    # the color is converted from BGR to RGB
    pil_img = Image.fromarray(cv.cvtColor(cv_img, cv.COLOR_BGR2RGB))

    return pil_img


def should_watermark_file(path, logo_path, image_format):
    # File is logo
    if path == logo_path:
        return False
    # Wrong image file format
    elif not path.endswith(image_format):
        return False
    # Watermarked file, skip
    elif os.path.basename(path).startswith(WATERMARK_FILE_PREFIX):
        print(
            "You have already watermarked files in this directory. Running the script again will overwrite these files."
        )
        return False

    return True


def main(cwd, image_format=None, logo_file_name=None):
    if image_format not in SUPPORTED_IMAGE_FORMATS:
        print("Image format not supported:", image_format)
        exit(-1)
    # Save actual cwd to go back after executing script
    original_cwd = os.path.abspath(os.getcwd())
    # Always require directory as a positional argument and change to it
    os.chdir(cwd)
    cwd_paths = os.listdir(os.getcwd())
    logo_path = [
        path for path in cwd_paths if os.path.basename(path).startswith(logo_file_name)
    ]
    if not len(logo_path) == 1:
        print(
            "Please make sure that you only have one logo file in the base directory."
        )
    logo_path = logo_path.pop()
    logo_img = cv.imread(logo_path)

    for subdir, _, files in os.walk(os.getcwd()):
        image_paths = [
            path
            for path in files
            if should_watermark_file(path, logo_path, image_format)
        ]

        for image_path in tqdm(
            image_paths,
            dynamic_ncols=True,
            desc="Watermarking images from sub-directory: {}".format(subdir),
        ):
            last_modified = time.ctime(os.path.getmtime(image_path))
            creation_time = time.ctime(os.path.getctime(image_path))
            img = cv.imread(image_path)

            if last_modified is not None:
                watermarked_img = watermark(img, logo_img, last_modified)
            else:
                watermarked_img = watermark(img, logo_img, creation_time)

            image_path_basename = os.path.basename(image_path)
            watermarked_img_path = image_path.replace(
                image_path_basename, WATERMARK_FILE_PREFIX + image_path_basename
            )
            cv.imwrite(watermarked_img_path, watermarked_img)
    # Go back to original cwd
    os.chdir(original_cwd)
    print("Success")
