import sys

import supervisely_lib as sly
from tqdm import tqdm

from similarity_scorer.utils.logger import Logger
from .bounding_box_checker import BoundingBoxChecker
from .segmentation_checker import SegmentationChecker
from .utils import safe_request


class SanityChecker:
    def __init__(
        self,
        server_address: str,
        server_token: str,
        team_name: str,
        workspace_name: str,
        project_name: str,
        dry_run: bool = False,
        verbose: bool = False,
    ):
        self.dry_run = dry_run
        self.verbose = verbose
        self.sly_api = None
        self.team = None
        self.workspace = None
        self.project = None
        self.project_meta = None
        self.datasets = []
        self.jobs = []
        self.job_statistics = {}

        if self.dry_run:
            Logger.log_warn("This is a DRYRUN, i.e., tags will not be uploaded.")
        if self.verbose:
            Logger.log_warn(
                "Verbose mode activated, i.e., all discovered issues will be printed."
            )

        self._initialize_supervisely(
            server_address, server_token, team_name, workspace_name, project_name
        )
        self._initialize_datasets()
        self._initialize_jobs()

    def __del__(self):
        if self.dry_run:
            Logger.log_warn("This was a DRYRUN, i.e., tags have not been uploaded.")

    def __str__(self):
        string = ""
        max_length_line = 0
        max_length_job_name = max([len(job_name) for job_name in self.job_statistics])
        for job_name, job_statistics in self.job_statistics.items():
            new_line = f'{job_name.ljust(max_length_job_name)} | number of issues = {job_statistics["numberIssues"]}\n'
            string += new_line
            max_length_line = max(max_length_line, len(new_line))
        max_length_line -= 1  # Subtract new line break \n
        string = "-" * max_length_line + "\n" + string + "-" * max_length_line
        return string

    def run(self):
        for dataset in self.datasets:
            self._run_dataset(dataset)

    def _initialize_supervisely(
        self,
        server_address: str,
        server_token: str,
        team_name: str,
        workspace_name: str,
        project_name: str,
    ):
        self.sly_api = sly.Api(server_address, server_token)

        self.team = safe_request(self.sly_api.team.get_info_by_name, team_name)
        if self.team is None:
            Logger.log_error(f"Team {team_name} not found.")
            sys.exit(-1)
        else:
            Logger.log_info(f"Team: id={self.team.id}, name={self.team.name}")

        self.workspace = safe_request(
            self.sly_api.workspace.get_info_by_name, self.team.id, workspace_name
        )
        if self.workspace is None:
            Logger.log_error(f"Workspace {workspace_name} not found.")
            sys.exit(-1)
        else:
            Logger.log_info(
                f"Workspace: id={self.workspace.id}, name={self.workspace.name}"
            )

        self.project = safe_request(
            self.sly_api.project.get_info_by_name, self.workspace.id, project_name
        )
        if self.project is None:
            Logger.log_error(f"Project {project_name} not found.")
            sys.exit(-1)
        else:
            Logger.log_info(f"Project: id={self.project.id}, name={self.project.name}")

        # This is used in several calls to the API, e.g., creating objects from JSON representation.
        project_meta_json = safe_request(self.sly_api.project.get_meta, self.project.id)
        self.project_meta = sly.ProjectMeta.from_json(project_meta_json)

    def _initialize_datasets(self):
        for dataset in safe_request(self.sly_api.dataset.get_list, self.project.id):
            Logger.log_info(f"Dataset: id={dataset.id}, name={dataset.name}")
            self.datasets.append(dataset)

    def _initialize_jobs(self):
        # We have to query the jobs twice since the Supervisely API does not provide the entities (assigned images) in
        #  the first API call "get_list()"
        # Fun fact: the functionality has only been added due to our feature request and broke their repo multiple times
        jobs = []
        for dataset in self.datasets:
            jobs += safe_request(
                self.sly_api.labeling_job.get_list, self.team.id, dataset_id=dataset.id
            )

        for job in jobs:
            Logger.log_info(f"Job: id={job.id}, name={job.name}")
            self.jobs.append(
                safe_request(self.sly_api.labeling_job.get_info_by_id, job.id)
            )  # Query assigned images

            # ToDo: Workaround because the API does not fill out the field 'classes_to_label'
            if "Bounding Boxes" in job.name:
                geometry_type = "rectangle"
            elif "Segmentation" in job.name:
                geometry_type = "bitmap"
            else:
                geometry_type = ""
                Logger.log_warn(
                    f"Cannot determine geometry type from job name: {job.name}"
                )

            # Use CamelCase to match the API's convention when creating JSON dictionaries
            self.job_statistics[job.name] = {
                "geometryType": geometry_type,
                "numberIssues": 0,
            }

    def _get_image_job_names(self, image_name: str, geometry_type: str) -> list:
        # The image could be in multiple jobs. Also, filter for the requested label type.
        job_names = []
        for job in self.jobs:
            for job_image in job.entities:
                if (
                    job_image["name"] == image_name
                    and self.job_statistics[job.name]["geometryType"] == geometry_type
                ):
                    job_names.append(job.name)
        return job_names

    def _run_dataset(self, dataset):
        # These are all images in the dataset
        images = safe_request(self.sly_api.image.get_list, dataset.id)

        with tqdm(
            total=len(images), desc=f"Processing dataset: {dataset.name}"
        ) as pbar:
            # Batch images to reduce the number of API calls
            for batch in sly.batched(images, batch_size=10):
                image_ids = [image.id for image in batch]
                annotations = safe_request(
                    self.sly_api.annotation.download_batch, dataset.id, image_ids
                )
                updated_annotations = {"image_ids": [], "annotations": []}

                # Iterate over images in batch
                for image in annotations:
                    # We use this object to update the labels. All checkers share the same instance.
                    updated_annotation = sly.Annotation.from_json(
                        image.annotation, self.project_meta
                    )
                    bounding_box_checker = BoundingBoxChecker(
                        image.image_name, updated_annotation, self.verbose
                    )
                    segmentation_checker = SegmentationChecker(
                        image.annotation["size"]["height"],
                        image.annotation["size"]["width"],
                        image.image_name,
                        updated_annotation,
                        self.verbose,
                    )
                    bounding_box_job_names = self._get_image_job_names(
                        image.image_name, "rectangle"
                    )
                    segmentation_job_names = self._get_image_job_names(
                        image.image_name, "bitmap"
                    )

                    update_image = False
                    # Iterate over labels in current image
                    for label in image.annotation["objects"]:
                        # We do not convert to a SLY object since it is easier to operate with the JSON dictionary
                        if label["geometryType"] == "rectangle":
                            if not bounding_box_checker.run(label):
                                update_image = True
                                for job_name in bounding_box_job_names:
                                    self.job_statistics[job_name]["numberIssues"] += 1
                        elif label["geometryType"] == "bitmap":
                            if not segmentation_checker.run(label):
                                update_image = True
                                for job_name in segmentation_job_names:
                                    self.job_statistics[job_name]["numberIssues"] += 1
                        else:
                            Logger.log_warn(
                                f"Found unsupported geometry type: {label['geometryType']}"
                            )

                    if update_image:
                        assert id(bounding_box_checker.updated_annotation) == id(
                            segmentation_checker.updated_annotation
                        )
                        updated_annotations["image_ids"].append(image.image_id)
                        updated_annotations["annotations"].append(
                            bounding_box_checker.updated_annotation
                        )
                    pbar.update(1)

                # Upload all annotations in the current batch if there are any
                if updated_annotations["image_ids"] and not self.dry_run:
                    safe_request(
                        self.sly_api.annotation.upload_anns,
                        updated_annotations["image_ids"],
                        updated_annotations["annotations"],
                    )
