#!/usr/bin/env python
# coding: utf-8

"""
    Darknet YOLO => Supervisely format

    https://docs.supervise.ly/ann_format/

    \b
    The mapping between Darknet class IDs and the class names we use in FSOCO can be adapted in this file:
    tools/label_converters/class_id_to_fsoco.yaml

    \b
    Input:
    ── images_folder
       ├── img_x.jpeg
       ├── img_y.jpeg
       └── img_z.jpeg
    ── darknet_labels_folder
       ├── img_x.txt
       ├── img_y.txt
       └── img_z.txt

    \b
    Output:
    project_name
    ├── meta.json
    └── dataset_name
        ├── ann
        │   ├── img_x.json
        │   ├── img_y.json
        │   └── img_z.json
        └── img
            ├── img_x.jpeg
            ├── img_y.jpeg
            └── img_z.jpeg

    Simply drag and drop the project_name folder in Supervisely to create a new project with the converted dataset
    contained in it.
"""

import json
import os
import shutil

# TODO Replace OpenCV with PIL since only the image dimensions are required
import cv2
import numpy as np
from tqdm import tqdm

from ..helpers import fsoco_classes, class_id_to_fsoco
from ..helpers import supervisely_template, supervisely_bbox_template

SUPPORTED_IMAGE_FORMATS = ["jpg", "JPG", "jpeg", "JPEG", "png", "PNG"]


def min_max_clip(min_val, max_val, val):
    # Return clipped value in interval [min_val, max_val]
    clipped_value = max(min_val, min(max_val, val))
    return clipped_value


def main(
    images_folder=None,
    darknet_labels_folder=None,
    out_path=None,
    project_name=None,
    dataset_name=None,
):
    sly_project_folder = os.path.join(out_path, project_name)
    sly_labels_folder = os.path.join(out_path, project_name, dataset_name, "ann")
    sly_images_folder = os.path.join(out_path, project_name, dataset_name, "img")
    os.makedirs(sly_project_folder, exist_ok=True)
    os.makedirs(sly_labels_folder, exist_ok=True)
    os.makedirs(sly_images_folder, exist_ok=True)

    filenames = []
    for f in os.listdir(images_folder):
        # Get file extension without leading dot '.'
        extension = os.path.splitext(f)[1][1:]
        if extension in SUPPORTED_IMAGE_FORMATS:
            filenames.append(f)

    darknet_labels = []
    for f in os.listdir(darknet_labels_folder):
        # Get all annotations files to match them with the images
        extension = os.path.splitext(f)[1][1:]
        if extension == "txt":
            darknet_labels.append(f)

    for filename in tqdm(filenames):
        label_file = None
        for f in darknet_labels:
            # Match image and label files
            if os.path.splitext(filename)[0] == os.path.splitext(f)[0]:
                label_file = f
                break

        sly_label_file = os.path.join(
            sly_labels_folder, os.path.splitext(filename)[0] + ".json"
        )
        sly_label = supervisely_template()

        if label_file is not None:
            image = cv2.imread(os.path.join(images_folder, filename))
            image_height, image_width = image.shape[:2]
            sly_label["size"]["height"] = image_height
            sly_label["size"]["width"] = image_width

            with open(os.path.join(darknet_labels_folder, label_file), "r") as f:
                labels = [line.rstrip("\n").split(" ") for line in f.readlines()]

            for label in labels:
                class_id, box_points = int(label[0]), [float(x) for x in label[1:]]

                class_name = class_id_to_fsoco(class_id)
                if class_name not in fsoco_classes():
                    print(f'\033[91mSkipped not supported class: "{class_name}"\033[0m')
                    continue

                pixel_bb_x = int(np.round(box_points[0] * image_width))
                pixel_bb_y = int(np.round(box_points[1] * image_height))
                pixel_bb_w = int(np.round(box_points[2] * image_width))
                pixel_bb_h = int(np.round(box_points[3] * image_height))

                x1, x2 = (pixel_bb_x + pixel_bb_w / 2), (pixel_bb_x - pixel_bb_w / 2)
                y1, y2 = (pixel_bb_y - pixel_bb_h / 2), (pixel_bb_y + pixel_bb_h / 2)

                # Clip pixel values to valid image space
                upper_left = [
                    min_max_clip(0, image_width, x1),
                    min_max_clip(0, image_height, y1),
                ]
                lower_right = [
                    min_max_clip(0, image_width, x2),
                    min_max_clip(0, image_height, y2),
                ]

                sly_bbox = supervisely_bbox_template()
                sly_bbox["classTitle"] = class_name
                sly_bbox["points"]["exterior"] = [upper_left, lower_right]
                sly_label["objects"].append(sly_bbox)

        # Save labels file
        with open(sly_label_file, "w") as f:
            json.dump(sly_label, f, indent=4)

        # Save image file
        shutil.copy(
            os.path.join(images_folder, filename),
            os.path.join(sly_images_folder, filename),
        )

    # Use FSOCO project meta file
    shutil.copy(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "meta.json"),
        os.path.join(sly_project_folder, "meta.json"),
    )
