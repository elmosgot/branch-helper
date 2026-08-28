import requests
from requests.auth import HTTPBasicAuth

from branch_helper.config import require_config_section
from branch_helper.http_errors import handle_http_error
from branch_helper.slugify import slugify


class Entity:
    def __init__(self, data: dict):
        self.data = data
        self.fields = {} if data["fields"] is None else data["fields"]

    def getId(self) -> str:
        return self.data.get("key")

    def getField(self, key, default=None) -> str | None:
        field = self.fields.get(key)

        return default if field is None else field

    def getName(self) -> str:
        return f"{self.getId()} {self.getField('summary')}"

    def getType(self) -> str:
        issue_type = self.getField("issuetype")
        return f"{issue_type['name']}"

    def message(self) -> str:
        return f"({self.getId()}) {self.getField('summary')}"


class JiraEntity(Entity):
    def __init__(self, data: dict):
        super().__init__(data)
        if self.hasParent():
            self.parent = JiraEntity(self.getField("parent"))

    def hasParent(self) -> bool:
        return self.getField("parent") is not None

    def getParent(self) -> Entity:
        return self.parent

    def getBranch(self) -> str:
        base = self
        if self.hasParent():
            base = self.parent

        title = base.getField("summary")

        return f"{base.getId()}-{slugify(title)}"

    def getTaskBranch(self) -> str:
        if not self.hasParent():
            return "no-parent"

        title = self.getField("summary")

        return f"{self.parent.getId()}-{self.getId()}-{slugify(title)}"


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


def fetch_jira_entities(profile: dict, alias: str) -> list[JiraEntity]:
    tasks = get_jira_tasks(profile, alias)
    return [JiraEntity(issue) for issue in tasks.get("issues", [])]
