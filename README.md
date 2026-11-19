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

More plugins will be added one at a time.

## Requirements

`python3` on your `PATH` for plugins that ship hooks. The hooks use only the standard library.

## Development

```
python3 -m unittest discover -s tests -v
claude plugin validate . --strict
claude plugin validate ./plugins/quality-guard --strict
```

## Security

Please report vulnerabilities privately, see [SECURITY.md](SECURITY.md).

## License

MIT, see [LICENSE](LICENSE).
