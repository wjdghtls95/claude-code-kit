"""Shared helpers for the quality-guard hooks (standard library only)."""
import json
import os
import re
import sys

PREFIX = "[quality-guard]"
CONFIG_FILE = ".quality-guard.json"
DISABLE_VALUES = {"off", "0", "false", "disable", "disabled", "no"}
DEFAULT_TAIL_BYTES = 2_000_000
MAX_TAIL_BYTES = 50_000_000
EDIT_TOOLS = {"Edit", "Write", "MultiEdit"}
# A tier token stands alone: not part of a word or index (arr[A]) and not a markdown link ([A](url)).
TIER_PATTERN = re.compile(r"(?<![\w\]])\[(?:A|B|C)\](?!\()")

DEFAULT_SOURCE_EXTENSIONS = [
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".py", ".go", ".rs", ".java", ".kt", ".rb",
    ".php", ".cs", ".swift", ".c", ".cc", ".cpp", ".h", ".hpp", ".sql",
]
DEFAULT_SKIP_PATTERNS = [
    "node_modules/", ".git/", "dist/", "build/", ".claude/", "__pycache__/", ".venv/", "vendor/",
    "package-lock.json", "pnpm-lock.yaml", "yarn.lock",
]
DEFAULT_TEST_FILE_PATTERNS = [
    r"(^|/)(tests?|__tests__)/",
    r"\.(spec|test)\.[A-Za-z]+$",
    r"(^|/)test_[^/]+\.py$",
    r"_test\.(go|py)$",
    r"(^|/)conftest\.py$",
]


def warn(message):
    print(f"{PREFIX} {message}", file=sys.stderr)


def guarded(main):
    """Run a hook entry point. An unexpected error must never block the user's work."""
    try:
        return main()
    except Exception as exc:  # noqa: BLE001 - the hook fails open on purpose
        warn(f"internal error ({exc.__class__.__name__}); allowing the action.")
        return 0


def is_disabled(env=None):
    value = (env if env is not None else os.environ).get("QUALITY_GUARD", "")
    return value.strip().lower() in DISABLE_VALUES


def hook_disabled(config, name):
    return name in config.get("disable", [])


def read_hook_input(stream):
    """Read the hook JSON as UTF-8, whatever the platform's default encoding is."""
    try:
        raw = stream.buffer.read() if hasattr(stream, "buffer") else stream.read()
        data = json.loads(raw.decode("utf-8", errors="replace") if isinstance(raw, bytes) else raw)
    except (ValueError, OSError):
        return None
    return data if isinstance(data, dict) else None


def project_dir(hook_input, env=None):
    env = env if env is not None else os.environ
    return env.get("CLAUDE_PROJECT_DIR") or hook_input.get("cwd") or os.getcwd()


def _is_str_list(value):
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def _compiles(pattern):
    try:
        re.compile(pattern)
        return True
    except re.error:
        return False


def _valid_mapping(mapping):
    if not isinstance(mapping, dict):
        return False
    source, test, content = mapping.get("source"), mapping.get("test"), mapping.get("content_regex")
    if not (isinstance(source, str) and isinstance(test, str) and _compiles(source)):
        return False
    return content is None or (isinstance(content, str) and _compiles(content))


def sanitize_config(data):
    """Keep only well-formed settings. Returns (clean_config, problems)."""
    clean, problems = {}, []
    for key in ("source_extensions", "skip_patterns", "disable"):
        if key in data:
            if _is_str_list(data[key]):
                clean[key] = data[key]
            else:
                problems.append(f"'{key}' must be a list of strings")
    if "tdd" in data:
        tdd = data["tdd"]
        if not isinstance(tdd, dict):
            problems.append("'tdd' must be an object")
        else:
            clean["tdd"] = clean_tdd = {}
            patterns = tdd.get("test_file_patterns")
            if patterns is not None:
                if _is_str_list(patterns) and all(_compiles(p) for p in patterns):
                    clean_tdd["test_file_patterns"] = patterns
                else:
                    problems.append("'tdd.test_file_patterns' must be a list of valid regular expressions")
            mappings = tdd.get("mappings")
            if mappings is not None:
                if isinstance(mappings, list):
                    clean_tdd["mappings"] = [m for m in mappings if _valid_mapping(m)]
                    if len(clean_tdd["mappings"]) != len(mappings):
                        problems.append("some 'tdd.mappings' entries are invalid and were skipped")
                else:
                    problems.append("'tdd.mappings' must be a list")
    return clean, problems


def load_config(directory):
    """Return (config, warning). A missing file is normal; invalid settings fall back to the defaults."""
    path = os.path.join(directory, CONFIG_FILE)
    if not os.path.isfile(path):
        return {}, None
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (ValueError, OSError) as exc:
        return {}, f"{CONFIG_FILE} is invalid ({exc.__class__.__name__}); using defaults."
    if not isinstance(data, dict):
        return {}, f"{CONFIG_FILE} must contain a JSON object; using defaults."
    clean, problems = sanitize_config(data)
    warning = f"{CONFIG_FILE}: " + "; ".join(problems) + "; the defaults apply to those settings." if problems else None
    return clean, warning


def relative_posix(path, directory):
    absolute = path if os.path.isabs(path) else os.path.join(directory, path)
    try:
        relative = os.path.relpath(absolute, directory)
    except ValueError:
        relative = absolute
    return relative.replace(os.sep, "/")


def is_skipped(relative, config):
    """A skip pattern matches from the start of a folder or file name, never from the middle of one."""
    padded = "/" + relative
    return any(("/" + pattern.lstrip("/")) in padded for pattern in config.get("skip_patterns", DEFAULT_SKIP_PATTERNS) if pattern)


def is_source_file(path, directory, config):
    relative = relative_posix(path, directory)
    extensions = [e.lower() for e in config.get("source_extensions", DEFAULT_SOURCE_EXTENSIONS)]
    return os.path.splitext(relative)[1].lower() in extensions and not is_skipped(relative, config)


def tail_limit(env=None):
    raw = (env if env is not None else os.environ).get("QUALITY_GUARD_TAIL_BYTES", "").strip()
    if raw.isascii() and raw.isdigit() and int(raw) > 0:
        return min(int(raw), MAX_TAIL_BYTES)
    return DEFAULT_TAIL_BYTES


def read_tail(path, max_bytes):
    """Return (lines, complete). complete is False when the start of the file was cut off."""
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        if size > max_bytes:
            f.seek(size - max_bytes)
            data = f.read()
            data = data.split(b"\n", 1)[1] if b"\n" in data else b""
            complete = False
        else:
            data = f.read()
            complete = True
    return data.decode("utf-8", errors="replace").splitlines(), complete


def _message(entry):
    inner = entry.get("message")
    return inner if isinstance(inner, dict) else entry


def entry_role(entry):
    return _message(entry).get("role") or entry.get("role") or entry.get("type")


def _blocks(entry):
    content = _message(entry).get("content")
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    return [b for b in content if isinstance(b, dict)] if isinstance(content, list) else []


def assistant_texts(entry):
    return [b["text"] for b in _blocks(entry) if b.get("type") == "text" and isinstance(b.get("text"), str)]


def _has_user_content(block):
    kind = block.get("type")
    if kind == "text":
        return bool(str(block.get("text") or "").strip())
    return kind in ("image", "document")


def is_user_prompt(entry):
    """A real user prompt that starts a new turn.

    Entries that carry a tool result are not prompts: Claude Code stores a message the user sends
    while it is working in the same entry as the tool result, and that must not reset the turn.
    """
    if entry_role(entry) != "user" or entry.get("isMeta"):
        return False
    blocks = _blocks(entry)
    if any(b.get("type") == "tool_result" for b in blocks):
        return False
    return any(_has_user_content(b) for b in blocks)


def analyze_current_turn(lines, complete):
    """Walk back to the last user prompt and collect assistant text.

    Returns (texts, boundary_found). The start of a complete file counts as a boundary.
    """
    texts, boundary = [], complete
    for raw in reversed(lines):
        try:
            entry = json.loads(raw)
        except ValueError:
            continue
        if not isinstance(entry, dict):
            continue
        if is_user_prompt(entry):
            boundary = True
            break
        if entry_role(entry) == "assistant":
            texts.extend(assistant_texts(entry))
    return texts, boundary
