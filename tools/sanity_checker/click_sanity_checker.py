import click

from .sanity_checker import SanityChecker
from similarity_scorer.utils.logger import Logger


@click.command()
@click.argument("team_name", type=str)
@click.argument("workspace_name", type=str)
@click.argument("project_name", type=str)
@click.option(
    "--token", "server_token", type=str, help="Secret token to access Supervisely."
)
def sanity_checker(
    team_name: str, workspace_name: str, project_name: str, server_token: str
):
    server_address: str = "https://app.supervise.ly"

    checker = SanityChecker(
        server_address, server_token, team_name, workspace_name, project_name
    )
    checker.run()
    Logger.log_info("Sanity checks finished with the following results.")
    print(checker)


if __name__ == "__main__":
    click.echo(
        "[LOG] This sub-module is not meant to be run as a stand-alone script. Please refer to\n $ fsoco --help"
    )