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
