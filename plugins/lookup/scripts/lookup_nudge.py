#!/usr/bin/env python3
"""lookup: when a prompt clearly asks to look something up, remind Claude to use the find skill (UserPromptSubmit hook).

Strong signals (an explicit search request, a code request, a pasted error) are enough on their own.
Weak words ("최신", "차이", "지원돼", "latest") count only when the prompt also names a tool such as a library,
and never in an opinion or planning question. It only adds one line of context. It never blocks, never writes files and
never repeats the prompt. Set LOOKUP=off to disable.
"""
import json
import os
import re
import sys

MAX_PROMPT_CHARS = 20_000
OFF_VALUES = {"off", "0", "false", "no", "disable", "disabled"}

STRONG_KO = ("검색해", "검색 해", "서치해", "서치 해", "찾아봐", "찾아 봐", "찾아줘", "찾아 줘", "알아봐", "알아 봐",
             "조사해", "공식 문서", "코드 알려", "예제", "샘플 코드", "사용법")
STRONG_EN = ("look up", "look it up", "search for", "search the", "google it", "find docs", "docs for",
             "how do i", "how can i", "how to ", "example of", "code for")
WEAK = ("최신", "지원돼", "지원 돼", "지원되", "지원하나", "지원 종료", "지원 중단", "아직 돼", "아직 되", "언제까지", "차이", "바뀐", "달라진", "deprecated",
        "latest", "supported", "what changed", "difference between", " vs ", "end of life", "eol")
OPINION = ("생각해", "생각하", "어떤지", "좋을지", "좋을까", "좋은가", "맞을까", "맞나", "맞는지", "괜찮", "별로", "추천",
           "의견", "해야될지", "해야 될지", "해야되나", "하는게 나", "what do you think", "should i", "would you")
ERROR_TEXT = re.compile(r"\b[A-Z]\w*(Error|Exception)\b|Traceback \(most recent call last\)|\bE[A-Z]{3,}\b:")
WORD = re.compile(r"[A-Za-z0-9][A-Za-z0-9.+#@/-]*")
HANGUL = re.compile(r"[가-힣]")

CONTEXT = ("lookup: this looks like a lookup question. First call the Skill tool with skill \"lookup:find\" "
           "and follow its steps (it finds the installed library version and the right sources). Do not answer from memory "
           "or from the project code alone, and do not work from this note instead of the skill. A question about a library, "
           "an API, an error or a version is a lookup even when it is about this project. Skip it only when the user wants an "
           "opinion, asks where one of their own files or notes is, or the answer is already in this conversation.")


def names_a_tool(text):
    """A library, product or version in the prompt, not counting the weak words themselves"""
    rest = text
    for w in WEAK:
        rest = re.sub(re.escape(w.strip()), " ", rest, flags=re.I)
    words = WORD.findall(rest)
    if HANGUL.search(text):
        return any(len(w) >= 2 or w.isdigit() for w in words)
    # in English every word is Latin, so only name-like words count: BullMQ, SDK, node20, v5, a mid-sentence Capital
    return any(re.search(r"[0-9.@/]", w) or re.search(r"[A-Z]", w[1:]) or (i > 0 and w[0].isupper())
               for i, w in enumerate(words))


def looks_like_lookup(prompt):
    text = prompt[:MAX_PROMPT_CHARS].strip()
    if not text or text.startswith("/"):
        return False
    low = " " + text.lower() + " "
    if any(p in low for p in STRONG_KO + STRONG_EN) or ERROR_TEXT.search(text):
        return True
    if any(p in low for p in OPINION):
        return False
    return any(p in low for p in WEAK) and names_a_tool(text)


def main():
    if os.environ.get("LOOKUP", "").strip().lower() in OFF_VALUES:
        return 0
    try:
        data = json.loads(sys.stdin.buffer.read(MAX_PROMPT_CHARS * 4).decode("utf-8", errors="replace") or "{}")
    except ValueError:
        return 0
    prompt = data.get("prompt") if isinstance(data, dict) else None
    if isinstance(prompt, str) and looks_like_lookup(prompt):
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": CONTEXT}}))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
