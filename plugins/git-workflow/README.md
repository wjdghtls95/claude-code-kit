# git-workflow

[English](README.md) | [한국어](README.ko.md)

Skills for the git delivery loop, from the last edit to a merged pull request.

- **Ship** — one step to commit (with a message you confirm), push and open a pull request, then pick the review level the change needs.
- **Land** — merge a reviewed pull request (squash), delete the branch and return to the default branch, after you confirm.
- **Branch check** — lists open pull requests, leftover local and remote branches, failing CI, commits that break the convention and unpushed commits.
- **Safe git rules** — sync the default branch, one branch per task, rebase instead of merge, never force-push without your approval, never auto-resolve conflicts.
- **Ship reminder** — a one-line nudge at the end of a reply when coding work is finished.
- **Conventions** — default branch names, commit message format and scope, merge strategy and a pull request checklist. They are defaults: a project's own conventions win.

## Install

```
/plugin marketplace add wjdghtls95/claude-code-kit
/plugin install git-workflow@claude-code-kit
```

Requirements: `git` and the GitHub CLI `gh` (logged in) for the pull request steps. The plugin has no hooks and needs no `python3`.

## Skills

Skills are namespaced by the plugin name:

| Skill | Use it for |
|-------|-----------|
| `/git-workflow:ship` | Commit, push and open a pull request. Arguments: a quoted message, or `--no-review` |
| `/git-workflow:land` | Merge the pull request, delete the branch, return to the default branch |
| `/git-workflow:pr-check` | Open pull requests, leftover branches, CI and convention check |
| `/git-workflow:git-rules` | Safe day-to-day git rules |
| `/git-workflow:ship-reminder` | The finish-line reminder |
| `/git-workflow:git-conventions` | Branch names, commit format, merge strategy |

Most skills also start on their own when the conversation matches their description.

## What it does to your repository

- `ship` runs `git add` with file names (never `git add -A`), `git commit`, `git push` and `gh pr create`, and asks you to confirm the commit message it generated (a message you pass yourself is used as given).
- `land` runs `gh pr merge --squash --delete-branch`, `git checkout` and `git pull`, and asks you to confirm first.
- `pr-check` runs `git fetch --prune` (it updates remote-tracking references only), reads pull request and branch state, deletes branches only after you approve, and adds a line to the progress file only if you agree.
- The skills never push to the default branch directly. Force-push needs your approval every time.

## Settings

None required. The skills detect the default branch of the repository. If a progress file exists (`docs/progress/current.md` or `progress.md`, or the path in `progress_file` of `.claude-kit.json`), `pr-check` adds one line to it. A starting template is in `templates/progress.template.md`.

## Development

```
python3 -m unittest discover -s tests -v
claude plugin validate ./plugins/git-workflow --strict
```

## License

MIT, see the repository `LICENSE`.
