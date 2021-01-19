import os
import logging
from requests_html import HTMLSession

GAPPS_URL = "https://script.google.com/macros/s/AKfycbwe9WgdWy_nsfyk1zC13pGc-ZnoJ4iRGvvJyIXZ2h4buI5MWLTL/exec"
IGNORE = ["Donations", "BME watermarked"]


def get_teams_from_env_var():
    teams = os.environ.get("SANITY_CHECKS_TEAMS", " -p fsoco").split(" -p ")[1:]
    teams = [team.replace('"', "") for team in teams]
    # Filter project names in old format
    teams = [team for team in teams if team not in IGNORE]
    logging.info(teams)
    return teams


def test_google_app_script_response():
    session = HTMLSession()
    teams = get_teams_from_env_var()
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
