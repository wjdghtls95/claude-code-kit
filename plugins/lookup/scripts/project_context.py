#!/usr/bin/env python3
"""lookup: which version of a library does this project really use, and where is its source?

  project_context.py <package> [--root DIR]

Prints JSON: ecosystem, the declared range, the installed version (node_modules or site-packages first,
then the lockfile), the local source path to read, the changelog and readme files shipped with the installed
package, its repository, homepage and changelog links, and the manifests it looked at. Reads only.
Supports npm (package.json, package-lock.json, pnpm-lock.yaml, yarn.lock), Python (pyproject.toml,
requirements.txt, requirements-dev.txt, requirements.in, uv.lock, poetry.lock, .venv or venv site-packages)
and Go (the version in the root go.mod only).
"""
import glob
import json
import os
import re
import sys

MAX_READ_BYTES = 5_000_000
SKIP_DIRS = {"node_modules", ".git", ".venv", "venv", "dist", "build", ".next", "__pycache__"}


def _read(path):
    try:
        if os.path.getsize(path) > MAX_READ_BYTES:
            return None
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return None


def _manifests(root, names, depth=3):
    found = []
    for dirpath, dirs, files in os.walk(root):
        rel = os.path.relpath(dirpath, root)
        level = 0 if rel == "." else rel.count(os.sep) + 1
        # hidden folders (.claude/worktrees, .git, .turbo) hold copies or caches, not the project's own packages
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not d.startswith(".") and level < depth)
        for n in names:
            if n in files:
                found.append(os.path.join(dirpath, n))
    return found


DOC_PREFIXES = ("CHANGELOG", "CHANGES", "HISTORY", "RELEASES", "README")
DOC_EXTS = ("", ".md", ".markdown", ".rst", ".txt")
PY_URL_KEYS = {"changelog": "changelog", "changes": "changelog", "release notes": "changelog", "history": "changelog",
               "source": "repository", "source code": "repository", "repository": "repository", "code": "repository",
               "github": "repository", "homepage": "homepage", "home": "homepage",
               "documentation": "documentation", "docs": "documentation"}


def _web(url):
    url = url.strip() if isinstance(url, str) else ""
    return url if re.match(r"https?://\S+$", url) else None


def _repo_url(value):
    url = value.get("url") if isinstance(value, dict) else value
    if not isinstance(url, str):
        return None
    url = url.strip()
    if re.match(r"^[\w.-]+/[\w.-]+$", url):
        url = "github:" + url
    url = re.sub(r"^github:", "https://github.com/", url)
    url = re.sub(r"^git@([^:]+):", r"https://\1/", url)
    url = re.sub(r"^(git\+)?(git|ssh|https?)://(git@)?", "https://", url)
    return _web(re.sub(r"\.git$", "", url))


def _docs(folder):
    try:
        names = sorted(os.listdir(folder))
    except OSError:
        return []
    picked = [n for n in names for prefix in DOC_PREFIXES
              if n.upper().startswith(prefix) and os.path.splitext(n)[1].lower() in DOC_EXTS]
    picked.sort(key=lambda n: (n.upper().startswith("README"), n))
    return [os.path.join(folder, n) for n in picked]


def _py_links(metadata):
    links = {}
    for line in (metadata or "").split("\n\n", 1)[0].splitlines():
        key, _, value = line.partition(":")
        if key == "Home-page" and _web(value):
            links.setdefault("homepage", _web(value))
        if key == "Project-URL":
            label, _, url = value.partition(",")
            name = PY_URL_KEYS.get(label.strip().lower())
            if name and _web(url):
                links.setdefault(name, _web(url))
    return links


def _py_norm(name):
    return re.sub(r"[-_.]+", "-", name).lower()


# ---------- npm

def _npm(root, pkg, result):
    for path in _manifests(root, ["package.json"]):
        text = _read(path)
        try:
            data = json.loads(text) if text is not None else None
        except ValueError:
            data = None
        if not isinstance(data, dict):
            result["notes"].append(f"could not read package.json at {os.path.relpath(path, root)}")
            continue
        result["manifests"].append(os.path.relpath(path, root))
        for section in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
            deps = data.get(section)
            if isinstance(deps, dict) and pkg in deps and result["declared"] is None:
                result["declared"] = str(deps[pkg])
    if not result["manifests"]:
        return False
    result["ecosystem"] = "npm"
    installed = None
    lock = _read(os.path.join(root, "package-lock.json"))
    if lock:
        try:
            entry = json.loads(lock).get("packages", {}).get(f"node_modules/{pkg}", {})
            installed = entry.get("version") or installed
        except (ValueError, AttributeError):
            result["notes"].append("could not read package-lock.json")
    pnpm = _read(os.path.join(root, "pnpm-lock.yaml"))
    if pnpm and not installed:
        m = re.search(r"^\s+['\"]?/?" + re.escape(pkg) + r"@(\d[^:('\"\s]*)", pnpm, re.M)
        installed = m.group(1) if m else None
    yarn = _read(os.path.join(root, "yarn.lock"))
    if yarn and not installed:
        m = re.search(r'^"?' + re.escape(pkg) + r'@[^\n]*:\n\s+version "?([^"\n]+)"?', yarn, re.M)
        installed = m.group(1) if m else None
    # the root node_modules first, then each workspace package's own node_modules (pnpm puts them there)
    candidates = [os.path.join(root, "node_modules", *pkg.split("/"), "package.json")]
    candidates += [os.path.join(root, os.path.dirname(m), "node_modules", *pkg.split("/"), "package.json")
                   for m in result["manifests"] if os.path.dirname(m)]
    pj = next((c for c in candidates if os.path.isfile(c)), candidates[0])
    text = _read(pj)
    if text:
        try:
            data = json.loads(text)
            installed = data.get("version") or installed
            result["source_path"] = os.path.dirname(pj)
            result["types"] = data.get("types") or data.get("typings")
            result["docs"] = _docs(os.path.dirname(pj))
            links = {"repository": _repo_url(data.get("repository")), "homepage": _web(data.get("homepage"))}
            result["links"] = {k: v for k, v in links.items() if v}
        except ValueError:
            result["notes"].append("could not read the installed package.json")
    result["installed"] = installed
    return True


# ---------- Python

def _python(root, pkg, result):
    want = _py_norm(pkg)
    manifests = _manifests(root, ["pyproject.toml", "requirements.txt", "requirements-dev.txt", "requirements.in"])
    venvs = sorted(glob.glob(os.path.join(root, ".venv", "lib", "python*", "site-packages"))
                   + glob.glob(os.path.join(root, "venv", "lib", "python*", "site-packages")))
    locks = [n for n in ("uv.lock", "poetry.lock") if os.path.isfile(os.path.join(root, n))]
    if not manifests and not locks and not venvs:
        return False
    result["ecosystem"] = "python"
    for path in manifests:
        result["manifests"].append(os.path.relpath(path, root))
        text = _read(path) or ""
        if path.endswith(".toml"):
            for m in re.finditer(r'"([A-Za-z0-9_.\-]+)\s*(\[[^\]]*\])?\s*([<>=!~][^";]*)?', text):
                if _py_norm(m.group(1)) == want and result["declared"] is None:
                    result["declared"] = (m.group(3) or "").strip() or "any"
            for m in re.finditer(r'^([A-Za-z0-9_.\-]+)\s*=\s*"([^"]+)"', text, re.M):
                if _py_norm(m.group(1)) == want and result["declared"] is None:
                    result["declared"] = m.group(2)
        else:
            for line in text.splitlines():
                m = re.match(r"^\s*([A-Za-z0-9_.\-]+)\s*(\[[^\]]*\])?\s*([<>=!~].*)?$", line.split("#", 1)[0])
                if m and _py_norm(m.group(1)) == want and result["declared"] is None:
                    result["declared"] = (m.group(3) or "").strip() or "any"
    for lockname in ("uv.lock", "poetry.lock"):
        text = _read(os.path.join(root, lockname))
        if not text:
            continue
        for m in re.finditer(r'\[\[package\]\]\s*\nname\s*=\s*"([^"]+)"\s*\nversion\s*=\s*"([^"]+)"', text):
            if _py_norm(m.group(1)) == want:
                result["installed"] = m.group(2)
    for sp in venvs:
        for info in glob.glob(os.path.join(sp, "*.dist-info")):
            base = os.path.basename(info)[: -len(".dist-info")]
            name, _, version = base.rpartition("-")
            if _py_norm(name) == want:
                result["installed"] = version
                result["links"] = _py_links(_read(os.path.join(info, "METADATA")))
                for cand in (name, name.replace("-", "_"), want.replace("-", "_")):
                    if os.path.isdir(os.path.join(sp, cand)):
                        result["source_path"] = os.path.join(sp, cand)
                        result["docs"] = _docs(result["source_path"])
                        break
    return True


# ---------- Go

def _go(root, pkg, result):
    text = _read(os.path.join(root, "go.mod"))
    if text is None:
        return False
    result["ecosystem"] = "go"
    result["manifests"].append("go.mod")
    m = re.search(r"^\s*(?:require\s+)?" + re.escape(pkg) + r"\s+(v\S+)", text, re.M)
    if m:
        result["declared"] = result["installed"] = m.group(1)
    return True


def _empty(pkg):
    return {"package": pkg, "ecosystem": None, "declared": None, "installed": None,
            "source_path": None, "types": None, "docs": [], "links": {}, "manifests": [], "notes": []}


def find(root, pkg):
    # each ecosystem fills its own result, so notes from a package.json do not end up in a Python answer
    tried = []
    for probe in (_npm, _python, _go):
        result = _empty(pkg)
        found = probe(root, pkg, result)
        if not found and not result["notes"]:
            continue
        if found and (result["declared"] or result["installed"]):
            return result
        tried.append(result)
    result = tried[0] if tried else _empty(pkg)
    for other in tried[1:]:
        result["manifests"] += other["manifests"]
        result["notes"] += other["notes"]
    result["notes"].append(f"{pkg} not found in the project's manifests or lockfiles")
    return result


def main(argv, stdout=None):
    out = stdout or sys.stdout
    args = [a for a in argv]
    if not args or args[0].startswith("-"):
        out.write(__doc__)
        return 2
    root = "."
    if "--root" in args:
        i = args.index("--root")
        root = args[i + 1] if i + 1 < len(args) else "."
    out.write(json.dumps(find(os.path.abspath(root), args[0]), ensure_ascii=False, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
