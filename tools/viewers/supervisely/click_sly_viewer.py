import click

from .sly_viewer import main


@click.command()
@click.argument("input_folder", type=str)
@click.option("--sample_size", type=click.FloatRange(0.0, 1.0), default=1.0)
def supervisely(input_folder, sample_size):
    """
    Supervisely label viewer

    \b
    This viewer allows you to visualize labels in Supervisely's bounding box and segmentation formats.
    Specify --sample_size [0.0-1.0] to only show a smaller subset of all labels without changing their order.

    \b
    Input:
    input_folder
        ├── img
        │  ├── img_x.jpeg
        │  ├── img_y.jpeg
        │  └── img_z.jpeg
        └── ann
           ├── img_x.jpeg.json
           ├── img_y.jpeg.json
           └── img_z.jpeg.json

    """
    click.echo("[LOG] Running Supervisely label viewer")
    main(input_folder, sample_size)


if __name__ == "__main__":
    click.echo(
        "[LOG] This sub-module is not meant to be run as a stand-alone script. Please refer to\n $ fsoco --help"
    )
