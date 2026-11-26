# quality-guard

[English](README.md) | [한국어](README.ko.md)

Claude가 코드를 다룰 때 규율을 지키게 하는 훅과 스킬입니다.

- **티어 선언** — Claude는 소스 파일을 수정하기 전에 답변에서 티어(`[A]`, `[B]`, `[C]`)를 먼저 선언해야 합니다. 선언이 없으면 훅이 수정을 막습니다.
- **6라운드 프로토콜** — 새 기능, 버그 수정, 설계 변경(`[A]`)에서는 체크리스트(의도, 반론, 참고 사례, 단순성, 지속성, 테스트 용이성)를 거치고, 코드를 쓰기 전에 사용자의 확인을 기다립니다.
- **테스트 먼저** — 선택 기능입니다. 테스트 파일이 없으면 새 소스 파일을 만들지 못하게 막습니다.
- **스킬** — 위 규칙의 본문입니다. 필요할 때 불러옵니다.

> **주의: 이 플러그인은 파일 수정을 막을 수 있습니다.** Claude가 티어를 선언하지 않고 소스 파일을 수정하면 훅이 수정을 거부하고 해야 할 일을 알려 줍니다. 이것이 플러그인의 목적이지만, 모르고 쓰면 오류처럼 보일 수 있습니다. [끄는 방법](#끄는-방법)을 참고하세요.

## 설치

```
/plugin marketplace add wjdghtls95/claude-code-kit
/plugin install quality-guard@claude-code-kit
```

필요한 것: `PATH`에 `python3`가 있어야 합니다(표준 라이브러리만 사용, 따로 설치할 것 없음). Windows에서는 `python3`가 Python 3을 가리키는지 확인하세요.

## 티어

| 티어 | 언제 | Claude가 하는 일 |
|------|------|------------------|
| `[A]` | 새 기능, 버그 수정, 설계 변경 | 6라운드를 거치고, 5줄 요약을 보여 주고, 확인을 기다린 뒤, 코드보다 테스트를 먼저 씁니다 |
| `[B]` | 리뷰 반영, assertion 변경, 상수 이름 변경 | 축약 점검: 의도, 위험, 나머지를 생략하는 이유 (3줄) |
| `[C]` | 문서와 메타 파일 | 한 줄 이유만, 라운드 없음 |

선언은 한 차례(사용자 메시지 한 번에 대한 작업) 전체에 적용되므로 한 번 선언하면 여러 번 수정할 수 있습니다. `[A]` 계획을 확인해 주시면 그 확인이 새 차례를 시작하므로, Claude는 다음 답변에서 티어를 다시 선언합니다.

## 스킬

스킬 이름 앞에는 플러그인 이름이 붙습니다.

| 스킬 | 용도 |
|------|------|
| `/quality-guard:code-generation-protocol` | 티어, 6라운드, 확인 단계 |
| `/quality-guard:tdd-rule` | 테스트 목록, Red, Green, Refactor, 읽기 쉬운 테스트, 테스트가 코드를 실제로 지키는지 보는 변이 확인 |
| `/quality-guard:coding-behavior-guidelines` | 코딩 전에 생각하기, 단순성, 최소 변경 |
| `/quality-guard:code-consistency` | 패턴 변경 알리기, 세 번째 중복 규칙 |
| `/quality-guard:code-pitfalls` | 실제 리뷰에서 나온 버그 패턴 |
| `/quality-guard:code-standard` | ESLint가 검사하는 TypeScript 코드 기준(설정 파일 포함), 린트로 못 보는 리뷰 기준, 동작을 바꾸지 않는 리팩터링 절차 |
| `/quality-guard:project-structure` | 폴더 구조를 정하는 순서와 기본값, 의존 방향을 린트가 지키게 하는 방법 |

세션이 시작될 때마다 티어 규칙을 짧게 상기시키는 안내가 추가됩니다.

스킬과 함께 파일 두 개가 들어 있습니다.

- `templates/eslint-standard.js`: `code-standard`의 ESLint 설정(flat config)입니다. TypeScript 프로젝트에 복사하고 `eslint @eslint/js typescript-eslint @stylistic/eslint-plugin`을 설치합니다(ESLint 9, typescript-eslint 8, @stylistic 5로 시험함).
- `scripts/mutation_check.py`: `.mutations.json` 목록대로 소스를 한 곳씩 일부러 망가뜨리고 테스트를 돌린 뒤 파일을 되돌립니다. 도는 동안 소스 파일이 바뀌고, 되돌릴 때까지 파일 옆에 `.mutation-backup` 사본을 둡니다(Ctrl+C나 일반 종료는 파일을 되돌리고, 강제 종료 뒤에는 사본으로 되돌릴 때까지 다음 실행을 거부합니다). 자세한 내용은 `tdd-rule` 스킬에 있습니다.

## 설정

설정 없이도 동작합니다. 기본값을 바꾸려면 프로젝트 루트에 `.quality-guard.json`을 만드세요.

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

| 키 | 의미 |
|----|------|
| `source_extensions` | 티어 선언이 필요한 파일. 기본값은 흔한 코드 확장자 |
| `skip_patterns` | 두 훅 모두 검사하지 않는 경로. 패턴은 폴더나 파일 이름의 앞부분(접두) 일치입니다. `dist/`는 `pkg/dist/a.js`와 일치하지만 `redist/a.js`와는 일치하지 않고, `foo`는 `foobar/a.ts`와도 일치합니다. 기본값은 `node_modules/`, `dist/`, `build/`, `.git/`, 잠금 파일 등 |
| `tdd.mappings` | 정규식 `source` → `test` 경로 템플릿(이름 있는 그룹이 `{name}`이 됨). 처음으로 적용되는 매핑이 결정합니다. `source`가 일치하고, `content_regex`가 있으면 새 파일 내용도 일치해야 적용됩니다. 이 목록이 비어 있지 않을 때만 테스트 먼저 훅이 동작 |
| `tdd.mappings[].content_regex` | 선택. 새 파일 내용이 일치할 때만 적용 |
| `tdd.test_file_patterns` | 선택. 테스트 파일로 보는 정규식(이런 파일은 막지 않음) |
| `disable` | 선택. `"tier_guard"`와 `"tdd_guard"` 중 끄고 싶은 훅 이름의 목록 |

잘못된 설정(깨진 JSON, 틀린 값 타입, 잘못된 정규식)은 안내만 출력하고 무시하며, 그 설정에는 기본값을 씁니다.

## 끄는 방법

| 방법 | 효과 |
|------|------|
| 환경 변수 `QUALITY_GUARD=off` | 훅 둘과 세션 안내가 모두 아무 일도 하지 않음 (`0`, `false`, `no`, `disable`, `disabled`도 가능) |
| `.quality-guard.json`의 `"disable": ["tier_guard"]` | 훅 하나만 끔(`tier_guard`를 끄면 세션 시작 안내도 조용해짐) |
| 환경 변수 `QUALITY_GUARD_TAIL_BYTES` | 고급: 티어 검사가 세션 대화 기록의 끝에서 읽는 바이트 수(기본 2,000,000, 최대 50,000,000) |
| `/plugin disable quality-guard` | 플러그인 전체를 끔 |
| 플러그인 삭제 | 남는 것이 없음, 이 플러그인은 데이터를 저장하지 않음 (`mutation_check.py`는 도는 동안에만 소스 파일을 바꿈) |

## 티어 검사가 하는 일과 못 하는 일

훅은 세션 대화 기록을 읽어 사용자의 마지막 메시지까지 거슬러 올라가고, 그 이후 Claude의 글에 `[A]`, `[B]`, `[C]`가 있는지 찾습니다. 일부러 너그럽게 만들었습니다.

- **이번 차례의 Claude 글이 보이는데 선언이 없을 때만 막습니다.**
- Claude Code는 응답을 도구가 실행된 뒤에야 대화 기록에 저장합니다. 그래서 훅은 **수정과 같은 응답 안에 있는 선언을 볼 수 없습니다.** 아직 보이는 글이 없으면(보통 한 차례의 첫 수정) 수정을 허용하고 안내만 출력합니다.
- 여러 단계로 이어지는 차례에서는 **불필요한 차단이 한 번** 생길 수 있습니다. Claude가 수정과 같은 응답에서 티어를 선언했는데, 훅은 그보다 앞의 선언 없는 글만 보는 경우입니다. Claude가 다시 시도하면 그때는 선언이 저장되어 보입니다. 재시도는 항상 도구 결과 뒤에 오고 그 시점에는 앞 응답이 저장되어 있으므로 무한히 반복되지는 않습니다.
- 기록이 없거나 읽을 수 없을 때도 수정을 허용합니다. 가끔 놓치는 가드가 사용자를 가두는 가드보다 낫기 때문입니다.
- 이런 한계 때문에 이 훅은 보안 경계가 아니라 **환기 장치**입니다. 세션이 시작될 때 추가되는 안내(Claude가 스스로 티어를 선언하게 함)가 대부분의 역할을 하고, 훅은 같은 차례의 이후 수정을 점검합니다.
- 이전 차례에서 한 선언은 인정하지 않습니다.

## 개발

```
python3 -m unittest discover -s tests -v
claude plugin validate ./plugins/quality-guard --strict
```

## 라이선스와 출처

MIT, 저장소의 `LICENSE`를 참고하세요. `coding-behavior-guidelines` 스킬은 Andrej Karpathy가 공개한 LLM 코딩 함정에 대한 관찰에서 파생되었습니다.
