import numpy as np
import supervisely_lib as sly

from similarity_scorer.utils.logger import Logger
from .label_checker import LabelChecker


class BoundingBoxChecker(LabelChecker):
    def run(self, label: dict):
        if label["geometryType"] != "rectangle":
            raise ValueError(
                f"Wrong label type: {label['geometryType']}. Expected: rectangle."
            )

        # Compute area of bounding box
        corner_points = label["points"]["exterior"]
        label["area"] = np.abs(corner_points[0][0] - corner_points[1][0]) * np.abs(
            corner_points[0][1] - corner_points[1][1]
        )

        is_ok = True
        is_ok &= not self._is_small_label(
            label, minimum_area=25, delete_threshold_area=10
        )
        is_ok &= not self._is_outside_image_frame(label, image_border_size=140)
        return is_ok

    def _is_small_label(
        self, label: dict, minimum_area: int, delete_threshold_area: int = -1
    ):
        is_small_label = label["area"] < minimum_area
        remove_label = label["area"] < delete_threshold_area and self.apply_auto_fixes

        if remove_label:
            self._delete_label(label)
        else:
            self._update_issue_tag(label, "Small label", is_small_label)

        if self.verbose and is_small_label:
            log_text = f'{self.image_name} | bounding box | small label ({label["area"]} < {minimum_area})'
            log_text += " --> removed" if remove_label else ""
            Logger.log_info_alt(log_text)
        if remove_label:
            is_small_label = False
        return is_small_label

    def _is_outside_image_frame(self, label: dict, image_border_size: int):
        # Check if the label reaches into the black border (watermark)

        corners = label["points"]["exterior"]
        min_x = min(corners[0][0], corners[1][0])
        max_x = max(corners[0][0], corners[1][0])
        min_y = min(corners[0][1], corners[1][1])
        max_y = max(corners[0][1], corners[1][1])

        is_outside_image_frame = False
        is_outside_image_frame |= min_x < image_border_size
        is_outside_image_frame |= max_x > self.image_width - image_border_size
        is_outside_image_frame |= min_y < image_border_size
        is_outside_image_frame |= max_y > self.image_height - image_border_size

        if not self.apply_auto_fixes:
            self._update_issue_tag(label, "Inside watermark", is_outside_image_frame)
        elif is_outside_image_frame:
            # Crop bounding box to the main image
            label["points"]["exterior"] = [
                [max(min_x, image_border_size), max(min_y, image_border_size)],
                [
                    min(max_x, self.image_width - image_border_size),
                    min(max_y, self.image_height - image_border_size),
                ],
            ]
            self._update_rectangle_data(label)
            # Remove issue tag if it previously existed
            self._delete_issue_tag(label, "Inside watermark")

        if self.verbose and is_outside_image_frame:
            log_text = f"{self.image_name} | segmentation | inside watermark"
            log_text += " --> fixed" if self.apply_auto_fixes else ""
            Logger.log_info_alt(log_text)
        if self.apply_auto_fixes:
            is_outside_image_frame = False
        return is_outside_image_frame

    def _update_rectangle_data(self, label: dict):
        updated_label = sly.Label.from_json(label, self.project_meta)
        self._update_label(updated_label)
        # Update label object for later checks
        label = updated_label.to_json()
        corner_points = label["points"]["exterior"]
        label["area"] = np.abs(corner_points[0][0] - corner_points[1][0]) * np.abs(
            corner_points[0][1] - corner_points[1][1]
        )
