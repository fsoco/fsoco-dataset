import numpy as np
import supervisely_lib as sly
from scipy import ndimage

from similarity_scorer.utils.logger import Logger
from .label_checker import LabelChecker


class SegmentationChecker(LabelChecker):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # We use this to check for overlapping labels within an image
        self.image_mask = np.zeros((self.image_height, self.image_width), dtype=np.int)

    def run(self, label: dict):
        if label["geometryType"] != "bitmap":
            raise ValueError(
                f"Wrong label type: {label['geometryType']}. Expected: bitmap."
            )
        # Run all checks on the same label.
        self.label = label

        # Create numpy array from bitmap
        self.label["mask"] = sly.geometry.bitmap.Bitmap.base64_2_data(
            self.label["bitmap"]["data"]
        )

        is_ok = True
        is_ok &= not self._is_small_label(minimum_area=10, delete_threshold_area=5)
        is_ok &= not self._is_outside_image_frame(image_border_size=140)
        is_ok &= not self._is_ghost_bounding_box()
        is_ok &= not self._is_perforated()
        is_ok &= not self._is_overlapping_label()
        is_ok &= not self._is_distorted_box(
            minimum_ratio=0.5, maximum_ratio=3.0
        )  # Should be after ghost_box check
        return is_ok

    def _is_small_label(self, minimum_area: int, delete_threshold_area: int = -1):
        is_small_label = np.sum(self.label["mask"]) < minimum_area
        remove_label = (
            np.sum(self.label["mask"]) < delete_threshold_area and self.apply_auto_fixes
        )

        if remove_label:
            self._delete_label(self.label)
        else:
            self._update_issue_tag(self.label, "Small label", is_small_label)

        if self.verbose and is_small_label:
            log_text = f'{self.image_name} | segmentation | small label ({np.sum(self.label["mask"])} < {minimum_area})'
            log_text += " --> removed" if remove_label else ""
            Logger.log_info_alt(log_text)
        if remove_label:
            is_small_label = False
        return is_small_label

    def _is_overlapping_label(self):
        # Check if a single pixel belongs to multiple instance masks

        mask = self.label["mask"]
        origin = self.label["bitmap"]["origin"]
        self.image_mask[
            origin[1] : origin[1] + mask.shape[0],
            origin[0] : origin[0] + mask.shape[1],
        ][mask == 1] += mask[mask == 1]
        is_overlapping_label = np.max(self.image_mask) > 1

        # Reset the check so that other labels do not trigger it again just because it has been triggered before
        self.image_mask[self.image_mask > 1] = 1

        self._update_issue_tag(self.label, "Overlapping label", is_overlapping_label)

        if self.verbose and is_overlapping_label:
            Logger.log_info_alt(f"{self.image_name} | segmentation | overlapping label")
        return is_overlapping_label

    def _is_outside_image_frame(self, image_border_size: int):
        # Check if the label reaches into the black border (watermark)

        mask = self.label["mask"].copy()
        origin = self.label["bitmap"]["origin"]
        min_x, max_x = origin[0], origin[0] + mask.shape[1]  # width
        min_y, max_y = origin[1], origin[1] + mask.shape[0]  # height

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
            # Remove annotated pixels outside the main image, i.e., inside the watermark
            mask[:, : image_border_size - min_x] = False
            mask[:, self.image_width - image_border_size - min_x :] = False
            mask[: image_border_size - min_y, :] = False
            mask[self.image_height - image_border_size - min_y :, :] = False
            self.label["bitmap"]["data"] = sly.geometry.bitmap.Bitmap.data_2_base64(
                mask
            )
            self._update_bitmap_data()
            # Remove issue tag if it previously existed
            self._delete_issue_tag(self.label, "Inside watermark")

        if self.verbose and is_outside_image_frame:
            log_text = f"{self.image_name} | segmentation | inside watermark"
            log_text += " --> fixed" if self.apply_auto_fixes else ""
            Logger.log_info_alt(log_text)
        if self.apply_auto_fixes:
            is_outside_image_frame = False
        return is_outside_image_frame

    def _is_ghost_bounding_box(self):
        # Sometimes the inferred bounding box is larger than the actual mask

        # We just convert the mask back to the encrypted version and check for differences
        data = sly.geometry.bitmap.Bitmap.data_2_base64(self.label["mask"])
        is_ghost_bounding_box = self.label["bitmap"]["data"] != data

        if not self.apply_auto_fixes:
            self._update_issue_tag(
                self.label, "Ghost bounding box", is_ghost_bounding_box
            )
        elif is_ghost_bounding_box:
            self.label["bitmap"]["data"] = data
            self._update_bitmap_data()
            # Remove issue tag if it previously existed
            self._delete_issue_tag(self.label, "Ghost bounding box")

        if self.verbose and is_ghost_bounding_box:
            log_text = f"{self.image_name} | segmentation | ghost bounding box"
            log_text += " --> fixed" if self.apply_auto_fixes else ""
            Logger.log_info_alt(log_text)
        if self.apply_auto_fixes:
            is_ghost_bounding_box = False
        return is_ghost_bounding_box

    def _is_distorted_box(self, minimum_ratio: float, maximum_ratio: float):
        # maximum_ratio: height to width
        # The reasons for a distorted box could be that the mask covers multiple labels or
        #  there are some pixels that have been accidentally labeled but are separated

        ratio = self.label["mask"].shape[0] / self.label["mask"].shape[1]
        greater_max_ratio = ratio > maximum_ratio
        smaller_min_ratio = ratio < minimum_ratio
        is_distorted_box = greater_max_ratio or smaller_min_ratio

        self._update_issue_tag(self.label, "Suspicious aspect ratio", is_distorted_box)

        if self.verbose and is_distorted_box:
            log_text = f"{self.image_name} | segmentation | aspect ratio ({np.round(ratio, 1)} "
            if greater_max_ratio:
                log_text += f"> {maximum_ratio})"
            elif smaller_min_ratio:
                log_text += f"< {minimum_ratio})"
            Logger.log_info_alt(log_text)
        return is_distorted_box

    def _is_perforated(self):
        # Check for holes in the segmentation mask

        # Fill holes, if there are any. This will only change true holes.
        updated_mask = ndimage.binary_fill_holes(self.label["mask"])
        is_perforated = np.any(updated_mask != self.label["mask"])

        if not self.apply_auto_fixes:
            self._update_issue_tag(self.label, "Perforated label", is_perforated)
        elif is_perforated:
            self.label["bitmap"]["data"] = sly.geometry.bitmap.Bitmap.data_2_base64(
                updated_mask
            )
            self._update_bitmap_data()
            # Remove issue tag if it previously existed
            self._delete_issue_tag(self.label, "Perforated label")

        self._update_issue_tag(self.label, "Perforated label", is_perforated)

        if self.verbose and is_perforated:
            log_text = f"{self.image_name} | segmentation | perforated label"
            log_text += " --> fixed" if self.apply_auto_fixes else ""
            Logger.log_info_alt(log_text)
        if self.apply_auto_fixes:
            is_perforated = False
        return is_perforated

    def _update_bitmap_data(self):
        updated_label = sly.Label.from_json(self.label, self.project_meta)
        self._update_label(updated_label)
        # Update label object for later checks
        self.label = updated_label.to_json()
        self.label["mask"] = sly.geometry.bitmap.Bitmap.base64_2_data(
            self.label["bitmap"]["data"]
        )
