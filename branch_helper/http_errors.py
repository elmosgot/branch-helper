import sys

import requests


def handle_http_error(error: requests.HTTPError, source: str) -> None:
    response = error.response
    if response is not None and response.status_code in (401, 403):
        print(
            f"{source} authentication failed ({response.status_code}). "
            "Check your token and scopes in config.yml.",
            file=sys.stderr,
        )
        sys.exit(1)

    raise error
