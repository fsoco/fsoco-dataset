from abc import ABC, abstractmethod

import supervisely_lib as sly
from supervisely_lib.annotation.tag_collection import TagCollection


# ToDo: This is how it should be done if the API would support it
# tagged_label = l.delete_tag(issue_tag)
# Adapted from annotation.py
def label_delete_tag(label, tag):
    retained_tags = []
    for label_tag in label.tags.items():
        if label_tag.meta.name != tag.meta.name or label_tag.value != tag.value:
            retained_tags.append(label_tag)
    return label.clone(tags=TagCollection(items=retained_tags))


class LabelChecker(ABC):
    # All implemented checker share the same object as a single image could contain different label types
    updated_annotation = None

    def __init__(self, image_name: str, updated_annotation, verbose: bool = False):
        super().__init__()
        self.image_name = image_name
        self.verbose = verbose
        LabelChecker.updated_annotation = updated_annotation

    @abstractmethod
    def run(self, label: dict) -> bool:
        pass

    @staticmethod
    def _update_issue_tag(label: dict, tag_text: str, found_issue: bool):
        if found_issue:
            LabelChecker._add_issue_tag(label, tag_text)
        else:
            LabelChecker._delete_issue_tag(label, tag_text)

    @staticmethod
    def _add_issue_tag(label: dict, tag_text: str):
        # Do not tag multiple times
        if LabelChecker._is_issue_tagged(label, tag_text):
            return

        # Search for this label in the updated_annotations object
        for candidate_label in LabelChecker.updated_annotation.labels:
            if candidate_label.geometry.sly_id == label["id"]:
                tagged_label = candidate_label.add_tag(
                    LabelChecker._create_issue_tag(tag_text)
                )
                LabelChecker.updated_annotation = LabelChecker.updated_annotation.delete_label(
                    candidate_label
                ).add_label(
                    tagged_label
                )
                break

    @staticmethod
    def _delete_issue_tag(label: dict, tag_text: str):
        if not LabelChecker._is_issue_tagged(label, tag_text):
            return

        # Search for all of these label and delete them
        for candidate_label in LabelChecker.updated_annotation.labels:
            if candidate_label.geometry.sly_id == label["id"]:
                tagged_label = label_delete_tag(
                    candidate_label, LabelChecker._create_issue_tag(tag_text)
                )
                LabelChecker.updated_annotation = LabelChecker.updated_annotation.delete_label(
                    candidate_label
                ).add_label(
                    tagged_label
                )
                break

    @staticmethod
    def _is_issue_tagged(label: dict, tag_text: str):
        for tag in label["tags"]:
            if tag["name"] == "Issue" and tag["value"] == tag_text:
                return True
        return False

    @staticmethod
    def _create_issue_tag(tag_text: str):
        issue_tag_meta = sly.TagMeta(
            name="Issue", value_type=sly.TagValueType.ANY_STRING
        )
        issue_tag = sly.Tag(meta=issue_tag_meta, value=tag_text)
        return issue_tag
