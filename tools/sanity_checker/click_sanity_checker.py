import click
from pathlib import Path
from typing import Tuple

from similarity_scorer.utils.logger import Logger
from .sanity_checker import SanityChecker


@click.command()
@click.option(
    "--team_name",
    "-t",
    type=str,
    required=True,
    help="Specify the Supervisely team name.",
)
@click.option(
    "--workspace_name",
    "-w",
    type=str,
    required=True,
    help="Specify the Supervisely workspace name.",
)
@click.option(
    "--project_name",
    "-p",
    type=str,
    multiple=True,
    help="Specify a Supervisely project name. You can use this option multiple times.",
)
@click.option(
    "--whitelist/--blacklist",
    "projects_whitelisted",
    default=True,
    help="Decide whether to white- or blacklist the specified Supervisely projects. Default is whitelisting.",
)
@click.option(
    "--token",
    "server_token",
    type=str,
    required=True,
    help="Secret token to access Supervisely.",
)
@click.option(
    "--label_type",
    "-l",
    type=click.Choice(["bitmap", "rectangle"], case_sensitive=False),
    default=("bitmap", "rectangle"),
    multiple=True,
    help="If specified, only labels of this type will be checked."
    + " You can use this option multiple times",
)
@click.option(
    "--results_path",
    type=click.Path(exists=False),
    default=None,
    help="Save the results as JSON in the specified folder."
    + " It will overwrite existing logs.",
)
@click.option(
    "--dry_run", is_flag=True, help="Do not update the labels on Supervisely."
)
@click.option("--verbose", is_flag=True, help="Print all discovered issues.")
def sanity_checker(
    team_name: str,
    workspace_name: str,
    project_name: Tuple[str, ...],
    projects_whitelisted: bool,
    server_token: str,
    label_type: Tuple[str, ...],
    results_path: str,
    dry_run: bool,
    verbose: bool,
):
    """
    The tools runs sanity checks on the labels on the Supervisely server.
    It supports both bounding boxes and instance segmentation.
    """
    server_address: str = "https://app.supervise.ly"

    checker = SanityChecker(
        server_address,
        server_token,
        team_name,
        workspace_name,
        project_name,
        label_type,
        projects_whitelisted,
        dry_run,
        verbose,
    )
    checker.run()
    Logger.log_info("Sanity checks finished with the following results.")
    print(checker)

    if results_path is not None:
        results_path = Path(results_path)
        results_filename = results_path / "sanity_checks.json"
        if not results_path.exists():
            results_path.mkdir(parents=True)
            Logger.log_info(f"Created results directory: {results_path.absolute()}")
        checker.save_results(results_filename)


if __name__ == "__main__":
    click.echo(
        "[LOG] This sub-module is not meant to be run as a stand-alone script. Please refer to\n $ fsoco --help"
    )
