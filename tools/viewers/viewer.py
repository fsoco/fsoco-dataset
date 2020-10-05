#!/usr/bin/env python
# coding: utf-8

import math
from abc import ABCMeta, abstractmethod
from pathlib import Path
from random import shuffle

import cv2
import numpy as np
from screeninfo import get_monitors


class Viewer(metaclass=ABCMeta):
    HEIGHT_MARGIN = 180
    WIDTH_MARGIN = 20
    HEADER_HEIGHT = 85

    CV_FONT = cv2.FONT_HERSHEY_SIMPLEX

    def __init__(self):
        self.screen_width = 0
        self.screen_height = 0
        self.label_file_extension = ""
        self.images_subdir = ""
        self.labels_subdir = ""

    def main(self, input_folder: str, sample_size: float):
        self._get_screen_size()
        self._handle_folder(Path(input_folder), sample_size)

    @abstractmethod
    def _draw_labels(self, label_file: Path, image: np.ndarray):
        pass

    @staticmethod
    def _class_to_color(class_name: str):
        if "yellow" in class_name:
            return 0, 255, 255
        elif "blue" in class_name:
            return 255, 0, 42
        elif "orange" in class_name and "large" not in class_name:
            return 0, 128, 255
        elif "large_orange" in class_name:
            return 42, 0, 255
        else:
            return 15, 219, 59

    def _get_screen_size(self):
        for m in get_monitors():
            if m.width > self.screen_width and m.height > self.screen_height:
                self.screen_width = m.width - self.WIDTH_MARGIN
                self.screen_height = m.height - self.HEIGHT_MARGIN

    def _handle_folder(self, folder: Path, sample_size: float):
        images_directory = folder / self.images_subdir
        labels_directory = folder / self.labels_subdir

        if images_directory.exists() and labels_directory.exists():
            label_files = list(
                labels_directory.glob("*{}".format(self.label_file_extension))
            )

            if len(label_files) == 0:
                print(f"[ERROR] {labels_directory} does not contain any label files!")
                return False

            shuffle(label_files)
            num_samples = math.ceil(len(label_files) * sample_size)
            samples = sorted(label_files[:num_samples])

            index = 0
            while True:
                image_file = images_directory / samples[index].stem
                action = self._handle_image(
                    samples[index], image_file, index, num_samples
                )

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
            print(f"[ERROR] {folder} does not contain a labels or images directory!")

    def _handle_image(self, label_file: Path, image_file: Path, index: int, total: int):
        if not image_file.exists():
            possible_candidates = list(image_file.parent.glob(f"{image_file.stem}.*"))

            if len(possible_candidates) == 0:
                print(f"[WARNING] Could not find image for label file [{label_file}]")
                return "next"
            elif len(possible_candidates) > 1:
                print(
                    f"[WARNING] There is more than one possible image for label file [{label_file}]"
                )
                return "next"
            else:
                image_file = possible_candidates[0]

        image = cv2.imread(str(image_file))
        if image is None:
            print(f"[ERROR] Could not open image [{image_file}]")
            return "next"

        image_width = image.shape[1]
        image_height = image.shape[0]

        self._draw_labels(label_file, image)

        # rescale to fit screen
        ratio = image_width / image_height
        new_width = int(self.screen_width)
        new_height = int(self.screen_width / ratio)
        if new_height > self.screen_height:
            new_width = int(self.screen_height * ratio)
            new_height = int(self.screen_height)
        resized_image = cv2.resize(
            image, (new_width, new_height), interpolation=cv2.INTER_AREA
        )

        canvas = np.zeros((new_height + Viewer.HEADER_HEIGHT, new_width, 3), np.uint8)
        canvas[Viewer.HEADER_HEIGHT :, :, :] = resized_image

        cv2.putText(
            canvas,
            "press 'n' for next | 'p' for previous | 'q' for quit",
            (20, 30),
            Viewer.CV_FONT,
            1.0,
            (255, 255, 255),
            2,
        )

        cv2.putText(
            canvas,
            f"[{index + 1}/{total}] {image_file}",
            (20, 70),
            Viewer.CV_FONT,
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
