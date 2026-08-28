# branch-helper

CLI tool that lists your assigned issues from Jira or GitHub and prints suggested git branch names and commit messages.

Each project context is a named **alias** in config — source type and credentials combined. Use `--alias` to switch between them.

## Usage

```bash
branch-helper                          # uses default alias
branch-helper --alias project-x         # Jira project
branch-helper --alias elmosgot         # GitHub for elmosgot repos
branch-helper --list-aliases           # list aliases, mark default, show source
```

### Jira output

For each issue it shows:

- **branch** — story branch name (parent issue key + lowercase slugified summary, e.g. `PROJ-123-add-pest-testing`)
- **task branch** — task branch name (parent + task key + lowercase slugified summary), for Subtaak/Taak issues
- **commit message** — formatted as `(KEY) summary`

### GitHub output

For each assigned open issue it shows:

- **branch** — `{number}-{slugified-title}` (e.g. `1-implement-support-for-github-issues`)
- **commit message** — `(#{number}) {title}` (e.g. `(#1) Implement support for GitHub Issues`)

Branch names are slugified to be git-safe (special characters removed, unicode normalized to ASCII, title segment lowercased).

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

## GitHub personal access token

Create a personal access token with:

- **Classic token:** `repo` scope
- **Fine-grained token:** Issues read access on the repos you use

## Configuration

The CLI reads `~/.config/branch-helper/config.yml`. Copy `example.yml` as a starting point:

```yaml
default: project-x

aliases:
  project-x:
    source: jira
    jira:
      domain: "your-org.atlassian.net"
      username: "you@example.com"
      token: "your-jira-api-token"

  elmosgot:
    source: github
    github:
      token: "ghp_your-github-personal-access-token"
```

- `default` — alias used when `--alias` is omitted
- `aliases.<name>.source` — `jira` or `github`
- `aliases.<name>.jira` — Jira domain, username, token
- `aliases.<name>.github` — GitHub token

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

## Updating

After making changes to the script, reinstall:

```bash
sudo install -m 755 branch-helper /usr/local/bin/branch-helper
```

The command expects `~/.config/branch-helper/config.yml`. If the file is missing, it prints the expected path and exits.
