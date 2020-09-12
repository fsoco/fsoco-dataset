#!/usr/bin/env python
# coding: utf-8

import json
import math
from pathlib import Path
from random import shuffle

import cv2
import numpy as np
from screeninfo import get_monitors

from .sly_viever_helper import base64_2_mask

LABEL_FILE_EXTENSION = ".json"
IMAGES_SUBDIR = "img"
LABELS_SUBDIR = "ann"

CV_FONT = cv2.FONT_HERSHEY_SIMPLEX

HEIGHT_MARGIN = 180
WIDTH_MARGIN = 20
HEADER_HEIGHT = 85

screen_width = 0
screen_height = 0


def _class_to_color(class_name: str):
    if "blue" in class_name:
        return 255, 0, 42
    elif "yellow" in class_name:
        return 0, 255, 255
    elif "orange" in class_name and "large" not in class_name:
        return 0, 128, 255
    elif "large_orange" in class_name:
        return 42, 0, 255
    else:
        return 15, 219, 59


def _handle_folder(folder: Path, sample_size: float):
    images_directory = folder / IMAGES_SUBDIR
    labels_directory = folder / LABELS_SUBDIR

    if images_directory.exists() and labels_directory.exists():
        label_files = list(labels_directory.glob("*{}".format(LABEL_FILE_EXTENSION)))

        if not len(label_files):
            print(f"{labels_directory} does not contain any label files!")
            return False

        shuffle(label_files)
        num_samples = math.ceil(len(label_files) * sample_size)
        samples = sorted(label_files[:num_samples])

        index = 0
        while True:
            image_file = images_directory / samples[index].stem
            label_file = labels_directory / samples[index].stem
            label_file = label_file.parent / (label_file.name + LABEL_FILE_EXTENSION)
            action = _handle_image(label_file, image_file, index, num_samples)

            if action == "next":
                index += 1
                if index >= num_samples:
                    index = 0
            elif action == "previous":
                index -= 1
                if index < 0:
                    index = num_samples - 1
            elif action == "quit":
                break

    else:
        print(f"{folder} does not contain a labels or images directory!")


def _handle_image(label_file: Path, image_file: Path, index: int, total: int):
    image = cv2.imread(str(image_file))
    image_width = image.shape[1]
    image_height = image.shape[0]

    with open(str(label_file), "r") as label_file:
        label_data = json.load(label_file)
        image_mask = np.zeros(image.shape[:2], dtype=np.int)
        image_mask_color = np.zeros(image.shape, dtype=image.dtype)

        for label in label_data["objects"]:
            color = _class_to_color(label["classTitle"])

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

    # rescale to fit screen
    ratio = image_width / image_height
    new_width = int(screen_width)
    new_height = int(screen_width / ratio)
    if new_height > screen_height:
        new_width = int(screen_height * ratio)
        new_height = int(screen_height)
    resized_image = cv2.resize(
        image, (new_width, new_height), interpolation=cv2.INTER_AREA
    )
    canvas = np.zeros((new_height + HEADER_HEIGHT, new_width, 3), np.uint8)
    canvas[HEADER_HEIGHT:, :, :] = resized_image

    cv2.putText(
        canvas,
        "press 'n' for next | 'p' for previous | 'q' for quit",
        (20, 30),
        CV_FONT,
        1.0,
        (255, 255, 255),
        2,
    )
    cv2.putText(
        canvas,
        f"[{index + 1}/{total}] {image_file}",
        (20, 70),
        CV_FONT,
        1.0,
        (255, 255, 255),
        2,
    )
    cv2.imshow("FSOCO label viewer", canvas)

    action = ""
    while True:
        key = cv2.waitKey(1)
        if key == ord("n"):
            action = "next"
            break
        elif key == ord("p"):
            action = "previous"
            break
        elif key == ord("q"):
            action = "quit"
            break

    return action


def _get_screen_size():
    global screen_width, screen_height
    for m in get_monitors():
        if m.width > screen_width and m.height > screen_height:
            screen_width = m.width - WIDTH_MARGIN
            screen_height = m.height - HEIGHT_MARGIN


def main(input_folder, sample_size):
    _get_screen_size()
    _handle_folder(Path(input_folder), sample_size)
