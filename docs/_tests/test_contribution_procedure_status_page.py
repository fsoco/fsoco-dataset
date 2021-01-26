import os
import logging
import regex as re
import requests
from requests_html import HTMLSession

GAPPS_URL = "https://script.google.com/macros/s/AKfycbwe9WgdWy_nsfyk1zC13pGc-ZnoJ4iRGvvJyIXZ2h4buI5MWLTL/exec"


def get_teams():
    s = os.environ.get("SANITY_CHECKS_TEAMS")
    sly_team = re.match(r".*-t\s(?P<team>\S+)", s).group("team")
    sly_ws = re.match(r".*-w\s(?P<ws>\S+\s\S+)", s).group("ws")
    env_teams = [
        match.group("team") for match in re.finditer(r"\s*-p\s(?<team>\".*?\"|\S+)", s)
    ]
    blacklist = bool(re.match(r".*--blacklist", s))
    headers = {"x-api-key": os.environ.get("SLY_TOKEN")}
    r_teams = requests.get(
        "https://app.supervise.ly/public/api/v3/teams.list", headers=headers
    )
    try:
        team_id = next(
            team["id"]
            for team in r_teams.json()["entities"]
            if team["name"] == sly_team
        )
    except StopIteration:
        print(sly_team, [team["name"] for team in r_teams.json()["entities"]])
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
            if project not in env_teams
        ]
    else:
        teams = [
            project["name"]
            for project in r_projects.json()["entities"]
            if project in env_teams
        ]
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
