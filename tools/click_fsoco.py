#!/usr/bin/env python

import os

import click

from label_converters.label_converters import label_converters
from watermark.click_watermark import watermark
from similarity_scorer.click_similarity_scorer import similarity_scorer
from collect_stats.click_collect_stats import collect_stats
from viewers.viewers import viewers


class Tools(object):
    def __init__(self, home=None, debug=False):
        """
        Initialize tools class.
        """
        self.home = os.path.abspath(home or ".")
        self.debug = debug


@click.group()
@click.option("--tools-home", envvar="FSOCO_TOOLS_HOME", default=".")
@click.option("--debug/--no-debug", default=False, envvar="FSOCO_TOOLS_DEBUG")
@click.pass_context
def fsoco(ctx, tools_home, debug):
    """
    CLI tool-suite for the FSOCO dataset.

    Its purpose is to aid with data processing tasks revolving around the project.\n
    The current use-cases:

    \b
    - Dataset originality score: fsoco similarity-scorer [Options] Arguments
    - Dataset statistics: fsoco collect-stats [Options] Arguments
    - Label viewer: fsoco viewers [Options] Arguments
    - Label conversion: fsoco label-converters [Options] Arguments
    - Image watermarking: fsoco watermark [Options] Arguments

    If you're interested in extending the available tools or even adding new ones, have a look at:
    https://github.com/fsoco/fsoco/blob/master/tools/CONTRIBUTING.md
    """
    ctx.obj = Tools(tools_home, debug)


fsoco.add_command(label_converters)
fsoco.add_command(watermark)
fsoco.add_command(similarity_scorer)
fsoco.add_command(collect_stats)
fsoco.add_command(viewers)


if __name__ == "__main__":
    fsoco()
