from abc import ABC, abstractmethod
from typing import Optional
import functools

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


def check_label_existence(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        # A previous check delete the label. Thus, fallback to returning no issue.
        if self.label is None:
            return False
        return func(self, *args, **kwargs)

    return wrapper


class LabelChecker(ABC):
    # All implemented checker share the same object as a single image could contain different label types
    updated_annotation = None
    is_annotation_updated = None

    issue_tag_meta = sly.TagMeta(
        name="issue", value_type=sly.TagValueType.ANY_STRING, color=[255, 0, 0]
    )
    resolved_tag_meta = sly.TagMeta(
        name="resolved", value_type=sly.TagValueType.NONE, color=[0, 255, 0]
    )

    def __init__(
        self,
        image_name: str,
        image_height: int,
        image_width: int,
        project_meta,
        updated_annotation,
        apply_auto_fixes: bool,
        verbose: bool = False,
    ):
        super().__init__()
        self.image_name = image_name
        self.project_meta = project_meta
        self.apply_auto_fixes = apply_auto_fixes
        self.verbose = verbose
        LabelChecker.updated_annotation = updated_annotation
        LabelChecker.is_annotation_updated = False

        # We use these numbers to check for labels reaching into the watermark
        self.image_height = image_height
        self.image_width = image_width

        # The checks run on this object
        self.label: Optional[dict] = None

    @abstractmethod
    def run(self, label: dict) -> bool:
        pass

    @staticmethod
    def _delete_label(label: dict):
        # Search for this label in the updated_annotations object
        for candidate_label in LabelChecker.updated_annotation.labels:
            if candidate_label.geometry.sly_id == label["id"]:
                LabelChecker.updated_annotation = LabelChecker.updated_annotation.delete_label(
                    candidate_label
                )
                LabelChecker.is_annotation_updated = True
                break

    @staticmethod
    def _update_label(updated_label):
        # Search for this label in the updated_annotations object
        for candidate_label in LabelChecker.updated_annotation.labels:
            if candidate_label.geometry.sly_id == updated_label.geometry.sly_id:
                LabelChecker.updated_annotation = LabelChecker.updated_annotation.delete_label(
                    candidate_label
                ).add_label(
                    updated_label
                )
                LabelChecker.is_annotation_updated = True
                break

    @staticmethod
    def _update_issue_tag(label: dict, tag_text: str, found_issue: bool):
        if found_issue:
            LabelChecker._add_issue_tag(label, tag_text)
        else:
            LabelChecker._delete_issue_tag(label, tag_text)

    @staticmethod
    def _add_issue_tag(label: dict, tag_text: str):
        # Do not tag multiple times
        if LabelChecker.is_issue_tagged(label, tag_text):
            return

        # Search for this label in the updated_annotations object
        for candidate_label in LabelChecker.updated_annotation.labels:
            if candidate_label.geometry.sly_id == label["id"]:
                updated_label = candidate_label.add_tag(
                    sly.Tag(meta=LabelChecker.issue_tag_meta, value=tag_text)
                )
                LabelChecker.updated_annotation = LabelChecker.updated_annotation.delete_label(
                    candidate_label
                ).add_label(
                    updated_label
                )
                LabelChecker.is_annotation_updated = True
                break

    @staticmethod
    def _delete_issue_tag(label: dict, tag_text: str):
        if not LabelChecker.is_issue_tagged(label, tag_text):
            return

        # Search for this label in the updated_annotations object
        for candidate_label in LabelChecker.updated_annotation.labels:
            if candidate_label.geometry.sly_id == label["id"]:
                updated_label = label_delete_tag(
                    candidate_label,
                    sly.Tag(meta=LabelChecker.issue_tag_meta, value=tag_text),
                )
                LabelChecker.updated_annotation = LabelChecker.updated_annotation.delete_label(
                    candidate_label
                ).add_label(
                    updated_label
                )
                LabelChecker.is_annotation_updated = True
                break

    @staticmethod
    def is_issue_tagged(label: dict, tag_text: Optional[str] = None):
        for tag in label["tags"]:
            if tag["name"] == LabelChecker.issue_tag_meta.name:
                if tag_text is None:
                    return True
                elif tag["value"] == tag_text:
                    return True
        return False

    @staticmethod
    def is_resolved_tagged(label: dict):
        for tag in label["tags"]:
            if tag["name"] == LabelChecker.resolved_tag_meta.name:
                return True
        return False
