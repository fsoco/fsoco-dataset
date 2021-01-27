# coding: utf-8
from pathlib import Path
from collections import defaultdict
import os
import shutil

import cv2 as cv
from multiprocessing import Pool
from tqdm import tqdm
from functools import partial
import pascal_voc_writer

from supervisely_lib.io import fs as fs_utils
from supervisely_lib.project.project import Project, OpenMode, Dataset
from supervisely_lib.annotation.annotation import Annotation
from supervisely_lib.geometry.rectangle import Rectangle
from typing import Dict

from watermark.watermark import FSOCO_IMPORT_BORDER_THICKNESS

OUT_IMG_EXT = ".jpg"
XML_EXT = ".xml"
TXT_EXT = ".txt"


def save_images_lists(path: Path, tags_to_lists: Dict[str, list]):
    for tag_name, samples_desc_list in tags_to_lists.items():
        with open(str(path / f"{tag_name}{TXT_EXT}"), "a+") as fout:
            for record in samples_desc_list:
                fout.write(f"{record[0]}  {record[1]}\n")
                # 0 - sample name, 1 - objects count


def get_total_num_images(project: Project):
    total_num = 0
    for dataset in project.datasets:
        total_num += len(dataset)

    return total_num


def iterate_project(
    save_path: Path, project: Project, remove_watermark: bool, merge: bool
):
    # Create root pascal 'datasets' folders
    with tqdm(
        total=get_total_num_images(project), desc="convertig labels", unit="images"
    ) as pbar:
        for dataset in project.datasets:

            if merge:
                pascal_dataset_path = save_path
            else:
                pascal_dataset_path = save_path / f"{dataset.name}"

            images_dir = pascal_dataset_path / "JPEGImages"
            anns_dir = pascal_dataset_path / "Annotations"
            lists_dir = pascal_dataset_path / "ImageSets" / "Layout"

            pascal_dataset_path.mkdir(exist_ok=True, parents=True)
            images_dir.mkdir(exist_ok=True, parents=True)
            anns_dir.mkdir(exist_ok=True, parents=True)
            lists_dir.mkdir(exist_ok=True, parents=True)

            samples_by_tags = iterate_dataset(
                dataset, images_dir, anns_dir, project, remove_watermark, pbar
            )
            save_images_lists(lists_dir, samples_by_tags)


def iterate_dataset(
    dataset: Dataset,
    images_dir: Path,
    anns_dir: Path,
    project: Project,
    remove_watermark: bool,
    pbar: tqdm,
):
    samples_by_tags = defaultdict(list)  # TRAIN: [img_1, img2, ..]

    convert_func = partial(
        handle_image,
        dataset,
        images_dir,
        anns_dir,
        project,
        remove_watermark,
    )

    with Pool() as p:
        for info in p.imap_unordered(convert_func, dataset):
            img_tags, no_ext_name, len_ann_labels = info

            for tag in img_tags:
                samples_by_tags[tag.name].append((no_ext_name, len_ann_labels))

            pbar.update(1)

    return samples_by_tags


def export_image(
    voc_export_images_dir: Path,
    src_file: Path,
    new_file_name: str,
    remove_watermark: bool,
):
    if remove_watermark:
        rescale_copy_image(voc_export_images_dir, src_file, new_file_name)
    else:
        copy_image(voc_export_images_dir, src_file, new_file_name)


def copy_image(voc_export_images_dir: Path, src_file: Path, new_file_name: str):
    old_file_name = src_file.name
    shutil.copy(src_file, voc_export_images_dir)

    dst_file = voc_export_images_dir / old_file_name
    new_dst_file_name = voc_export_images_dir / new_file_name
    os.rename(dst_file, new_dst_file_name)


def rescale_copy_image(voc_export_images_dir: Path, src_file: Path, new_file_name: str):
    image = cv.imread(str(src_file))
    cropped_image = image[
        FSOCO_IMPORT_BORDER_THICKNESS:-FSOCO_IMPORT_BORDER_THICKNESS,
        FSOCO_IMPORT_BORDER_THICKNESS:-FSOCO_IMPORT_BORDER_THICKNESS,
        :,
    ]

    new_dst_file_name = voc_export_images_dir / new_file_name
    cv.imwrite(str(new_dst_file_name), cropped_image)


def handle_image(
    dataset: Dataset,
    images_dir: Path,
    anns_dir: Path,
    project: Project,
    remove_watermark: bool,
    item_name: str,
):
    img_path, ann_path = dataset.get_item_paths(item_name)
    no_ext_name = fs_utils.get_file_name(item_name)
    pascal_img_path = os.path.join(images_dir, no_ext_name + OUT_IMG_EXT)
    pascal_ann_path = os.path.join(anns_dir, no_ext_name + XML_EXT)

    export_image(images_dir, img_path, no_ext_name + OUT_IMG_EXT, remove_watermark)

    ann = Annotation.load_json_file(ann_path, project_meta=project.meta)

    writer = pascal_voc_writer.Writer(
        path=pascal_img_path, width=ann.img_size[1], height=ann.img_size[0]
    )

    for label in ann.labels:
        obj_class = label.obj_class
        rect: Rectangle = label.geometry.to_bbox()

        xmin = rect.left
        ymin = rect.top
        xmax = rect.right
        ymax = rect.bottom

        if remove_watermark:
            xmin -= FSOCO_IMPORT_BORDER_THICKNESS
            ymin -= FSOCO_IMPORT_BORDER_THICKNESS
            xmax -= FSOCO_IMPORT_BORDER_THICKNESS
            ymax -= FSOCO_IMPORT_BORDER_THICKNESS

        writer.addObject(
            name=obj_class.name,
            xmin=xmin,
            ymin=ymin,
            xmax=xmax,
            ymax=ymax,
        )

    writer.save(pascal_ann_path)
    return ann.img_tags, no_ext_name, len(ann.labels)


def main(sly_project_path: str, output_path: str, remove_watermark: bool, merge: bool):
    output_path = Path(output_path)
    if output_path.exists():
        shutil.rmtree(output_path)

    sly_project = Project(sly_project_path, OpenMode.READ)
    iterate_project(output_path, sly_project, remove_watermark, merge)
