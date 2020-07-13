import click

from .labelbox2sly import main


@click.command()
@click.argument("images_folder", type=str)
@click.argument("lb_labels_file", type=str)
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
def labelbox2sly(images_folder, lb_labels_file, out_path, project_name, dataset_name):
    """
    Labelbox => Supervisely format

    https://docs.supervise.ly/ann_format/

    \b
    Mappings between naming styles can be adapted in this file:
    tools/label_converters/names_to_fsoco.yaml

    \b
    Input:
    ── images_folder
       ├── img_x.jpeg
       ├── img_y.jpeg
       └── img_z.jpeg
    ── lb_labels_file

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
    click.echo("[LOG] Running Labelbox to Supervisely label converter")
    main(images_folder, lb_labels_file, out_path, project_name, dataset_name)


if __name__ == "__main__":
    click.echo(
        "[LOG] This sub-module is not meant to be run as a stand-alone script. Please refer to\n $ fsoco --help"
    )
