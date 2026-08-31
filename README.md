# branch-helper

CLI tool that lists your assigned issues from Jira, GitHub, or Linear and prints suggested git branch names and commit messages.

Each project context is a named **alias** in config — source type and credentials combined. Use `--alias` to switch between them.

## Usage

```bash
branch-helper                          # interactive wizard: pick project, pick issue, create/verify branch
branch-helper --commit                 # interactive wizard: stage and commit on the issue branch
branch-helper --update                 # interactive wizard: fetch and upmerge parent branch
branch-helper --alias project-x         # list all assigned issues for Jira project
branch-helper --alias elmosgot --commit # commit mode for a specific project alias
branch-helper --list-aliases           # list aliases, mark default, show source
```

On an interactive terminal, `branch-helper` with no flags starts a wizard: select a project (alias), then select an issue, then create or verify the suggested git branch. Use separate commands for committing and updating:

| Command | What it does |
|---|---|
| `branch-helper` | Create or checkout the issue branch (verify if already on it). Does not stage or commit. |
| `branch-helper --commit` | Stage and commit on the issue branch. You must already be on that branch (run plain `branch-helper` first). |
| `branch-helper --update` | Fetch from origin, merge `origin/<current-branch>`, then upmerge the parent branch. Matches the current branch to an in-progress issue when possible; otherwise upmerges `base_branch`. |

`--commit` and `--update` cannot be combined. Both require an interactive terminal.

Branch creation rules (default mode):

- **Story / GitHub issues** — created from the alias’s `base_branch` (or `.branch-helper-default`)
- **Jira / Linear tasks** — created from the story branch; the story branch is ensured first (from `base_branch` if missing)
- **New branches** — created with `--no-track`, then pushed with `git push -u origin <branch>` so upstream is `origin/<branch>`, not master
- **Dirty working tree** — prompts to stash before switching; restores stash after checkout

**Commit mode** (`--commit`): after selecting an issue, opens the staging screen (↑/↓ navigate, Space stage/unstage, Enter commit, q cancel). Enter prompts for an optional extra message, then creates a commit with the issue subject plus any body you add.

**Update mode** (`--update`): when the working tree is dirty, prompts to stash before updating (restored after). Matches the current git branch to an assigned in-progress issue when possible and uses that issue’s parent for the upmerge; otherwise updates the current branch from `base_branch` (even when no issues are listed). No issue picker. Fetches origin, merges `origin/<current-branch>` when it exists, then upmerges the parent:

- **Matched story / GitHub issue** — parent is `base_branch`
- **Matched Jira / Linear task** — parent is the story branch
- **No match / empty issue list** — parent is `base_branch`

If you have only one project or one issue, selection steps are skipped automatically.

Use `--alias` when you want a non-interactive list of all assigned issues for a specific project.

### Jira output

For each issue it shows:

- **branch** — feature branch for this issue (own issue key + lowercase slugified summary, e.g. `feature/PROJ-123-add-auth-flow`); for Subtaak/Taak tasks, shows the parent story branch instead
- **task branch** — task branch name (parent + task key + lowercase slugified summary), for Subtaak/Taak issues (e.g. `feature/PROJ-123-PROJ-456-add-tests`)
- **commit message** — formatted as `(KEY) summary` (e.g. `(PROJ-456) Add tests`)

### GitHub output

For each assigned open issue it shows:

- **branch** — `issues/{number}-{slugified-title}` (e.g. `issues/1-implement-support-for-github-issues`)
- **commit message** — `(#{number}) {title}` (e.g. `(#1) Implement support for GitHub Issues`)

### Linear output

For each assigned open issue it shows:

- **branch** — feature branch for this issue (own identifier + slugified title, e.g. `feature/ENG-123-add-auth-flow`); for sub-issues, shows the parent story branch instead
- **task branch** — for sub-issues: `feature/{parent}-{child}-{slugified-title}` (e.g. `feature/ENG-123-ENG-456-implement-login`)
- **commit message** — `({identifier}) {title}` (e.g. `(ENG-456) Implement login`)

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

## Linear API key

Create a personal API key in Linear under **Settings > Security & access > Personal API keys**.

The key is passed as the `Authorization` header value (no `Bearer` prefix).

## Configuration

The CLI reads `~/.config/branch-helper/config.yml`. Copy `example.yml` as a starting point:

```yaml
default: project-x

aliases:
  project-x:
    source: jira
    base_branch: main
    jira:
      domain: "your-org.atlassian.net"
      username: "you@example.com"
      token: "your-jira-api-token"

  elmosgot:
    source: github
    base_branch: master
    github:
      token: "ghp_your-github-personal-access-token"

  my-linear:
    source: linear
    base_branch: master
    linear:
      token: "lin_api_your-personal-api-key"
```

- `default` — alias used when `--alias` is omitted and no `.branch-helper-default` is found
- `aliases.<name>.source` — `jira`, `github`, or `linear`
- `aliases.<name>.base_branch` — default branch to create feature branches from (e.g. `main`, `master`); required for wizard branch creation
- `aliases.<name>.jira` — Jira domain, username, token
- `aliases.<name>.github` — GitHub token
- `aliases.<name>.linear` — Linear personal API key

## Per-project default

Place a `.branch-helper-default` file in a repo root to override project settings for that repo. The first non-comment line is the alias name; you can optionally add a `base_branch` line for wizard branch creation:

```
elmosgot
base_branch: master
```

branch-helper walks up from the current directory until it finds this file (same idea as git finding `.git`). Commit it in your repo so the whole team gets the correct defaults.

**Alias priority:** `--alias` > `.branch-helper-default` alias line > `config.yml` `default`

**Base branch priority:** `.branch-helper-default` `base_branch` > `aliases.<name>.base_branch` in `config.yml`

When a local alias is set, the interactive wizard skips project selection and goes straight to issue selection. A `base_branch`-only file does not skip project selection.

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
python3 -m branch_helper --commit
python3 -m branch_helper --update
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

When you push a feature branch, a **draft PR** is opened automatically against `master` if one does not already exist.

### GitHub issues

Branch format: `issues/{number}-{slug}` (as suggested by `branch-helper --alias elmosgot`)

- **Title:** `(#N) {issue title}`
- **Body:** issue description plus `Closes #N`

### Linear issues

Branch format: `{TEAM}-{number}-{slug}` or `{prefix}/{TEAM}-{number}-{slug}` (e.g. `feature/BRA-1-add-linear-support`)

- **Title:** `(BRA-1) {issue title}`
- **Body:** issue description plus link to Linear

For sub-issue branches with multiple identifiers (e.g. `feature/ENG-123-ENG-456-implement-login`), the **last** identifier is used (`ENG-456`).

Requires repository secret **`LINEAR_API_KEY`** (Linear personal API key).

Branches that do not match either format are skipped.
