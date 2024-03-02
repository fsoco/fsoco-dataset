#!/usr/bin/env python
# coding: utf-8

import json
import os
import sys
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
            image_mask = np.zeros(image.shape[:2], dtype=int)
            image_mask_color = np.zeros(image.shape, dtype=image.dtype)

            for label in label_data["objects"]:
                color = self._class_to_color(label["classTitle"])
                # color = list(np.random.choice(range(256), size=3))  # debugging

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

                    # Find edges of the shape and paint them black
                    ext_mask = np.zeros(
                        (mask.shape[0] + 2, mask.shape[1] + 2), dtype=int
                    )
                    edge_mask = np.zeros(
                        (mask.shape[0] + 2, mask.shape[1] + 2), dtype=int
                    )
                    ext_mask[1:-1, 1:-1] = mask
                    edge_mask[1:, :] += np.diff(ext_mask, axis=0)
                    edge_mask[:-1, :] += np.diff(-ext_mask, axis=0)
                    edge_mask[:, 1:] += np.diff(ext_mask, axis=1)
                    edge_mask[:, :-1] += np.diff(-ext_mask, axis=1)
                    edge_mask = edge_mask[1:-1, 1:-1]
                    mask_color[edge_mask > 0] = 0

                    # Copy colored instance mask to image-wide mask
                    image_mask_color[
                        origin[1] : origin[1] + mask.shape[0],
                        origin[0] : origin[0] + mask.shape[1],
                        :,
                    ][mask == 1] = mask_color[mask == 1]

            image[image_mask == 1] = image_mask_color[image_mask == 1]

    def main_sample_data(self, input_folder: str, sample_size: float):
        # This tool should work out-of-the-box for the FSOCO sample data.
        # Thus, we activate a special mode if this data has been detected.
        input_folder_content = os.listdir(input_folder)
        if (
            "bounding_boxes" in input_folder_content
            and "segmentation" in input_folder_content
            and "images" in input_folder_content
        ):
            self.images_subdir = "images"
            self.labels_subdir = "bounding_boxes"
            self.main(input_folder, sample_size)
            self.labels_subdir = "segmentation"
            self.main(input_folder, sample_size)
            sys.exit()


def main(input_folder: str, sample_size: float):
    viewer = SuperviselyViewer()
    viewer.main_sample_data(input_folder, sample_size)
    viewer.main(input_folder, sample_size)
