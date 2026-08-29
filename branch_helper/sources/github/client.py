import requests

from branch_helper.config import require_config_section
from branch_helper.http_errors import handle_http_error


def get_github_issues(profile: dict, alias: str) -> list[dict]:
    github = require_config_section(profile, "github", alias)
    token = github.get("token")
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    query = "is:issue is:open assignee:@me"
    issues = []
    page = 1

    while True:
        try:
            response = requests.get(
                "https://api.github.com/search/issues",
                headers=headers,
                params={"q": query, "per_page": 100, "page": page},
                timeout=30,
            )
            response.raise_for_status()
        except requests.HTTPError as error:
            handle_http_error(error, "GitHub")

        payload = response.json()
        issues.extend(payload.get("items", []))

        if len(issues) >= payload.get("total_count", 0):
            break
        if not payload.get("items"):
            break

        page += 1

    return issues
