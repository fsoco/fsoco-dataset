# from https://docs.supervise.ly/data-organization/import-export/supervisely-format

import base64
import io
import zlib

import cv2
import numpy as np
from PIL import Image


def base64_2_mask(s):
    z = zlib.decompress(base64.b64decode(s))
    n = np.fromstring(z, np.uint8)
    mask = cv2.imdecode(n, cv2.IMREAD_UNCHANGED)[:, :, 3].astype(bool)
    return mask


def mask_2_base64(mask):
    img_pil = Image.fromarray(np.array(mask, dtype=np.uint8))
    img_pil.putpalette([0, 0, 0, 255, 255, 255])
    bytes_io = io.BytesIO()
    img_pil.save(bytes_io, format="PNG", transparency=0, optimize=0)
    bytes_value = bytes_io.getvalue()
    return base64.b64encode(zlib.compress(bytes_value)).decode("utf-8")
