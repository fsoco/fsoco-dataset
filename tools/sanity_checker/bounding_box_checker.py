import numpy as np
import supervisely_lib as sly

from similarity_scorer.utils.logger import Logger
from .label_checker import LabelChecker, check_label_existence


class BoundingBoxChecker(LabelChecker):
    def __init__(self, *args):
        super().__init__(*args)

        # Used to check for redundant boxes
        self.previous_labels = []

    def run(self, label: dict):
        if label["geometryType"] != "rectangle":
            raise ValueError(
                f"Wrong label type: {label['geometryType']}. Expected: rectangle."
            )
        # Do not run the checker on labels tagged as "resolved"
        if LabelChecker.is_resolved_tagged(label):
            return True
        # Run all checks on the same label.
        self.label = label

        # Compute area of bounding box
        corner_points = self.label["points"]["exterior"]
        self.label["area"] = np.abs(corner_points[0][0] - corner_points[1][0]) * np.abs(
            corner_points[0][1] - corner_points[1][1]
        )

        is_ok = True
        is_ok &= not self._is_repeated_box(maximum_distance=2)
        is_ok &= not self._is_small_label(minimum_area=20, delete_threshold_area=10)
        is_ok &= not self._is_outside_image_frame(image_border_size=140)
        is_ok &= not self._is_distorted_box(
            minimum_ratio=0.5, maximum_ratio=3.0, skip_if_truncated=True
        )
        return is_ok

    @check_label_existence
    def _is_repeated_box(self, maximum_distance: int = 0):
        # This checks for redundant boxes:
        # - if the location, the class, and the tags are equal, the current label is removed
        # - if there are differences, add an issue tag

        category = self.label["classTitle"]
        tags = [tag["name"] for tag in self.label["tags"]]
        corner_points = self.label["points"]["exterior"]

        is_repeated_box = False
        for previous_label in self.previous_labels:
            if (
                category == previous_label[0]
                and tags == previous_label[1]
                and corner_points == previous_label[2]
            ):
                # Remove the redundant label
                Logger.log_info_alt("Remove label")
                if self.apply_auto_fixes:
                    self._delete_label(self.label)
                else:
                    is_repeated_box = True
            elif (
                np.abs(np.array(corner_points) - np.array(previous_label[2]))
                <= maximum_distance
            ).all():
                # Add an issue tag
                is_repeated_box = True
        self.previous_labels.append((category, tags, corner_points))

        self._update_issue_tag(self.label, "Repeated label", is_repeated_box)

        if self.verbose and is_repeated_box:
            log_text = f"{self.image_name} | bounding box | repeated label"
            Logger.log_info_alt(log_text)
        return is_repeated_box

    @check_label_existence
    def _is_small_label(self, minimum_area: int, delete_threshold_area: int = -1):
        is_small_label = self.label["area"] < minimum_area
        remove_label = (
            self.label["area"] < delete_threshold_area and self.apply_auto_fixes
        )

        if remove_label:
            self._delete_label(self.label)
        else:
            self._update_issue_tag(self.label, "Small label", is_small_label)

        if self.verbose and is_small_label:
            log_text = f'{self.image_name} | bounding box | small label ({self.label["area"]} < {minimum_area})'
            log_text += " --> removed" if remove_label else ""
            Logger.log_info_alt(log_text)
        if remove_label:
            is_small_label = False
            self.label = None
        return is_small_label

    @check_label_existence
    def _is_outside_image_frame(self, image_border_size: int):
        # Check if the label reaches into the black border (watermark)

        corner_points = self.label["points"]["exterior"]
        min_x = min(corner_points[0][0], corner_points[1][0])
        max_x = max(corner_points[0][0], corner_points[1][0])
        min_y = min(corner_points[0][1], corner_points[1][1])
        max_y = max(corner_points[0][1], corner_points[1][1])

        is_outside_image_frame = False
        is_outside_image_frame |= min_x < image_border_size
        is_outside_image_frame |= max_x > self.image_width - image_border_size
        is_outside_image_frame |= min_y < image_border_size
        is_outside_image_frame |= max_y > self.image_height - image_border_size

        if not self.apply_auto_fixes:
            self._update_issue_tag(
                self.label, "Inside watermark", is_outside_image_frame
            )
        elif is_outside_image_frame:
            # Crop bounding box to the main image
            self.label["points"]["exterior"] = [
                [max(min_x, image_border_size), max(min_y, image_border_size)],
                [
                    min(max_x, self.image_width - image_border_size),
                    min(max_y, self.image_height - image_border_size),
                ],
            ]
            self._update_rectangle_data()
            # Remove issue tag if it previously existed
            self._delete_issue_tag(self.label, "Inside watermark")
            # Increment fixed_issue counter
            self._increment_fixed_issue_tag(self.label)

        if self.verbose and is_outside_image_frame:
            log_text = f"{self.image_name} | bounding box | inside watermark"
            log_text += " --> fixed" if self.apply_auto_fixes else ""
            Logger.log_info_alt(log_text)
        if self.apply_auto_fixes:
            is_outside_image_frame = False
        return is_outside_image_frame

    @check_label_existence
    def _is_distorted_box(
        self, minimum_ratio: float, maximum_ratio: float, skip_if_truncated: bool
    ):
        # maximum_ratio: height to width
        # The reason for a distorted box could be that the box covers multiple labels

        if skip_if_truncated and self.is_tagged(self.label, "truncated"):
            return False

        corner_points = self.label["points"]["exterior"]
        box_width = np.abs(corner_points[0][0] - corner_points[1][0])
        box_height = np.abs(corner_points[0][1] - corner_points[1][1])
        ratio = box_height / box_width
        greater_max_ratio = ratio > maximum_ratio
        smaller_min_ratio = ratio < minimum_ratio
        is_distorted_box = greater_max_ratio or smaller_min_ratio

        self._update_issue_tag(self.label, "Suspicious aspect ratio", is_distorted_box)

        if self.verbose and is_distorted_box:
            log_text = f"{self.image_name} | bounding box | aspect ratio ({np.round(ratio, 1)} "
            if greater_max_ratio:
                log_text += f"> {maximum_ratio})"
            elif smaller_min_ratio:
                log_text += f"< {minimum_ratio})"
            Logger.log_info_alt(log_text)
        return is_distorted_box

    def _update_rectangle_data(self):
        updated_label = sly.Label.from_json(self.label, self.project_meta)
        self._update_label(updated_label)
        # Update label object for later checks
        self.label = updated_label.to_json()
        corner_points = self.label["points"]["exterior"]
        self.label["area"] = np.abs(corner_points[0][0] - corner_points[1][0]) * np.abs(
            corner_points[0][1] - corner_points[1][1]
        )
