#!/usr/bin/env python3

import sys
import os
import supervisely_lib as sly
from typing import List
from tqdm import tqdm
import zipfile
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import shutil


def download_dataset(
    sly_token: str,
    sly_team: str,
    sly_workspace: str,
    sly_project: str,
    download_path: str,
):
    SLY_ADDRESS = "https://app.supervise.ly"

    # Initialize API
    sly_api = sly.Api(SLY_ADDRESS, sly_token)

    # Get IDs of team, workspace and project by names
    team = sly_api.team.get_info_by_name(sly_team)
    if team is None:
        raise RuntimeError(f"Team {sly_team} not found.")

    workspace = sly_api.workspace.get_info_by_name(team.id, sly_workspace)
    if workspace is None:
        raise RuntimeError(f"Workspace {sly_workspace} not found.")

    project = sly_api.project.get_info_by_name(workspace.id, sly_project)
    if project is None:
        raise RuntimeError(f"Project {sly_project} not found.")

    print(f"Team: id={team.id}, name={team.name}")
    print(f"Workspace: id={workspace.id}, name={workspace.name}")
    print(f"Project: id={project.id}, name={project.name}")

    sly.download_project(sly_api, project.id, download_path, log_progress=True)


def zip_dataset(project_dir: str, zipfile_name: str, dataset_blacklist: List[str] = []):
    assert os.path.exists(project_dir)

    number_files = sum([len(files) for r, d, files in os.walk(download_path)])
    with tqdm(total=number_files, desc="Zipping dataset", unit="files") as pbar:
        with zipfile.ZipFile(zipfile_name, "w", zipfile.ZIP_DEFLATED) as zip_obj:
            for foldername, subfolders, filenames in os.walk(project_dir):
                for filename in filenames:
                    file_path = os.path.join(foldername, filename)
                    zip_file_path = file_path.replace(project_dir, "")
                    dataset = zip_file_path.split("/")[1]
                    if dataset not in dataset_blacklist:
                        zip_obj.write(file_path, zip_file_path)
                    pbar.set_postfix(dataset=dataset)
                    pbar.update(1)


def upload_zipfile(zipfile_name: str, drive_folder_id: str):
    assert os.path.exists(zipfile_name)

    gauth = GoogleAuth()
    if os.path.exists("credentials.txt"):
        gauth.LoadCredentialsFile("credentials.txt")
    else:
        gauth.LocalWebserverAuth()
        gauth.SaveCredentialsFile("credentials.txt")
    drive = GoogleDrive(gauth)

    file_drive = drive.ListFile(
        {
            "q": f'"{drive_folder_id}" in parents and title contains "{zipfile_name}" and trashed=false'
        }
    ).GetList()
    assert len(file_drive) <= 1

    if not file_drive:
        file_drive = drive.CreateFile(
            {"title": zipfile_name, "parents": [{"id": drive_folder_id}]}
        )
    else:
        file_drive = file_drive[0]
    prev_revision_id = file_drive.get("headRevisionId", "")

    print(f"Uploading zip file: {zipfile_name}")
    file_drive.SetContentFile(zipfile_name)
    file_drive.Upload()

    assert file_drive["headRevisionId"] != prev_revision_id


def main(sly_token: str, download_path: str):
    sly_team = "fsoco private"
    sly_workspace = "FSOCO"
    projects = {
        "bboxes_train": {
            "sly_project": "Bounding_Boxes-train",
            "zipfile": "fsoco_bounding_boxes_train.zip",
        },
        "bboxes_test": {
            "sly_project": "Bounding_Boxes-test",
            "zipfile": "fsoco_bounding_boxes_test.zip",
        },
        "segmentation_train": {
            "sly_project": "Segmentation",
            "zipfile": "fsoco_segmentation_train.zip",
        },
        "segmentation_early_adopters": {
            "sly_project": "Segmentation",
            "zipfile": "fsoco_segmentation_early_adopters.zip",
            "dataset_blacklist": ["tuwr", "fsb", "orion"],
        },
    }
    drive_folder_id = "1P0TiljS1RCaqdbKGFqju2W4_Drxd-_GI"

    for project_config in projects.values():
        os.makedirs(download_path)

        download_dataset(
            sly_token,
            sly_team,
            sly_workspace,
            project_config["sly_project"],
            download_path,
        )
        dataset_blacklist = project_config.get("dataset_blacklist", [])
        zip_dataset(download_path, project_config["zipfile"], dataset_blacklist)
        upload_zipfile(project_config["zipfile"], drive_folder_id)

        os.remove(project_config["zipfile"])
        shutil.rmtree(download_path)

        print("-" * 40)


if __name__ == "__main__":
    sly_token = os.getenv("SLY_TOKEN")
    if sly_token is None:
        print('ERROR: cannot find environment variable "SLY_TOKEN"')
        sys.exit(-1)

    download_path = os.path.join(os.getcwd(), "tmp")
    main(sly_token, download_path)
