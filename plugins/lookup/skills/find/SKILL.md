---
name: find
description: "Look things up properly while working: code (how to do X with a library, an error message, an API, an example that fits this project's installed version) or information (whether something is supported, what changed, A versus B, current facts). Use when the user asks how to do something, what an error means, whether a feature exists, for the latest state of something, or says search, look up or find."
---

Find the answer that is true **for this project and today**, show where it came from, and say what could not be confirmed.

## Step 1: decide what kind of search this is

| Kind | Signs | Go to |
|------|-------|-------|
| Code | "how do I", an error message, an API or option name, "example", a library name | Step 2 |
| Information | "is it supported", "what changed", "A or B", "latest", prices, limits, policies, dates | Step 3 |
| Both | "how do I" plus "is this still the way" | Step 2, then check the claims with Step 3 |

Decide the depth: a **quick** lookup (one fact or one snippet, a few searches) or a **deep** one (several sub-questions, many sources, a comparison). For a long written report, suggest the `deep-research` skill if it is available instead of doing it here.

Anything that changes over time (versions, prices, limits, release dates, policies, "latest") must be searched, not answered from memory.

## Step 2: code

1. **Look in the project first.**
   - Find the library version the project really uses: `python3 <base directory>/../../scripts/project_context.py <package> --root <project root>`. It prints the declared range, the installed version, the local source folder, the types file, the changelog and readme shipped with the package (`docs`) and its repository, homepage and changelog links (`links`). The base directory of this skill is shown when it loads.
   - Search the project for existing usage of the same API (Grep). Reuse the project's own pattern when there is one.
   - If the answer depends on library behavior, read the installed source or the types file in the folder the script printed. The installed code is the ground truth for this project.
   - If `docs` lists a changelog, search it for the API name before going to the web: it is the change history of exactly this version.
2. **Then the web, in this order:**
   1. The official documentation **for the installed major version** (look for a version switcher or versioned URL). Start from `links` when the script printed them. If a documentation tool is connected in this session (a docs MCP server, for example), use it with the installed version.
   2. The library's changelog or release notes when the version matters (breaking changes, deprecations, renamed APIs)
   3. The library's own repository (`links.repository`): examples, tests and source at the tag of the installed version (with `gh` when it is available, for example `gh api repos/<owner>/<repo>/contents/<path>?ref=v<version>`)
   4. Issues and discussions for bugs and workarounds (`gh search issues` when available)
   5. Blogs and Q&A sites last, and only when they state a version or a date you can check
3. **Fit the code to the project:** the installed version, the project's language and style, its existing helpers. Mark any API that is deprecated or renamed in the installed version.
4. **Check it when it is safe:** run a type check, a test or a tiny script that has no side effects (no network writes, no database changes, no file deletion). If you could not run it, say "not run".
5. **License:** if you copy more than a few lines from another project, name the source and its license.

## Step 3: information

1. Prefer **primary sources**: the vendor's documentation, the specification, the official announcement or changelog, the source code.
   For the claim the answer rests on, **open the primary page itself** with the fetch tool before you answer (load the tool first if it is listed as deferred). A search result snippet is a lead, not a source. If the page cannot be opened, say so under Not confirmed.
2. **Check the date** of every source. Today's date is in your context. Drop or flag anything that may be out of date.
3. **Confirm important claims with two independent sources.** If they disagree, show both and say which is newer or more authoritative.
4. Separate **facts** (with a source) from **opinions and estimates** (say whose).
5. Search technical topics in English first (more primary sources), and topics about Korean services, laws or companies in Korean. Answer in the user's language.

## Step 4: answer

```
[The answer in a few lines]

[Code fitted to the project, if any]

Sources
- [title] (URL or file:line) - what it confirms, version or date

Not confirmed
- [anything you could not verify, or "none"]
```

- Put the answer first. Keep sources short and specific (a URL or a file and line, plus what it proves).
- Say which version the answer is for, for example "for bullmq 5.81.3 installed in apps/server".
- Never invent an API, an option, a version number, a URL or a quote. If you are not sure, say so and say how to check.
- If the search changed something the project relies on (a deprecated API it uses, a security notice), point it out even if the user did not ask.
- Otherwise stay on the question. Do not add unrelated facts, and never add one without a source.
