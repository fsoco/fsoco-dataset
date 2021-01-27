from abc import ABC, abstractmethod


class Checker(ABC):
    # All implemented checkers share the same object as a single image could contain multiple issues
    updated_annotation = None
    is_annotation_updated = None

    def __init__(
        self,
        image_name: str,
        updated_annotation,
        apply_auto_fixes: bool,
        verbose: bool = False,
    ):
        super().__init__()
        self.image_name = image_name
        self.apply_auto_fixes = apply_auto_fixes
        self.verbose = verbose
        Checker.updated_annotation = updated_annotation
        Checker.is_annotation_updated = False

    @abstractmethod
    def run(self, *args, **kwargs) -> bool:
        raise NotImplementedError
