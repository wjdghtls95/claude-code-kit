# lookup

[English](README.md) | [한국어](README.ko.md)

Look things up properly while you work. Two kinds of questions come up all the time:

- **Code** — "how do I do X with this library", "what does this error mean", "show me an example". The answer has to fit **the version your project really has installed**, which is where web examples usually go wrong.
- **Information** — "is this still supported", "what changed", "A or B", "what is the latest". The answer has to come from **primary sources** and be **current**.

What the plugin does:

- A **find skill** (`/lookup:find`) with the steps: look in the project first (existing usage, the installed version, the installed source and types), then official docs for that version, changelogs, the library's own repository, issues, and blogs last. For information it prefers primary sources, opens the page the answer rests on, checks dates and confirms important claims with two independent sources.
- A small script that finds **the installed version and the local source folder** of a library: npm (package.json, lockfiles, node_modules including pnpm workspaces), Python (pyproject, requirements, uv.lock, poetry.lock, virtualenv site-packages) and Go (the version in the root go.mod only). For npm and Python it also lists the changelog and readme shipped inside the installed package, the repository and homepage links, and the changelog and documentation links a Python package declares, so the skill can read the history of exactly that version and open the right repository.
- A **reminder hook**: when your message clearly asks to look something up, Claude is told to use the find skill instead of answering from memory. Clear means an explicit request ("search for", "look up", "검색해줘", "찾아봐", "알아봐"), a code request ("코드 알려줘", "예제", "how do I"), a pasted error message, or a word like "latest", "supported", "최신", "지원돼?", "차이" in a message that also names a tool or a version. Opinion and planning questions ("어떻게 생각해", "좋을까") do not trigger it unless they also ask to search or for code. On about 1,200 real prompts it fired on under 2% of them. It only adds one line of context, never blocks and never repeats your message. Without it, Claude often answers from memory even when the skill is installed.

Every answer ends with **Sources** (links or file and line, with the version or date) and **Not confirmed** (what could not be verified).

## Install

```
/plugin marketplace add wjdghtls95/claude-code-kit
/plugin install lookup@claude-code-kit
```

Requirements: `python3` for the script and the reminder (standard library only). `gh` (the GitHub CLI) is used for repository and issue searches when it is available.

## Use

Just ask. If you want to be sure, call it directly:

```
/lookup:find how do I remove a repeatable job in bullmq
```

The script also runs on its own:

```
python3 scripts/project_context.py bullmq --root .
```

## Turning the reminder off

`LOOKUP=off` in the environment (`0`, `false`, `no`, `disable` and `disabled` also work), or `/plugin disable lookup`.

## Limits

- The reminder matches phrases, so it can miss a question (call `/lookup:find` then) or remind on one that needs no search. It is only a hint.
- The version script reads manifests and lockfiles. It does not run package managers.
- Search quality still depends on the web search and fetch tools available in your session.

## Development

```
python3 -m unittest discover -s tests -v
claude plugin validate ./plugins/lookup --strict
```

## License

MIT, see the repository `LICENSE`.
