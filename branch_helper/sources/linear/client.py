import sys

import requests

from branch_helper.config import require_config_section
from branch_helper.http_errors import handle_http_error

LINEAR_API_URL = "https://api.linear.app/graphql"

ASSIGNED_ISSUES_QUERY = """
query AssignedIssues($cursor: String) {
  viewer {
    assignedIssues(
      filter: { state: { type: { nin: ["completed", "canceled"] } } }
      first: 100
      after: $cursor
    ) {
      nodes {
        identifier
        title
        parent {
          identifier
          title
        }
      }
      pageInfo {
        hasNextPage
        endCursor
      }
    }
  }
}
"""


def query_linear(
    profile: dict,
    alias: str,
    query: str,
    variables: dict | None = None,
) -> dict:
    linear = require_config_section(profile, "linear", alias)
    token = linear.get("token")
    headers = {
        "Content-Type": "application/json",
        "Authorization": token,
    }

    try:
        response = requests.post(
            LINEAR_API_URL,
            headers=headers,
            json={"query": query, "variables": variables or {}},
            timeout=30,
        )
        response.raise_for_status()
    except requests.HTTPError as error:
        handle_http_error(error, "Linear")

    payload = response.json()
    if payload.get("errors"):
        message = payload["errors"][0].get("message", "Unknown Linear API error")
        print(f"Linear API error: {message}", file=sys.stderr)
        sys.exit(1)

    return payload.get("data", {})


def get_linear_issues(profile: dict, alias: str) -> list[dict]:
    issues = []
    cursor = None

    while True:
        data = query_linear(
            profile,
            alias,
            ASSIGNED_ISSUES_QUERY,
            {"cursor": cursor},
        )
        assigned = data.get("viewer", {}).get("assignedIssues", {})
        issues.extend(assigned.get("nodes", []))

        page_info = assigned.get("pageInfo", {})
        if not page_info.get("hasNextPage"):
            break

        cursor = page_info.get("endCursor")
        if not cursor:
            break

    return issues
