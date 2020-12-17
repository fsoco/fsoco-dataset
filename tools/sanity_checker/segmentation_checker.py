import numpy as np
import supervisely_lib as sly


class SegmentationChecker:
    def __init__(self, image_height, image_width):
        # We use this to check for overlapping labels within an image
        self.image_mask = np.zeros((image_height, image_width), dtype=np.int)

    def run(self, label: dict):
        assert label["geometryType"] == "bitmap"

        # Create numpy array from bitmap
        mask = sly.geometry.bitmap.Bitmap.base64_2_data(label["bitmap"]["data"])

        is_ok = True
        is_ok &= not self._is_small_label(mask, minimum_area=10)
        is_ok &= not self._is_overlapping_labels(mask, label["bitmap"]["origin"])
        return is_ok

    def _is_small_label(self, mask: np.ndarray, minimum_area: int):
        return np.sum(mask) < minimum_area

    def _is_overlapping_labels(self, mask: np.ndarray, origin: np.ndarray):
        self.image_mask[
            origin[1] : origin[1] + mask.shape[0],
            origin[0] : origin[0] + mask.shape[1],
        ][mask == 1] += mask[mask == 1]
        return np.max(self.image_mask) > 1
