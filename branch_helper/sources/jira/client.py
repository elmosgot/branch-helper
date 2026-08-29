import requests
from requests.auth import HTTPBasicAuth

from branch_helper.config import require_config_section
from branch_helper.http_errors import handle_http_error


def retrieve_jira(profile: dict, alias: str, endpoint: str, payload: dict) -> dict:
    jira = require_config_section(profile, "jira", alias)
    api_url = f"https://{jira.get('domain')}/rest/api/3/{endpoint}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    auth = HTTPBasicAuth(jira.get("username"), jira.get("token"))

    try:
        response = requests.post(
            api_url,
            headers=headers,
            auth=auth,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
    except requests.HTTPError as error:
        handle_http_error(error, "Jira")

    return response.json()


def get_jira_tasks(profile: dict, alias: str) -> dict:
    payload = {
        "jql": (
            "assignee = currentUser() "
            'AND issuetype IN("Bug", "Task", "Sub-task", "Feature", "Story") '
            'AND status IN ("In Progress", "Review", "Test")'
        ),
        "fields": ["key", "summary", "issuetype", "parent", "status"],
        "maxResults": 100,
    }

    return retrieve_jira(profile, alias, "search/jql", payload)
