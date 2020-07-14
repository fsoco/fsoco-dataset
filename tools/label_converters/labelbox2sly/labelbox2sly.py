#!/usr/bin/env python
# coding: utf-8

"""
    Labelbox => Supervisely format

    https://docs.supervise.ly/ann_format/

    \b
    Mappings between naming styles can be adapted in this file:
    tools/label_converters/names_to_fsoco.yaml

    \b
    Input:
    ── images_folder
       ├── img_x.jpeg
       ├── img_y.jpeg
       └── img_z.jpeg
    ── lb_labels_file

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

    Simply drag and drop the project_name folder in Supervisely to create a new project with the converted dataset contained in it.
"""

import json
import os
import shutil
from PIL import Image

from tqdm import tqdm

from ..helpers import fsoco_classes, fsoco_tags, naming_converter
from ..helpers import (
    supervisely_template,
    supervisely_bbox_template,
    supervisely_tag_template,
)

SUPPORTED_IMAGE_FORMATS = ["jpg", "JPG", "jpeg", "JPEG", "png", "PNG"]


def main(
    images_folder=None,
    lb_labels_file=None,
    out_path=None,
    project_name=None,
    dataset_name=None,
):
    with open(lb_labels_file, "r") as f:
        lb_labels = json.load(f)

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

    for filename in tqdm(filenames):
        label = None
        img = Image.open(os.path.join(images_folder, filename))
        for lb_label in lb_labels:
            if lb_label["External ID"] == filename and isinstance(
                lb_label["Label"], dict
            ):
                label = lb_label["Label"]
                break

        sly_label_file = os.path.join(
            sly_labels_folder, os.path.splitext(filename)[0] + ".json"
        )
        sly_label = supervisely_template()
        sly_label["size"]["width"] = img.shape[0]
        sly_label["size"]["height"] = img.shape[1]

        if label is not None:
            for class_name, labels_class in label.items():
                # Skip classes without any object
                if len(labels_class) == 0:
                    continue

                class_name = naming_converter(class_name, convert_class=True)
                if class_name not in fsoco_classes():
                    print(f'\033[91mSkipped not supported class: "{class_name}"\033[0m')
                    continue

                for bbox in labels_class:
                    sly_bbox = supervisely_bbox_template()

                    box_points = bbox["geometry"]
                    box_x = [p["x"] for p in box_points]
                    box_y = [p["y"] for p in box_points]
                    min_x, max_x = min(box_x), max(box_x)
                    min_y, max_y = min(box_y), max(box_y)
                    sly_bbox["classTitle"] = class_name
                    sly_bbox["points"]["exterior"] = [[min_x, min_y], [max_x, max_y]]

                    if "flags" in bbox.keys():
                        bbox_tags = bbox["flags"]
                        for tag_name in bbox_tags:
                            sly_tag = supervisely_tag_template()
                            tag_name = naming_converter(tag_name, convert_tag=True)
                            if tag_name not in fsoco_tags():
                                print(
                                    f'\033[93mSkipped not supported tag: "{tag_name}"\033[0m'
                                )
                                continue
                            else:
                                sly_tag["name"] = tag_name
                            if sly_tag not in sly_bbox["tags"]:
                                sly_bbox["tags"].append(sly_tag)

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
