from similarity_scorer.utils.logger import Logger
from tqdm import tqdm
import json
from pathlib import Path
import pandas as pd
import sys

from similarity_scorer.similarity_scorer import SimilarityScorer

try:
    import supervisely_lib as sly
except ImportError:
    Logger.log_error(
        "Please install the Supervisly SDK from https://github.com/supervisely/supervisely "
        "or use the [sly] option for pip install on fsoco tools.\n"
        "pip install --editable .[sly] "
    )
    sys.exit(-1)


def get_stat_template():
    stat = {}
    # general
    stat["team_name"] = ""
    stat["ann_file"] = ""
    stat["image_file"] = ""
    # image
    stat["image_width"] = -1
    stat["image_height"] = -1
    # label
    stat["num_boxes"] = 0
    stat["bounding_boxes"] = []

    return stat


class StatsCollector:
    def __init__(self, calc_similarity: bool, num_workers: int, use_gpu: bool):
        """
        Initialize the stats collector.
        """
        self.calc_similarity = calc_similarity
        self.num_workers = num_workers
        self.use_gpu = use_gpu

        self.project = None
        self._current_dataset = None

    def load_sly_project(self, sly_project_name: str):
        try:
            self.project = sly.Project(sly_project_name, sly.OpenMode.READ)
            return True
        except FileNotFoundError:
            Logger.log_error(f"Not able to load supervisly project {sly_project_name}!")
            return False

    def _collect_annotation_stats(self, ann_paths: list):
        stats = []

        for ann_path in tqdm(ann_paths):
            stats.append(self._extract_stats_from_annotation_file(ann_path))

        return stats

    def _extract_stats_from_annotation_file(self, ann_path: str):
        stats = get_stat_template()

        with open(ann_path) as json_file:
            data = json.load(json_file)

        ann = sly.Annotation.from_json(data, self.project.meta)

        stats["team_name"] = self._current_dataset.name
        stats["ann_file"] = ann_path

        image_file = Path(ann_path.replace("/ann/", "/img/").replace(".json", ""))
        if image_file.exists():
            stats["image_file"] = str(image_file)
        else:
            # no image file or more filenames with different suffixes are already handled by sly sdk
            stats["image_file"] = str(
                next(image_file.parent.glob(f"{image_file.stem}.*"))
            )

        stats["image_width"] = ann.img_size[1]
        stats["image_height"] = ann.img_size[0]

        bboxes = []

        for label in ann.labels:
            if isinstance(label.geometry, sly.geometry.rectangle.Rectangle):
                class_name = label.obj_class.name
                cleaned_tags = list(map(lambda tag_dict: tag_dict["name"], label.tags.to_json())) # remove user metadata information
                tags = cleaned_tags

                x = int(label.geometry.left + label.geometry.width / 2)
                y = int(label.geometry.top + label.geometry.height / 2)

                w = label.geometry.width
                h = label.geometry.height
                aspect_ratio = float(w) / float(h)
                bboxes.append(
                    {
                        "class_name": class_name,
                        "tags": tags,
                        "x": x,
                        "y": y,
                        "width": w,
                        "height": h,
                        "aspect_ratio": aspect_ratio,
                    }
                )

        stats["num_boxes"] = len(bboxes)
        stats["bounding_boxes"] = bboxes

        return stats

    def _handle_dataset(self, dataset: sly.project.project.Dataset):
        self._current_dataset = dataset
        names, img_paths, ann_paths = [], [], []
        for item_name in dataset:
            img_path, ann_path = dataset.get_item_paths(item_name)
            names.append(item_name)
            img_paths.append(img_path)
            ann_paths.append(ann_path)

        annotation_stats = self._collect_annotation_stats(ann_paths)

        self._current_dataset = None

        return annotation_stats

    def _collect_similarity_data(self):
        Logger.log_info("start collecting similarity data.")
        img_glob = f"{self.project.directory}/*/img/*"
        similarity_scorer = SimilarityScorer(
            image_glob=img_glob, gpu=self.use_gpu, num_workers=self.num_workers
        )

        similarity_scorer.per_folder_prefix = "team_"

        similarity_stats = similarity_scorer.collect_stats()

        return similarity_stats

    @staticmethod
    def _extract_box_stats(annotation_stats: list):
        box_rows = []
        for image_row in annotation_stats:
            for box_idx, bbox in enumerate(image_row["bounding_boxes"]):
                class_name, tags, x, y, w, h, aspect_ratio = bbox.values()

                box_rows.append(
                    (
                        image_row["team_name"],
                        image_row["ann_file"],
                        image_row["image_file"],
                        image_row["image_width"],
                        image_row["image_height"],
                        box_idx,
                        class_name,
                        tags,
                        x,
                        y,
                        w,
                        h,
                        aspect_ratio,
                    )
                )

        box_df = pd.DataFrame(
            box_rows,
            columns=[
                "team_name",
                "ann_file",
                "image_file",
                "image_width",
                "image_height",
                "box_id",
                "class",
                "tags",
                "mid-x",
                "mid-y",
                "width",
                "height",
                "bbox_aspect_ratio",
            ],
        )

        Logger.log_info(f"Extracted {len(box_rows)} bounding boxes.")
        return box_df

    @staticmethod
    def _merge_stats(annotation_stats: list, similarity_stats: pd.DataFrame):
        image_df = pd.DataFrame(annotation_stats)
        image_df.drop(columns=["bounding_boxes"], inplace=True)

        if similarity_stats is None:
            return image_df
        else:
            similarity_stats["image_file"] = (
                similarity_stats["folder"] + "/" + similarity_stats["file_name"]
            )
            similarity_stats.drop(columns=["folder", "file_name"], inplace=True)

            merged = pd.merge(
                image_df,
                similarity_stats,
                how="inner",
                on=["image_file"],
                validate="one_to_one",
            )

            return merged

    def collect_stats(self):
        annotation_stats = []
        similarity_stats = None
        for dataset in self.project:
            Logger.log_info(f"Extract stats for dataset '{dataset.name}'.")
            annotation_stats.extend(self._handle_dataset(dataset))

        if self.calc_similarity:
            similarity_stats = self._collect_similarity_data()

        box_df = self._extract_box_stats(annotation_stats)
        image_df = self._merge_stats(annotation_stats, similarity_stats)

        return image_df, box_df
