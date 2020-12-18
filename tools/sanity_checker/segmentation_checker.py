import numpy as np
import supervisely_lib as sly

from similarity_scorer.utils.logger import Logger
from .label_checker import LabelChecker


class SegmentationChecker(LabelChecker):
    def __init__(self, image_height: int, image_width: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # We use this to check for overlapping labels within an image
        self.image_mask = np.zeros((image_height, image_width), dtype=np.int)

    def run(self, label: dict):
        if label["geometryType"] != "bitmap":
            raise ValueError(f"Wrong label type: {label['geometryType']}")

        # Create numpy array from bitmap
        label["mask"] = sly.geometry.bitmap.Bitmap.base64_2_data(
            label["bitmap"]["data"]
        )

        is_ok = True
        is_ok &= not self._is_small_label(label, minimum_area=10)
        is_ok &= not self._is_overlapping_label(label)
        return is_ok

    def _is_small_label(self, label: dict, minimum_area: int):
        is_small_label = np.sum(label["mask"]) < minimum_area

        self._update_issue_tag(label, "Small label", is_small_label)

        if self.verbose and is_small_label:
            Logger.log_info_alt(
                f'{self.image_name} | segmentation | small label ({np.sum(label["mask"])} < {minimum_area})'
            )
        return is_small_label

    def _is_overlapping_label(self, label: dict):
        mask = label["mask"]
        origin = label["bitmap"]["origin"]
        self.image_mask[
            origin[1] : origin[1] + mask.shape[0],
            origin[0] : origin[0] + mask.shape[1],
        ][mask == 1] += mask[mask == 1]
        is_overlapping_label = np.max(self.image_mask) > 1

        # Reset the check so that other labels do not trigger it again just because it has been triggered before
        self.image_mask[self.image_mask > 1] = 1

        self._update_issue_tag(label, "Overlapping label", is_overlapping_label)

        if self.verbose and is_overlapping_label:
            Logger.log_info_alt(f"{self.image_name} | segmentation | overlapping label")
        return is_overlapping_label
