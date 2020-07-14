import click

from label_converters.labelbox2sly.click_labelbox2sly import labelbox2sly
from label_converters.yolo2sly.click_yolo2sly import yolo2sly


@click.group()
def label_converters():
    """
    Label Converters

    The commands in this group help you convert your labels into other formats.
    Please refer to the documentation page for a more thorough overview on what converters are available.
    If you're interested in extending the available converters, have a look at:
    https://github.com/fsoco/fsoco/blob/master/tools/CONTRIBUTING.md
    """
    pass


label_converters.add_command(yolo2sly)
label_converters.add_command(labelbox2sly, name="lb2sly")

if __name__ == "__main__":
    print(
        "[LOG] This sub-module contains Label Converters and is not meant to be run as a stand-alone script"
    )
