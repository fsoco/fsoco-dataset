import os
import shlex
import logging
import requests
from requests_html import HTMLSession
from typing import List

GAPPS_URL = "https://script.google.com/macros/s/AKfycbzxi0VKZJPCpySqvnxiGLsfBYOiHuxKo2Wtg4dONoxI_Huw-YkjqJVmBGCfGS7CfhPJ/exec"
SKIP_DESC_FLAG = "skip_status_page_test"

def get_teams() -> List[str]:
    s = os.environ.get("SANITY_CHECKS_TEAMS")
    args = shlex.split(s)
    sly_team = args[_list_index(args, ["--team_name", "-t"]) + 1]
    sly_ws = args[_list_index(args, ["--workspace_name", "-w"]) + 1]
    env_teams = [
        args[idx + 1] for idx, arg in enumerate(args) if arg in ["--project_name", "-p"]
    ]
    blacklist = "--blacklist" in args
    headers = {"x-api-key": os.environ.get("SLY_TOKEN")}
    r_teams = requests.get(
        "https://app.supervise.ly/public/api/v3/teams.list", headers=headers
    )
    team_id = next(
        team["id"] for team in r_teams.json()["entities"] if team["name"] == sly_team
    )
    r_ws = requests.get(
        "https://app.supervise.ly/public/api/v3/workspaces.list",
        params={"teamId": team_id},
        headers=headers,
    )
    ws_id = next(ws["id"] for ws in r_ws.json()["entities"] if ws["name"] == sly_ws)
    r_projects = requests.get(
        "https://app.supervise.ly/public/api/v3/projects.list",
        params={"workspaceId": ws_id},
        headers=headers,
    )
    if blacklist:
        teams = [
            project["name"]
            for project in r_projects.json()["entities"]
            if project["name"] not in env_teams
            and SKIP_DESC_FLAG not in project["description"]
        ]
    else:
        teams = [
            project["name"]
            for project in r_projects.json()["entities"]
            if project["name"] in env_teams
            and SKIP_DESC_FLAG not in project["description"]
        ]
    logging.info(teams)
    return teams


def test_google_app_script_response():
    session = HTMLSession()
    teams = get_teams()
    response_status = []
    for team in teams:
        logging.info(f"Getting page for {team}")
        r = session.get(GAPPS_URL, params={"team_name": team, "what": "get_job_status"})
        status = True if r.text.find(team) >= 0 else False
        response_status.append(status)
    assert all(response_status), [
        team_name for team_name, res in zip(teams, response_status) if not res
    ]


def _list_index(list_: list, elements: List[str]) -> int:
    """
    This function is an extension to the string method index() returning the
    first occurence of any of the given elements.

    Example:
    list_ = ['-t', 'team_A', '-w', 'workspace_A', '--team', 'team_B']
    ret = _list_index(list_, ['--team', '-t'])
    # ret = 0
    """
    for i, s in enumerate(list_):
        if s in elements:
            return i
    raise ValueError("None of the elements is in the list.")
