import click

from viewers.supervisely.click_sly_viewer import supervisely
from viewers.yolo.click_yolo_viewer import yolo


@click.group()
def viewers():
    """
    Label Viewers
    \b
    The commands in this group help you visualize your labels.
    If you're interested in extending the available viewers, have a look at:
    https://github.com/fsoco/fsoco-dataset/blob/master/CONTRIBUTING.md
    """
    pass


viewers.add_command(yolo)
viewers.add_command(supervisely)

if __name__ == "__main__":
    print(
        "[LOG] This sub-module contains label viewers and is not meant to be run as a stand-alone script"
    )
