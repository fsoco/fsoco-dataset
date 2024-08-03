from pathlib import Path
import json
from collections import defaultdict
import os
import shutil
import click
import cv2 as cv
from multiprocessing import Pool
import tqdm
from functools import partial
import zlib
import base64
import numpy as np
import random

from ..helpers import fsoco_to_class_id_mapping
from watermark.watermark import FSOCO_IMPORT_BORDER_THICKNESS


def clean_export_dir(
    yolov8_export_train_dir: Path,
    yolov8_export_test_dir: Path,
    yolov8_export_val_dir: Path,
):

    shutil.rmtree(yolov8_export_train_dir, ignore_errors=True)
    shutil.rmtree(yolov8_export_test_dir, ignore_errors=True)
    shutil.rmtree(yolov8_export_val_dir, ignore_errors=True)
    (yolov8_export_train_dir / "images/").mkdir(parents=True)
    (yolov8_export_test_dir / "images/").mkdir(parents=True)
    (yolov8_export_val_dir / "images/").mkdir(parents=True)
    (yolov8_export_train_dir / "labels/").mkdir(parents=True)
    (yolov8_export_test_dir / "labels/").mkdir(parents=True)
    (yolov8_export_val_dir / "labels/").mkdir(parents=True)


def export_image(
    darknet_export_images_dir: Path,
    src_file: Path,
    new_file_name: str,
    remove_watermark: bool,
):
    if remove_watermark:
        rescale_copy_image(darknet_export_images_dir, src_file, new_file_name)
    else:
        copy_image(darknet_export_images_dir, src_file, new_file_name)


def copy_image(darknet_export_images_dir: Path, src_file: Path, new_file_name: str):
    old_file_name = src_file.name
    shutil.copy(src_file, darknet_export_images_dir)

    dst_file = darknet_export_images_dir / old_file_name
    new_dst_file_name = darknet_export_images_dir / new_file_name
    os.rename(dst_file, new_dst_file_name)


def rescale_copy_image(
    darknet_export_images_dir: Path, src_file: Path, new_file_name: str
):
    image = cv.imread(str(src_file))
    cropped_image = image[
        FSOCO_IMPORT_BORDER_THICKNESS:-FSOCO_IMPORT_BORDER_THICKNESS,
        FSOCO_IMPORT_BORDER_THICKNESS:-FSOCO_IMPORT_BORDER_THICKNESS,
        :,
    ]

    new_dst_file_name = darknet_export_images_dir / new_file_name
    cv.imwrite(str(new_dst_file_name), cropped_image)


def convert_object_entry(
    obj: dict,
    image_width: float,
    image_height: float,
    class_id_mapping: dict,
    remove_watermark: bool,
    exclude_tags: list,
):
    tags = [tag["name"] for tag in obj["tags"]]

    if any(tag in tags for tag in exclude_tags):
        return None, None, None, None, None, None

    class_title = obj["classTitle"]
    class_id = class_id_mapping[class_title]

    left, top = obj["points"]["exterior"][0]
    right, bottom = obj["points"]["exterior"][1]

    if remove_watermark:
        left -= FSOCO_IMPORT_BORDER_THICKNESS
        top -= FSOCO_IMPORT_BORDER_THICKNESS
        right -= FSOCO_IMPORT_BORDER_THICKNESS
        bottom -= FSOCO_IMPORT_BORDER_THICKNESS

        image_width -= 2 * FSOCO_IMPORT_BORDER_THICKNESS
        image_height -= 2 * FSOCO_IMPORT_BORDER_THICKNESS

    mid_x = (left + right) / 2
    mid_y = (top + bottom) / 2

    bb_width = right - left
    bb_height = bottom - top

    norm_x = mid_x / image_width
    norm_y = mid_y / image_height

    norm_bb_width = bb_width / image_width
    norm_bb_height = bb_height / image_height

    if not (
        (0 <= norm_x <= 1)
        or (0 <= norm_y <= 1)
        or (0 <= norm_bb_width <= 1)
        or (0 <= norm_bb_height <= 1)
    ):
        raise RuntimeWarning(
            f"Normalized bounding box values outside the valid range! "
            f"x = {norm_x}; y = {norm_y}; w = {norm_bb_width}; h = {norm_bb_height}"
        )

    return class_id, class_title, norm_x, norm_y, norm_bb_width, norm_bb_height


def convert_object_entry_segmentation(
    obj: dict,
    image_width: float,
    image_height: float,
    class_id_mapping: dict,
    remove_watermark: bool,
    exclude_tags: list,
):
    tags = [tag["name"] for tag in obj["tags"]]

    if any(tag in tags for tag in exclude_tags):
        return None, None

    class_title = obj["classTitle"]
    class_id = class_id_mapping[class_title]

    z = zlib.decompress(base64.b64decode(obj["bitmap"]["data"]))
    n = np.fromstring(z, np.uint8)
    mask = cv.imdecode(n, cv.IMREAD_UNCHANGED)[..., 3]

    contours, _ = cv.findContours(
        mask.astype(np.uint8), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE
    )
    contours = np.vstack(contours)
    contours += obj["bitmap"]["origin"]

    if remove_watermark:
        contours -= FSOCO_IMPORT_BORDER_THICKNESS
        image_width -= 2 * FSOCO_IMPORT_BORDER_THICKNESS
        image_height -= 2 * FSOCO_IMPORT_BORDER_THICKNESS

    # normalize contours
    contours = contours / np.array([image_width, image_height])

    return class_id, class_title, contours


def write_meta_data(
    yolov8_export_base: Path,
    yolov8_train_dir: Path,
    yolov8_test_dir: Path,
    yolov8_val_dir: Path,
    class_id_mapping: dict,
    num_labeled_images: int,
    class_counter: dict,
):
    excluded_by_tag = class_counter.pop("excluded_by_tag", 0)

    # write class id mapping

    with open(yolov8_export_base / "data.yaml", "w") as class_info_file:

        class_info_file.write("train:  'train/images'\n")
        class_info_file.write("test: test/images\n")
        class_info_file.write("val: val/images\n")
        class_info_file.write(f"nc: {len(class_id_mapping)}\n")

        class_info_file.write("names: [")

        for class_name, _ in sorted(class_id_mapping.items(), key=lambda kv: kv[1]):
            class_info_file.write(f"{class_name},")

        class_info_file.write("]\n")

    # write stats

    print(f"\nNumber of exported Images: {num_labeled_images} \n")
    print("\n======================\n")
    print("Objects per class:\n")

    for class_name, count in sorted(
        class_counter.items(), key=lambda kv: kv[1], reverse=True
    ):
        print(f"{class_name} -> {count}")

    if excluded_by_tag > 0:
        print("\n======================\n")
        print(f"Number of objects excluded by tag -> {excluded_by_tag}\n")

    with open(yolov8_export_base / "stats.txt", "w") as class_stat_file:

        class_stat_file.write(f"\nNumber of images: {num_labeled_images}\n")
        class_stat_file.write("\n======================\n")
        class_stat_file.write("Objects per class:\n")

        total_num_objects = 0

        for class_name, count in sorted(
            class_counter.items(), key=lambda kv: kv[1], reverse=True
        ):
            total_num_objects += count
            class_stat_file.write(f"{class_name} -> {count}\n")

        class_stat_file.write(f"\nTotal number of objects: {total_num_objects}\n")

        if excluded_by_tag > 0:
            class_stat_file.write("\n======================\n")
            class_stat_file.write(
                f"Number of objects excluded by tag -> {excluded_by_tag}\n"
            )


def convert_label(
    yolov8_export_train_dir: Path,
    yolov8_export_test_dir: Path,
    yolov8_export_val_dir: Path,
    class_id_mapping: dict,
    remove_watermark: bool,
    segmentation: bool,
    exclude_tags: list,
    label: Path,
):
    class_counter = defaultdict(int)
    name = label.stem
    image = Path(str(label).replace("/ann/", "/img/").replace(".json", ""))

    with open(label) as json_file:
        data = json.load(json_file)

        if len(data["objects"]) > 0:

            selected_path = Path("")

            roll = random.random()
            if roll < 0.7:
                selected_path = yolov8_export_train_dir
            elif roll < 0.9:
                selected_path = yolov8_export_test_dir
            else:
                selected_path = yolov8_export_val_dir

            image_width = data["size"]["width"]
            image_height = data["size"]["height"]

            export_image(selected_path / "images", image, name, remove_watermark)
            label_file_name = (
                selected_path / "labels" / f"{os.path.splitext(name)[0]}.txt"
            )

            with open(label_file_name, "w") as darknet_label:

                for obj in data["objects"]:
                    try:
                        if segmentation:
                            (
                                class_id,
                                class_title,
                                segmentation_mask,
                            ) = convert_object_entry_segmentation(
                                obj,
                                image_height=image_height,
                                image_width=image_width,
                                class_id_mapping=class_id_mapping,
                                remove_watermark=remove_watermark,
                                exclude_tags=exclude_tags,
                            )

                            if class_id is None:
                                class_counter["excluded_by_tag"] += 1
                                continue

                            else:
                                class_counter[class_title] += 1

                                darknet_label.write(
                                    "{} {}\n".format(
                                        class_id,
                                        " ".join(
                                            [
                                                " ".join(map(str, row[0]))
                                                for row in list(segmentation_mask)
                                            ]
                                        ),
                                    )
                                )
                        else:
                            (
                                class_id,
                                class_title,
                                norm_x,
                                norm_y,
                                norm_bb_width,
                                norm_bb_height,
                            ) = convert_object_entry(
                                obj,
                                image_height=image_height,
                                image_width=image_width,
                                class_id_mapping=class_id_mapping,
                                remove_watermark=remove_watermark,
                                exclude_tags=exclude_tags,
                            )

                            if class_id is None:
                                class_counter["excluded_by_tag"] += 1
                                continue

                            else:
                                class_counter[class_title] += 1

                                darknet_label.write(
                                    "{} {} {} {} {}\n".format(
                                        class_id,
                                        norm_x,
                                        norm_y,
                                        norm_bb_width,
                                        norm_bb_height,
                                    )
                                )
                    except RuntimeWarning as e:
                        click.echo(
                            f"[Warning] Failed to convert object entry in {label_file_name} \n -> {e}"
                        )

    return class_counter


def main(
    sly_project_path: str,
    output_path: str,
    remove_watermark: bool,
    segmentation: bool,
    exclude: list,
):
    class_id_mapping = fsoco_to_class_id_mapping()

    sly_base = Path(sly_project_path)
    yolov8_export_base = Path(output_path)

    yolov8_export_train_dir = yolov8_export_base / "train"
    yolov8_export_test_dir = yolov8_export_base / "test"
    yolov8_export_val_dir = yolov8_export_base / "val"

    labels = list(sly_base.glob("*/ann/*.json"))

    clean_export_dir(
        yolov8_export_train_dir, yolov8_export_test_dir, yolov8_export_val_dir
    )

    convert_func = partial(
        convert_label,
        yolov8_export_train_dir,
        yolov8_export_test_dir,
        yolov8_export_val_dir,
        class_id_mapping,
        remove_watermark,
        segmentation,
        exclude,
    )

    global_class_counter = defaultdict(int)

    with Pool() as p:
        for class_counter in tqdm.tqdm(
            p.imap_unordered(convert_func, labels), total=len(labels)
        ):
            for class_name, count in class_counter.items():
                global_class_counter[class_name] += count

    write_meta_data(
        yolov8_export_base,
        yolov8_export_train_dir,
        yolov8_export_test_dir,
        yolov8_export_val_dir,
        class_id_mapping,
        len(labels),
        global_class_counter,
    )
