# branch-helper

CLI tool that lists your assigned issues from Jira or GitHub and prints suggested git branch names and commit messages.

Each project context is a named **alias** in config — source type and credentials combined. Use `--alias` to switch between them.

## Usage

```bash
branch-helper                          # interactive wizard (TTY): pick project, pick issue
branch-helper --alias project-x         # list all assigned issues for Jira project
branch-helper --alias elmosgot         # list all assigned issues for GitHub
branch-helper --list-aliases           # list aliases, mark default, show source
```

On an interactive terminal, `branch-helper` with no flags starts a wizard: select a project (alias), then select an issue, then see branch and commit suggestions for that item only. If you have only one project or one issue, that step is skipped automatically.

Use `--alias` when you want a non-interactive list of all assigned issues for a specific project.

### Jira output

For each issue it shows:

- **branch** — story branch name (parent issue key + lowercase slugified summary, e.g. `PROJ-123-add-pest-testing`)
- **task branch** — task branch name (parent + task key + lowercase slugified summary), for Subtaak/Taak issues
- **commit message** — formatted as `(KEY) summary`

### GitHub output

For each assigned open issue it shows:

- **branch** — `issues/{number}-{slugified-title}` (e.g. `issues/1-implement-support-for-github-issues`)
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

- `default` — alias used when `--alias` is omitted and no `.branch-helper-default` is found
- `aliases.<name>.source` — `jira` or `github`
- `aliases.<name>.jira` — Jira domain, username, token
- `aliases.<name>.github` — GitHub token

## Per-project default

Place a `.branch-helper-default` file in a repo root to override the global default for that project. The file contains a single alias name:

```
elmosgot
```

branch-helper walks up from the current directory until it finds this file (same idea as git finding `.git`). Commit it in your repo so the whole team gets the correct default.

**Priority:** `--alias` > `.branch-helper-default` > `config.yml` `default`

When a local default is set, the interactive wizard skips project selection and goes straight to issue selection.

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
./install.sh
```

Or manually:

```bash
sudo install -m755 bin/branch-helper /usr/local/bin/branch-helper
sudo cp -r branch_helper /usr/local/share/branch-helper/
```

## Updating

After pulling changes, reinstall:

```bash
./install.sh
```

The command expects `~/.config/branch-helper/config.yml`. If the file is missing, it prints the expected path and exits.

## Development

Run from the repo root without installing:

```bash
python3 -m branch_helper
python3 -m branch_helper --list-aliases
python3 -m branch_helper --alias elmosgot
```

Install [Ruff](https://docs.astral.sh/ruff/) and run locally:

```bash
pip install ruff
ruff check branch_helper bin
ruff format branch_helper bin
```

CI runs `ruff check` and `ruff format --check` on every push and pull request (see `.github/workflows/code-quality.yml`).

## Automated pull requests

When you push a branch named `issues/{number}-{slug}` (as suggested by `branch-helper --alias elmosgot`), a **draft PR** is opened automatically against `master`:

- **Title:** `(#N) {issue title}`
- **Body:** issue description plus `Closes #N`

Branches that do not match `issues/{number}-{slug}` are skipped. If a PR already exists for the branch, nothing is created.
