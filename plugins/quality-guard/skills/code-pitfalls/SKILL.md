---
name: code-pitfalls
description: Checklist of bug patterns found in real code reviews - external API constraints, collection edge cases, falsy fallbacks, silent data loss, dead code, handler scope. Use before writing or reviewing code.
---

# Code Pitfalls — Mandatory Check Patterns

Bug patterns found in real code reviews. Check them before writing or reviewing code.

## 1. Constraints of external APIs

Check the official documentation for constraints before using an external API.

**Claude messages API**
- No consecutive messages with the same role — user and assistant must alternate. Check the role of the last history message before appending the current one
- Check whether the position of `cache_control` affects the role order

**Inserting data into XML/HTML**
- Always escape external data (database, API responses, user input) before putting it inside markup
- `<`, `>`, `&` → `&lt;`, `&gt;`, `&amp;`
- Python: `import html; html.escape(content)`
- Unescaped data fails silently as a parsing error, with no exception — hard to debug

## 2. Collection edge cases

**Check for an empty container before indexing**

```python
# ❌
e["loc"][-1]

# ✅
e["loc"][-1] if e["loc"] else "<root>"
```

**Empty contents inside a non-empty list**
- `if not list:` only checks the list length — every element may still be empty
- Check separately whether anything is left after filtering

```python
# ❌ the list is not empty but every content is "" → returns an empty wrapper
if not items:
    return ""

# ✅
if not items:
    return ""
# ... after filtering
if not by_kind:  # ← check that there is actually valid data
    return ""
```

**The falsy trap of an `or` fallback**
- `value or default` also replaces `""`, `0`, `[]` and `False` with the default
- To replace only `None`, use `value if value is not None else default`

```python
# ❌ "" is also replaced by DEFAULT_MESSAGE
super().__init__(message or self.DEFAULT_MESSAGE)

# ✅
super().__init__(message if message is not None else self.DEFAULT_MESSAGE)
```

## 3. State your implicit assumptions

**A whitelist filter must handle unknown values**
- Iterating over a fixed list silently drops every value that is not in the list
- Data is lost without an error, which is hard to notice in production

```python
# ❌ kinds outside KNOWN_KINDS are silently lost
for kind in KNOWN_KINDS:
    for content in by_kind.get(kind, []):
        ...

# ✅ handle unknown values explicitly
unknown = set(by_kind) - set(KNOWN_KINDS)
if unknown:
    # add logging, or fall back to a default kind
    pass
```

**Remove dead code immediately**
- An unreachable branch (an `isinstance` check, an impossible condition) communicates a wrong design intent
- Do not leave it in; remove it right away

```python
# ❌ checks for CustomError although nothing in the try block ever raises it
error = CustomError(str(exc)) if not isinstance(exc, CustomError) else exc

# ✅
error = CustomError(str(exc))
```

**State the limits of a handler or filter**
- Never assume "this handler catches everything" — write its scope down in a code comment
- A framework-wide `exception_handler(Exception)` (for example in FastAPI) does not catch errors raised while a streaming response (SSE) is being iterated
  → an exception raised during `StreamingResponse` iteration happens after the headers are sent, so the handler never runs
  → the streaming generator must have its own `try/except`
