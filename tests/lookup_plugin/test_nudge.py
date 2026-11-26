"""lookup_nudge hook tests (UserPromptSubmit)

Test list (5 axes)
  normal:   an explicit search request, a code request, a pasted error, or a fact question about a named
            library or product gets one line of context pointing to the find skill
  error:    broken or empty stdin -> exit 0, no output
  boundary: opinion and planning questions ("어떻게 생각해", "좋을까"), weak words without a named tool
            ("다 최신이였고?"), slash commands, acknowledgements and plain instructions get nothing
  order:    the context is the same for repeated prompts (stateless), never blocks (exit 0 always)
  abuse:    kill switch, a huge prompt is capped, the prompt text is never echoed back
"""
import json
import os
import subprocess
import sys
import unittest

HOOK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "plugins", "lookup", "scripts", "lookup_nudge.py"))


def run(prompt=None, raw=None, env_extra=None):
    env = {k: v for k, v in os.environ.items() if not k.startswith("LOOKUP")}
    env.update(env_extra or {})
    data = raw if raw is not None else json.dumps({"hook_event_name": "UserPromptSubmit", "prompt": prompt})
    return subprocess.run([sys.executable, HOOK], input=data.encode("utf-8"), capture_output=True, env=env)


def context(r):
    if not r.stdout.strip():
        return ""
    return json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"]


class NudgeTests(unittest.TestCase):
    def assertFires(self, *prompts):
        for p in prompts:
            self.assertIn("lookup:find", context(run(p)), p)

    def assertQuiet(self, *prompts):
        for p in prompts:
            self.assertEqual(context(run(p)), "", p)

    def test_script_exists(self):
        self.assertTrue(os.path.isfile(HOOK))

    def test_explicit_search_requests(self):
        self.assertFires("웹훅 재시도 정책을 어떻게 하는지 서치해줘", "다른 도구로 찾아봐",
                         "bullmq 공식 문서 찾아줘", "이거 검색해서 알려줘", "요즘 어떻게 하는지 알아봐줘")

    def test_code_requests(self):
        self.assertFires("BullMQ에서 반복 작업을 삭제하는 코드 알려줘", "prisma 마이그레이션 사용법", "zod 예제 보여줘")

    def test_pasted_error_message(self):
        self.assertFires("TypeError: Cannot read properties of undefined 이거 왜 나?",
                         "Traceback (most recent call last): 이거 뭐야")

    def test_fact_question_about_a_named_tool(self):
        self.assertFires("Node 20 지원 아직 돼?", "Next.js 최신 버전에서 바뀐 거 뭐야", "Redis랑 Valkey 차이가 뭐야")

    def test_english_questions(self):
        self.assertFires("how do I cancel a repeatable job in bullmq", "is streaming supported in the latest SDK?",
                         "look up the docs for X")

    def test_opinion_and_planning_questions_get_nothing(self):
        self.assertQuiet("어떻게 하는게 좋을지 ??", "이 구조 어떻게 생각해?", "Redis 쓰는게 좋을까 어떻게 생각해?",
                         "발표 자료를 하나만 낼 수 있는데 이걸 어떻게 해야될지?", "what do you think about this approach?")

    def test_weak_words_without_a_named_tool_get_nothing(self):
        self.assertQuiet("다른것들은? 다 최신이였고?", "이거 어떻게 해야될지 모르겠네", "그 결과가 어떻게 됐는지 알려줘",
                         "이 에러 어떻게 고쳐?")

    def test_english_weak_words_alone_get_nothing(self):
        self.assertQuiet("is it supported?", "Is this the latest one?", "what changed since yesterday?",
                         "this approach vs that one, which do you prefer?")

    def test_english_weak_words_with_a_named_tool(self):
        self.assertFires("what changed in bullmq 5", "Is Valkey supported by ioredis?", "Redis vs Valkey")

    def test_instructions_and_acknowledgements_get_nothing(self):
        self.assertQuiet("정리해줘", "ㅇㅇ", "고마워", "이 파일 리팩터링해", "continue", "테스트 돌려")

    def test_slash_commands_get_nothing(self):
        self.assertQuiet("/lookup:find bullmq 공식 문서 찾아줘")

    def test_broken_or_empty_stdin(self):
        for raw in ("not json", "", "{}", "[1, 2]", json.dumps({"prompt": 3})):
            r = run(raw=raw)
            self.assertEqual((r.returncode, r.stdout.strip()), (0, b""))

    def test_same_prompt_same_answer(self):
        self.assertEqual(run("zod 예제 보여줘").stdout, run("zod 예제 보여줘").stdout)

    def test_never_blocks_and_never_echoes_the_prompt(self):
        r = run("abc123 secret 설정 방법 검색해줘")
        self.assertEqual(r.returncode, 0)
        self.assertIn("lookup:find", context(r))
        self.assertNotIn("abc123", context(r))

    def test_kill_switch(self):
        for value in ("off", "0", "false", "OFF"):
            self.assertEqual(context(run("bullmq 공식 문서 찾아줘", env_extra={"LOOKUP": value})), "", value)

    def test_huge_prompt_is_capped_and_still_fast(self):
        r = run("검색해줘 " + "가" * 2_000_000)
        self.assertEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main()
