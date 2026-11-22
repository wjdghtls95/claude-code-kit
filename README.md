# claude-code-kit

[English](README.md) | [한국어](README.ko.md)

A small kit of Claude Code plugins: guardrails and workflows for everyday engineering. Each plugin lives in its own folder under `plugins/` and can be installed on its own.

## Install

```
/plugin marketplace add wjdghtls95/claude-code-kit
/plugin install <plugin-name>@claude-code-kit
```

## Plugins

| Plugin | What it does | Docs |
|--------|--------------|------|
| `quality-guard` | Makes Claude declare a tier before editing source files, run a six-round protocol for risky changes and write tests first | [README](plugins/quality-guard/README.md) |
| `decision-log` | Keeps decisions, open topics, postponed work and lessons from getting lost: topic tracking, enhancement list, pattern capture, decision lookup | [README](plugins/decision-log/README.md) |

More plugins will be added one at a time.

## Shared settings

Plugins that read or write project files look for an optional `.claude-kit.json` in the project root. Every key is optional and the plugins work without the file.

```json
{
  "progress_file": "docs/progress/current.md",
  "decisions_dir": "docs/decisions",
  "enhancement_file": "docs/enhancement-list.md"
}
```

When a file a skill needs to read is missing, the skill skips that step, says so in one line and continues. A skill writes a file only for its own job (the enhancement list, pattern files, `INDEX.md`) and says in one line what it wrote and where. The progress file is never created for you.

## Requirements

`python3` on your `PATH` for plugins that ship hooks. The hooks use only the standard library.

## Development

```
python3 -m unittest discover -s tests -v
claude plugin validate . --strict
claude plugin validate ./plugins/quality-guard --strict
claude plugin validate ./plugins/decision-log --strict
```

## Security

Please report vulnerabilities privately, see [SECURITY.md](SECURITY.md).

## License

MIT, see [LICENSE](LICENSE).
