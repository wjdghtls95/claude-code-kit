# Security

## Reporting a vulnerability

Please do not open a public issue for a security problem. Use GitHub's private vulnerability reporting for this repository (Security tab → Report a vulnerability).

## Scope

The plugins in this repository run local scripts as Claude Code hooks. They read the hook input and, for `quality-guard`, the session transcript file that Claude Code passes in. They do not use the network, do not execute content from the transcript and do not write data. A report that shows otherwise is in scope.
