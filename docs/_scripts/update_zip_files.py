#!/usr/bin/env python3

import sys
import os
import supervisely_lib as sly
from typing import List
from tqdm import tqdm
from zipfile import ZipFile
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
        with ZipFile(zipfile_name, "w") as zip_obj:
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

    file_drive.SetContentFile(zipfile_name)
    file_drive.Upload()

    assert file_drive["headRevisionId"] != prev_revision_id


def main(sly_token: str, download_path: str):
    sly_team = "fsoco private"
    sly_workspace = "FSOCO"
    sly_projects = {
        "Bounding_Boxes-train": {"zipfile": "fsoco_bounding_boxes_train.zip"},
        "Bounding_Boxes-test": {"zipfile": "fsoco_bounding_boxes_test.zip"},
        "Segmentation": {"zipfile": "fsoco_segmentation_train.zip"},
    }
    drive_folder_id = "185NGDyUdzmx5B3pqfxNMns6q1c9C0_76"

    for sly_project, sly_project_config in sly_projects.items():
        if sly_project != "Bounding_Boxes-test":
            continue
        os.makedirs(download_path)

        download_dataset(sly_token, sly_team, sly_workspace, sly_project, download_path)
        zip_dataset(download_path, sly_project_config["zipfile"])
        upload_zipfile(sly_project_config["zipfile"], drive_folder_id)

        os.remove(sly_project_config["zipfile"])
        shutil.rmtree(download_path)


if __name__ == "__main__":
    sly_token = os.getenv("SLY_TOKEN")
    if sly_token is None:
        print('ERROR: cannot find environment variable "SLY_TOKEN"')
        sys.exit(-1)

    download_path = os.path.join(os.getcwd(), "tmp")
    main(sly_token, download_path)
