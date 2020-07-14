import click
from watermark.watermark import main


@click.command()
@click.argument("input_directory", required=True)
@click.argument("image_format", required=True)
@click.argument("logo_file", required=True)
def watermark(input_directory, image_format, logo_file):
    """
        Small script for dry-running watermarking.

        Based on the FSOCO Image Import plugin for supervisely.
    """
    click.echo("[LOG] Running Watermark script")
    main(input_directory, image_format=image_format, logo_file_name=logo_file)


if __name__ == "__main__":
    click.echo(
        "[LOG] This sub-module is not meant to be run as a stand-alone script. Please refer to\n $ fsoco --help"
    )
