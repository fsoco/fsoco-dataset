import numpy as np

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
