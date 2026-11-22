---
name: decision-index
description: Create or refresh the index of decision documents. Use when the user asks to build, update or regenerate the decisions index.
---

Where the decision documents live: the `decisions_dir` value in `.claude-kit.json` at the project root, otherwise `docs/decisions`. If the folder does not exist, say so and stop.

1. Scan every markdown file under the decisions folder, including subfolders. Skip `INDEX.md`.
2. From each file, extract the work summary (title), the final choice, and the date.
3. Create or update `INDEX.md` in the decisions folder.
4. Use this table format: `| ID (relative path link) | Area | Title | Chosen option | Date |`. "Area" is the subfolder name, or empty for files in the root.
5. Sort by ID in ascending order.

Do not edit any decision document while building the index. If a file has no recognizable date or choice, leave that cell empty and list the file name in your reply.
