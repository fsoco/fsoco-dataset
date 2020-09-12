#!/usr/bin/env python
# coding: utf-8

import json
from pathlib import Path

import cv2
import numpy as np

from .sly_viewer_helper import base64_2_mask
from ..viewer import Viewer


class SuperviselyViewer(Viewer):
    def __init__(self):
        super().__init__()
        self.label_file_extension = ".json"
        self.images_subdir = "img"
        self.labels_subdir = "ann"

    def _draw_labels(self, label_file: Path, image: np.ndarray):
        with open(str(label_file), "r") as label_file:
            label_data = json.load(label_file)
            image_mask = np.zeros(image.shape[:2], dtype=np.int)
            image_mask_color = np.zeros(image.shape, dtype=image.dtype)

            for label in label_data["objects"]:
                color = self._class_to_color(label["classTitle"])

                if label["geometryType"] == "rectangle":
                    pt1 = tuple(int(x) for x in label["points"]["exterior"][0])
                    pt2 = tuple(int(x) for x in label["points"]["exterior"][1])
                    cv2.rectangle(image, pt1, pt2, color, 2)

                elif label["geometryType"] == "bitmap":
                    mask = base64_2_mask(label["bitmap"]["data"])
                    origin = label["bitmap"]["origin"]
                    image_mask[
                        origin[1] : origin[1] + mask.shape[0],
                        origin[0] : origin[0] + mask.shape[1],
                    ][mask == 1] = mask[mask == 1]
                    mask_color = np.repeat(mask[:, :, np.newaxis], 3, axis=2) * color
                    image_mask_color[
                        origin[1] : origin[1] + mask.shape[0],
                        origin[0] : origin[0] + mask.shape[1],
                        :,
                    ][mask == 1] = mask_color[mask == 1]

            image[image_mask == 1] = image_mask_color[image_mask == 1]


def main(input_folder: str, sample_size: float):
    viewer = SuperviselyViewer()
    viewer.main(input_folder, sample_size)
