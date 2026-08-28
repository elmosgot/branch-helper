# branch-helper

CLI tool that lists your assigned Jira issues and prints suggested git branch names and commit messages.

For each issue it shows:

- **branch** — story branch name (parent issue key + slugified summary)
- **task branch** — task branch name (parent + task key + slugified summary), for Subtaak/Taak issues
- **commit message** — formatted as `(KEY) summary`

Branch names are slugified to be git-safe (special characters removed, unicode normalized to ASCII).

## Dependencies

Debian 12:

```bash
sudo apt install python3-yaml python3-requests
```

Debian < 12:

```bash
sudo apt install python3-pip
pip install pyyaml requests
```

## Jira API token

Create a personal API token in Jira with these scopes:

- read:account
- read:project:jira
- read:me
- read:issue:jira
- read:field:jira
- read:filter:jira
- read:epic:jira-software
- read:project.feature:jira

## Configuration

The CLI reads `~/.config/branch-helper/config.yml`. Copy `example.yml` as a starting point:

```yaml
jira:
    domain: "your-org.atlassian.net"
    username: "you@example.com"
    token: "your-jira-api-token"
```

- `domain` — your Atlassian host (e.g. `your-org.atlassian.net`)
- `username` — the email tied to your Jira API token
- `token` — your Jira personal API token

## Setup

1. Create the config directory:

   ```bash
   mkdir -p ~/.config/branch-helper
   ```

2. Copy the example config and fill in your values:

   ```bash
   cp example.yml ~/.config/branch-helper/config.yml
   ```

3. Restrict permissions on the config file:

   ```bash
   chmod 600 ~/.config/branch-helper/config.yml
   ```

## Install

```bash
sudo install -m 755 branch-helper /usr/local/bin/branch-helper
```

## Usage

Run from any directory:

```bash
branch-helper
```

The command expects `~/.config/branch-helper/config.yml`. If the file is missing, it prints the expected path and exits.

## Updating

After making changes to the script, reinstall:

```bash
sudo install -m 755 branch-helper /usr/local/bin/branch-helper
```
