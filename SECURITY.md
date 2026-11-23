# Security

## Reporting a vulnerability

Please do not open a public issue for a security problem. Use GitHub's private vulnerability reporting for this repository (Security tab → Report a vulnerability).

## Scope

The plugins in this repository have two kinds of parts.

- **Hooks** are local Python scripts. They read the hook input and, for `quality-guard`, the session transcript file that Claude Code passes in. They do not use the network, do not execute content from the transcript and do not write data.
- **Skills and agents** are instructions for Claude. They can ask Claude to run commands (for example `git`, `gh`, `npx`) and to write project files, as each plugin's README lists under what it does or runs. They contain no code of their own.

A report that shows a hook doing more than described, or a skill that asks for something its README does not say, is in scope.
