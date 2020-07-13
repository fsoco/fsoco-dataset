import copy
import json
import os

import yaml


def fsoco_classes(bboxes=True, segmentation=True):
    meta_classes = _fsoco_meta()["classes"]
    classes = []
    for fsoco_class in meta_classes:
        if bboxes and fsoco_class["shape"] == "rectangle":
            classes.append(fsoco_class["title"])
        if segmentation and fsoco_class["shape"] == "bitmap":
            classes.append(fsoco_class["title"])
    return classes


def fsoco_tags():
    meta_tags = _fsoco_meta()["tags"]
    tags = [t["name"] for t in meta_tags]
    return tags


def _fsoco_meta():
    with open(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "meta.json"), "r"
    ) as f:
        meta_data = json.load(f)
    return meta_data


def class_id_to_fsoco(class_id):
    mapping_file = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "class_id_to_fsoco.yaml"
    )
    with open(mapping_file, "r") as f:
        mapping_dict = yaml.full_load(f)
    for class_name, class_ids in mapping_dict.items():
        if isinstance(class_ids, int) and class_id == class_ids:
            return class_name
        elif isinstance(class_ids, list) and class_id in class_ids:
            return class_name
    return None


def naming_converter(name, convert_class=False, convert_tag=False):
    mapping_file = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "names_to_fsoco.yaml"
    )
    with open(mapping_file, "r") as f:
        mapping_dict = yaml.full_load(f)
    if convert_class:
        mapping_dict = mapping_dict["classes"]
    elif convert_tag:
        mapping_dict = mapping_dict["tags"]
    for fsoco_name, custom_names in mapping_dict.items():
        if isinstance(custom_names, str) and name == custom_names:
            return fsoco_name
        elif isinstance(custom_names, list) and name in custom_names:
            return fsoco_name
    return name


def supervisely_template():
    template_format = {
        "description": "",
        "tags": [],
        "size": {"height": None, "width": None},
        "objects": [],
    }
    return copy.deepcopy(template_format)


def supervisely_bbox_template():
    template_format = {
        "description": "",
        "geometryType": "rectangle",
        "tags": [],
        "classTitle": "",
        "points": {"exterior": [], "interior": []},
    }
    return copy.deepcopy(template_format)


def supervisely_tag_template():
    template_format = {"name": "", "value": None}
    return copy.deepcopy(template_format)
