# session-handoff

[English](README.md) | [한국어](README.ko.md)

Skills for handing work from one session to the next, all driven by a progress file.

- **Wrap up** — before you end a session: syncs the progress file, summarizes what was done, names the first task for next time and reports the git state (read only).
- **Resume** — when you come back: shows the latest progress entries and the git state, points out unfinished work and asks what to do next.
- **Next task check** — answers "what is next?": checks pull request states first, reads the progress file and lists what only you can do and what Claude can do next.

## Install

```
/plugin marketplace add wjdghtls95/claude-code-kit
/plugin install session-handoff@claude-code-kit
```

Nothing else is required. The plugin has no hooks and needs no `python3`. `gh` (the GitHub CLI) is used when it is available.

## Skills

Skills are namespaced by the plugin name:

| Skill | Use it for |
|-------|-----------|
| `/session-handoff:wrap-up` | Ending a session |
| `/session-handoff:resume` | Starting again after a break |
| `/session-handoff:next-task-check` | Deciding what to do next |

Most skills also start on their own when the conversation matches their description.

## What it does to your project

- `wrap-up` edits the progress file and, if you created new rules or skills, the project's index of them (and says in one line what it changed). It only reads git state. It never pushes, merges or opens pull requests, use a git workflow for that. If the progress file is very long it asks before moving old entries to an archive file.
- `resume` only reads. It never switches branches or pulls.
- `next-task-check` runs `gh pr list` (read only) and, if a pull request was merged, updates the progress file and says so.

## Settings

None required. The skills look for the progress file in this order: the path in `progress_file` of `.claude-kit.json`, `docs/progress/current.md`, `progress.md`. If none exists they skip that step and say so. A starting template is in `templates/progress.template.md`.

## Development

```
python3 -m unittest discover -s tests -v
claude plugin validate ./plugins/session-handoff --strict
```

## License

MIT, see the repository `LICENSE`.
