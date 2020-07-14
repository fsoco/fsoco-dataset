import click

from .yolo2sly import main


@click.command()
@click.argument("images_folder", type=str)
@click.argument("darknet_labels_folder", type=str)
@click.argument("out_path", type=str)
@click.option(
    "--project_name",
    "-p",
    type=str,
    default="my_project",
    help="The dataset will be added to this project.",
)
@click.option(
    "--dataset_name",
    "-d",
    type=str,
    default="my_dataset",
    help="The images will be added to this dataset.",
)
def yolo2sly(
    images_folder, darknet_labels_folder, out_path, project_name, dataset_name
):
    """
    Darknet YOLO => Supervisely format

    https://docs.supervise.ly/ann_format/

    \b
    The mapping between Darknet class IDs and the class names we use in FSOCO can be adapted in this file:
    tools/label_converters/class_id_to_fsoco.yaml

    \b
    Input:
    ── images_folder
       ├── img_x.jpeg
       ├── img_y.jpeg
       └── img_z.jpeg
    ── darknet_labels_folder
       ├── img_x.txt
       ├── img_y.txt
       └── img_z.txt

    \b
    Output:
    project_name
    ├── meta.json
    └── dataset_name
        ├── ann
        │   ├── img_x.json
        │   ├── img_y.json
        │   └── img_z.json
        └── img
            ├── img_x.jpeg
            ├── img_y.jpeg
            └── img_z.jpeg

    Simply drag and drop the project_name folder in Supervisely to create a new project with the converted dataset contained in it.
    """
    click.echo("[LOG] Running Darknet Yolo to Supervisely label converter")
    main(images_folder, darknet_labels_folder, out_path, project_name, dataset_name)


if __name__ == "__main__":
    click.echo(
        "[LOG] This sub-module is not meant to be run as a stand-alone script. Please refer to\n $ fsoco --help"
    )
