from typing import List

from similarity_scorer.utils.logger import Logger
from .checker import Checker


class ImageChecker(Checker):
    ILLEGAL_TAGS = [
        "truncated",
        "knocked_over",
        "sticker_band_removed",
    ]

    def __init__(
        self,
        image_name: str,
        updated_annotation,
        apply_auto_fixes: bool,
        verbose: bool = False,
    ):
        super().__init__(image_name, updated_annotation, apply_auto_fixes, verbose)

    def run(self) -> bool:  # pylint: disable=arguments-differ
        is_ok = True
        is_ok &= self._is_wrongly_tagged(ImageChecker.ILLEGAL_TAGS)
        return is_ok

    def _is_wrongly_tagged(self, illegal_tags: List[str]) -> bool:
        is_wrongly_tagged = False

        wrong_tags: List[str] = []
        for tag in Checker.updated_annotation.img_tags:
            if tag.name in illegal_tags:
                is_wrongly_tagged = True
                wrong_tags.append(tag.name)
        wrong_tags = sorted(wrong_tags)

        if self.verbose and is_wrongly_tagged:
            log_text = (
                f"{self.image_name} | image | illegal tag ({', '.join(wrong_tags)})"
            )
            log_text += " --> fixed" if self.apply_auto_fixes else ""
            Logger.log_info_alt(log_text)
        if self.apply_auto_fixes and is_wrongly_tagged:
            Checker.updated_annotation = Checker.updated_annotation.delete_tags_by_name(
                wrong_tags
            )
            Checker.is_annotation_updated = True
            is_wrongly_tagged = False
        return is_wrongly_tagged
