# quality-guard

[English](README.md) | [한국어](README.ko.md)

Hooks and skills that make Claude work with discipline on code:

- **Tier declaration** — Claude must declare a tier (`[A]`, `[B]` or `[C]`) in its reply before it edits a source file. A hook blocks the edit otherwise.
- **Six-round protocol** — for new features, bug fixes and design changes (`[A]`), Claude runs a checklist (intent, adversarial review, reference, simplicity, durability, testability) and waits for your confirmation before writing code.
- **Test first** — an optional hook blocks creating a new source file before its test file exists.
- **Skills** — the rules behind all of this, loaded on demand.

> **Heads-up: this plugin can block file edits.** If Claude edits a source file without declaring a tier first, the hook refuses the edit and tells Claude what to do. That is the point of the plugin, but it can look like a bug if you do not expect it. See [Turning it off](#turning-it-off).

## Install

```
/plugin marketplace add wjdghtls95/claude-code-kit
/plugin install quality-guard@claude-code-kit
```

Requirements: `python3` on your `PATH` (standard library only, nothing to install). On Windows, make sure `python3` resolves to Python 3.

## The tiers

| Tier | When | What Claude does |
|------|------|------------------|
| `[A]` | New feature, bug fix, design change | Runs the six rounds, shows a 5-line summary, waits for your confirmation, then writes tests before code |
| `[B]` | Review fix, assertion change, constant rename | Abbreviated check: intent, risk, why the rest is skipped (3 lines) |
| `[C]` | Docs and meta files | One-line reason, no rounds |

A declaration counts for the whole turn, so Claude declares once and can then make several edits. After you confirm an `[A]` plan, your confirmation starts a new turn, so Claude declares the tier again in its next reply.

## Skills

Skills are namespaced by the plugin name:

| Skill | Use it for |
|-------|-----------|
| `/quality-guard:code-generation-protocol` | The tiers, the six rounds and the confirmation gate |
| `/quality-guard:tdd-rule` | Test list, Red, Green, Refactor, readable tests, and a mutation check that shows whether the tests really guard the code |
| `/quality-guard:coding-behavior-guidelines` | Think before coding, simplicity, surgical changes |
| `/quality-guard:code-consistency` | Flag pattern changes, Rule of Three |
| `/quality-guard:code-pitfalls` | Bug patterns found in real reviews |
| `/quality-guard:code-standard` | A TypeScript code standard that ESLint checks (bundled config), the review rules a linter cannot check, and refactoring without changing behavior |
| `/quality-guard:project-structure` | How to decide folder structure, defaults, and letting the linter keep the dependency direction |

A short reminder of the tier rule is added to every session when it starts.

Two files come with the skills:

- `templates/eslint-standard.js`: the ESLint flat config behind `code-standard`. Copy it into a TypeScript project and install `eslint @eslint/js typescript-eslint @stylistic/eslint-plugin` (tested with ESLint 9, typescript-eslint 8, @stylistic 5).
- `scripts/mutation_check.py`: breaks the source one place at a time from a list in `.mutations.json`, runs your tests and puts the file back. It changes source files while it runs and keeps a `.mutation-backup` copy next to each one until it is restored (Ctrl+C and a normal kill restore the file; after a hard kill the next run refuses to start until you restore it from the copy). See the `tdd-rule` skill.

## Configuration

Everything works without configuration. To change the defaults, create `.quality-guard.json` in your project root:

```json
{
  "source_extensions": [".ts", ".tsx", ".py"],
  "skip_patterns": ["node_modules/", "dist/", "generated/"],
  "tdd": {
    "mappings": [
      { "source": "^src/(?P<name>[^/]+)\\.py$", "test": "tests/test_{name}.py" },
      { "source": "^lib/(?P<name>[^/]+)\\.ts$", "test": "lib/__tests__/{name}.test.ts", "content_regex": "export " }
    ]
  }
}
```

| Key | Meaning |
|-----|---------|
| `source_extensions` | Which files need a tier declaration. Default: common code extensions |
| `skip_patterns` | Paths that are never checked, by either hook. A pattern is a prefix match on a folder or file name: `dist/` matches `pkg/dist/a.js` but not `redist/a.js`, and `foo` also matches `foobar/a.ts`. Default: `node_modules/`, `dist/`, `build/`, `.git/`, lock files and similar |
| `tdd.mappings` | Regex `source` → `test` path template (named groups become `{name}`). The first mapping that applies decides: its `source` matches and, if it has a `content_regex`, the new file's content matches too. The test-first hook only runs when this list is non-empty |
| `tdd.mappings[].content_regex` | Optional. Enforce only when the new file's content matches |
| `tdd.test_file_patterns` | Optional. Regexes that mark a file as a test file (these are never blocked) |
| `disable` | Optional. A list with `"tier_guard"` and/or `"tdd_guard"` to turn a single hook off |

Invalid settings (broken JSON, wrong value types, invalid regular expressions) are ignored with a notice, and the defaults apply to them.

## Turning it off

| How | Effect |
|-----|--------|
| `QUALITY_GUARD=off` in the environment | Both hooks and the session reminder do nothing (`0`, `false`, `no`, `disable` and `disabled` also work) |
| `"disable": ["tier_guard"]` in `.quality-guard.json` | Turns off one hook only (turning off `tier_guard` also silences the session reminder) |
| `QUALITY_GUARD_TAIL_BYTES` in the environment | Advanced: how many bytes of the end of the session transcript the tier check reads (default 2,000,000, at most 50,000,000) |
| `/plugin disable quality-guard` | Disables the whole plugin |
| Remove the plugin | Nothing is left behind, the plugin stores no data (`mutation_check.py` changes your source files only while it runs) |

## How the tier check works and what it cannot do

The hook reads the session transcript, walks back to your last message and looks for `[A]`, `[B]` or `[C]` in Claude's text since then. It is deliberately forgiving:

- It **blocks only when it can see Claude's text for the current turn and no declaration is in it.**
- Claude Code saves a response to the transcript only after its tools have run, so the hook **cannot see a declaration that is in the same response as the edit**. When no text is visible yet (typically the first edit of a turn), the hook allows the edit and prints a notice.
- In a multi-step turn this can cause **one unnecessary block**: Claude declared a tier in the same response as the edit, but the hook only sees the earlier, undeclared text. Claude retries, and by then the declaration is saved and visible. It never loops, because every retry follows a tool result and the previous response is saved by then.
- If the transcript is missing or unreadable, the hook allows the edit as well. A guard that locks you out is worse than a guard that sometimes misses.
- Because of these limits it is a nudge, not a security boundary. Most of the work is done by the reminder added at session start, which makes Claude declare a tier on its own; the hook catches later edits in the same turn.
- A declaration from an earlier turn does not count.

## Development

```
python3 -m unittest discover -s tests -v
claude plugin validate ./plugins/quality-guard --strict
```

## License and attribution

MIT, see the repository `LICENSE`. The `coding-behavior-guidelines` skill is derived from Andrej Karpathy's public observations on LLM coding pitfalls.
