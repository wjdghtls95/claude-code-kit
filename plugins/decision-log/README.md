# decision-log

[English](README.md) | [한국어](README.ko.md)

Skills and templates that keep decisions, open questions, postponed work and lessons from getting lost between sessions.

- **Open topics** — Claude marks undecided topics at the end of a reply and saves working notes when you ask. A topic is never called confirmed until you say so.
- **Enhancement list** — features you postponed on purpose are recorded with the trigger that should bring them back.
- **Pattern capture** — corrections and lessons are buffered in a file, then promoted to reusable pattern files after you confirm.
- **Decision lookup and update** — answer "why did we choose X" from your decision documents, and change a confirmed decision only after showing a preview.
- **Decision index** — build an `INDEX.md` of your decision documents.

## Install

```
/plugin marketplace add wjdghtls95/claude-code-kit
/plugin install decision-log@claude-code-kit
```

Requirements: `python3` on your `PATH` for the session-start reminder (standard library only). The skills need nothing else.

## Skills

Skills are namespaced by the plugin name:

| Skill | Use it for |
|-------|-----------|
| `/decision-log:topic-tracking` | Mark open topics, save working notes, follow the lifecycle until a decision is confirmed |
| `/decision-log:enhancement-tracking` | Record postponed work with its trigger |
| `/decision-log:pattern-capture` | Buffer lessons, promote them to pattern files |
| `/decision-log:concept-update` | Change an already confirmed decision with a preview |
| `/decision-log:decision-lookup` | Answer "why" questions from the decision documents |
| `/decision-log:decision-index` | Build `INDEX.md` for the decisions folder |

Most skills also start on their own when the conversation matches their description.

## Settings

Everything works without settings. To change where files live, create `.claude-kit.json` in the project root. A copy is in `templates/claude-kit.example.json`.

```json
{
  "progress_file": "docs/progress/current.md",
  "decisions_dir": "docs/decisions",
  "enhancement_file": "docs/enhancement-list.md"
}
```

| Key | Meaning | Default |
|-----|---------|---------|
| `progress_file` | Where working notes are saved (the progress file) | first of `docs/progress/current.md`, `progress.md` |
| `decisions_dir` | Folder of decision documents | `docs/decisions` |
| `enhancement_file` | The enhancement list | `docs/enhancement-list.md` |

If the progress file does not exist, the skill skips that step and tells you. It never creates the file on its own. A starting template is in `templates/progress.template.md`.

## Session-start reminder

When a session starts, a small hook looks for `.claude/memory/pattern_candidates.md` in the project. If it has lines that start with `- [pending]`, Claude is reminded to ask you whether to review them. The hook never blocks anything and never writes files.

Turn it off with `DECISION_LOG=off` in the environment (`0`, `false`, `no`, `disable` and `disabled` also work), or disable the whole plugin with `/plugin disable decision-log`.

## Templates and examples

- `templates/pattern_candidates.md` — the buffer file for pattern candidates
- `templates/PATTERN_INDEX.md` — an empty pattern index
- `templates/progress.template.md` — a starting progress file with a Working Notes section
- `examples/` — two example patterns showing the pattern file format and file names

## Development

```
python3 -m unittest discover -s tests -v
claude plugin validate ./plugins/decision-log --strict
```

## License

MIT, see the repository `LICENSE`.
