import os
import logging
import regex as re
import requests
from requests_html import HTMLSession

GAPPS_URL = "https://script.google.com/macros/s/AKfycbwe9WgdWy_nsfyk1zC13pGc-ZnoJ4iRGvvJyIXZ2h4buI5MWLTL/exec"


def get_teams():
    s = os.environ.get("SANITY_CHECKS_TEAMS")
    sly_team = re.match(r".*(?P<team>-t\s\S+)", s).group("team")
    sly_ws = re.match(r".*(?P<ws>-w\s\S+\s\S+)", s).group("ws")
    env_teams = [
        team.strip() for team in re.findall(r"(-p[\s\S+]+)\s", s)[0].split("-p ")
    ]
    blacklist = bool(re.match("--blacklist", s))
    header = {"x-api-key": os.environ.get("SLY_TOKEN")}
    r_teams = requests.get(
        "https://app.supervise.ly/public/api/v3/teams.list", header=header
    )
    team_id = next(
        team["id"] for team in r_teams.json()["entities"] if team["name"] == sly_team
    )
    r_ws = requests.get(
        "https://app.supervise.ly/public/api/v3/workspaces.list",
        params={"teamId": team_id},
        header=header,
    )
    ws_id = next(ws["id"] for ws in r_ws.json()["entities"] if ws["name"] == sly_ws)
    r_projects = requests.get(
        "https://app.supervise.ly/public/api/v3/projects.list",
        params={"workspaceId": ws_id},
        header=header,
    )
    if blacklist:
        teams = [
            team for team in r_projects.json()["entities"] if team not in env_teams
        ]
    else:
        teams = [team for team in r_projects.json()["entities"] if team in env_teams]
    logging.info(teams)
    return teams


def test_google_app_script_response():
    session = HTMLSession()
    teams = get_teams()
    responses = []
    for team in teams:
        logging.info(f"Getting page for {team}")
        r = session.get(GAPPS_URL, params={"team_name": team})
        r.html.render(sleep=4, timeout=15.0)
        responses.append(r.html.text)
    # render for some reason doesn't execute the GApp JS script correctly
    # The User HTML generated can be searched through regex though
    # "Success" => team_name found; "Fail" => team_name not found
    response_status = [
        True if response.find("Success") >= 0 else False for response in responses
    ]
    assert all(response_status), [
        team_name for team_name, res in zip(teams, response_status) if not res
    ]
