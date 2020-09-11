#!/usr/bin/env python
# coding: utf-8

from pathlib import Path
import math
import cv2
from random import shuffle
from screeninfo import get_monitors
import numpy as np

ID_TO_COLOR = {
    "0": (0, 255, 255),  # yellow
    "1": (255, 0, 42),  # blue
    "2": (0, 128, 255),  # orange
    "3": (42, 0, 255),  # large orange
    "4": (15, 219, 59),  # unknown
}

LABEL_FILE_EXTENSION = ".txt"
IMAGES_SUBDIR = "images"
LABELS_SUBDIR = "labels"

CV_FONT = cv2.FONT_HERSHEY_SIMPLEX

HEIGHT_MARGIN = 180
WIDTH_MARGIN = 20
HEADER_HEIGHT = 85

screen_width = 0
screen_height = 0


def handle_folder(folder: Path, sample_size: float):
    images_directory = folder / IMAGES_SUBDIR
    labels_directory = folder / LABELS_SUBDIR

    if images_directory.exists() and labels_directory.exists():
        label_files = list(labels_directory.glob("*{}".format(LABEL_FILE_EXTENSION)))

        if len(label_files) == 0:
            print(f"{labels_directory} does not contain any label files!")
            return False

        shuffle(label_files)
        num_samples = math.ceil(len(label_files) * sample_size)
        samples = sorted(label_files[:num_samples])

        index = 0
        while True:
            image_file = images_directory / samples[index].stem
            action = handle_image(samples[index], image_file, index, num_samples)

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


def handle_image(label_file: Path, image_file: Path, index: int, total: int):
    if not image_file.exists():
        possible_candidates = list(image_file.parent.glob(f"{image_file.stem}.*"))

        if len(possible_candidates) == 0:
            print(f"Could not find image for label file [{label_file}]")
            return "next"
        elif len(possible_candidates) > 1:
            print(
                f"There are more then one possible image for label file [{label_file}]"
            )
            return "next"
        else:
            image_file = possible_candidates[0]

    image = cv2.imread(str(image_file))

    if image is None:
        print(f"Could not open image [{image_file}]")
        return "next"

    image_width = image.shape[1]
    image_height = image.shape[0]

    with open(label_file, "r") as label_file:

        for line in label_file:
            data = line.split(" ")
            class_id = data[0]
            norm_x, norm_y, norm_bb_width, norm_bb_height = [float(f) for f in data[1:]]

            color = ID_TO_COLOR[str(class_id)]

            x = int((norm_x - norm_bb_width / 2) * image_width)
            y = int((norm_y - norm_bb_height / 2) * image_height)
            w = int(norm_bb_width * image_width)
            h = int(norm_bb_height * image_height)

            cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)

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

    cv2.imshow("image", canvas)

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


def get_screen_size():
    global screen_width, screen_height
    for m in get_monitors():
        if m.width > screen_width and m.height > screen_height:
            screen_width = m.width - WIDTH_MARGIN
            screen_height = m.height - HEIGHT_MARGIN


def main(input_folder: str, sample_size: float):
    get_screen_size()
    handle_folder(Path(input_folder), sample_size=sample_size)
