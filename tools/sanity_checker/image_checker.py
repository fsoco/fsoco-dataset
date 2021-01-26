from abc import ABC
from typing import Optional, List, Dict, Any

from similarity_scorer.utils.logger import Logger


class ImageChecker(ABC):
    updated_annotation = None
    is_annotation_updated = None

    ILLEGAL_TAGS = [
        "truncated",
        "knocked_over",
        "sticker_band_removed",
    ]

    def __init__(
        self,
        image_name: str,
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
        ImageChecker.updated_annotation = updated_annotation
        ImageChecker.is_annotation_updated = False

        # The checks run on this object
        self.tags: Optional[List[Dict[str, Any]]] = None

    def run(self, tags: List[Dict[str, Any]]):
        # Run all checks on the same object.
        self.tags = tags

        is_ok = True
        is_ok &= self._is_wrongly_tagged(ImageChecker.ILLEGAL_TAGS)
        return is_ok

    def _is_wrongly_tagged(self, illegal_tags: List[str]) -> bool:
        is_wrongly_tagged = False

        updated_tags: List[dict] = []
        wrong_tags: List[str] = []
        for tag in self.tags:
            if tag["name"] in illegal_tags:
                is_wrongly_tagged = True
                wrong_tags.append(tag["name"])
            else:
                updated_tags.append(tag)
        wrong_tags = sorted(wrong_tags)

        if self.verbose and is_wrongly_tagged:
            log_text = (
                f"{self.image_name} | image | illegal tag ({', '.join(wrong_tags)})"
            )
            log_text += " --> fixed" if self.apply_auto_fixes else ""
            Logger.log_info_alt(log_text)
        if self.apply_auto_fixes:
            self.tags = updated_tags
            is_wrongly_tagged = False
        return is_wrongly_tagged
