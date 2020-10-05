#!/usr/bin/env python
# coding: utf-8

from pathlib import Path

import cv2
import numpy as np

from label_converters.helpers import class_id_to_fsoco
from ..viewer import Viewer


class YoloViewer(Viewer):
    def __init__(self):
        super().__init__()
        self.label_file_extension = ".txt"
        self.images_subdir = "images"
        self.labels_subdir = "labels"

    def _draw_labels(self, label_file: Path, image: np.ndarray):
        image_width = image.shape[1]
        image_height = image.shape[0]

        with open(str(label_file), "r") as label_file:
            for line in label_file:
                data = line.split(" ")
                class_id = int(data[0])
                norm_x, norm_y, norm_bb_width, norm_bb_height = [
                    float(f) for f in data[1:]
                ]

                color = self._class_to_color(class_id_to_fsoco(class_id))

                x = int((norm_x - norm_bb_width / 2) * image_width)
                y = int((norm_y - norm_bb_height / 2) * image_height)
                w = int(norm_bb_width * image_width)
                h = int(norm_bb_height * image_height)

                cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)


def main(input_folder: str, sample_size: float):
    viewer = YoloViewer()
    viewer.main(input_folder, sample_size)
