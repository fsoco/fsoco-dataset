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
        is_ok &= not self._is_small_label(label, minimum_area=10)
        return is_ok

    def _is_small_label(self, label: dict, minimum_area: int):
        is_small_label = label["area"] < minimum_area

        self._update_issue_tag(label, "Small label", is_small_label)

        if self.verbose and is_small_label:
            Logger.log_info_alt(
                f'{self.image_name} | bounding box | small label ({label["area"]} < {minimum_area})'
            )
        return is_small_label
