# decision-log

[English](README.md) | [한국어](README.ko.md)

결정, 열린 질문, 미뤄 둔 작업, 교훈이 세션 사이에 사라지지 않게 하는 스킬과 템플릿입니다.

- **열린 토픽** — 답변 끝에 아직 정해지지 않은 토픽을 표시하고, 요청하면 작업 노트로 저장합니다. 사용자가 확정이라고 말하기 전에는 확정이라고 쓰지 않습니다.
- **고도화 목록** — 일부러 미룬 기능을 다시 꺼낼 조건(트리거)과 함께 기록합니다.
- **패턴 수집** — 정정과 교훈을 버퍼 파일에 모았다가 사용자가 확인하면 재사용 가능한 패턴 파일로 승격합니다.
- **결정 조회와 변경** — "왜 X로 했지?"에 결정 문서에서 답하고, 확정된 결정은 미리보기를 보여 준 뒤에만 바꿉니다.
- **결정 목차** — 결정 문서의 `INDEX.md`를 만듭니다.

## 설치

```
/plugin marketplace add wjdghtls95/claude-code-kit
/plugin install decision-log@claude-code-kit
```

필요한 것: 세션 시작 안내를 위해 `PATH`에 `python3`가 있어야 합니다(표준 라이브러리만 사용). 스킬은 다른 것이 필요 없습니다.

## 스킬

스킬 이름 앞에는 플러그인 이름이 붙습니다.

| 스킬 | 용도 |
|------|------|
| `/decision-log:topic-tracking` | 열린 토픽 표시, 작업 노트 저장, 확정될 때까지의 생명주기 |
| `/decision-log:enhancement-tracking` | 미룬 작업을 트리거와 함께 기록 |
| `/decision-log:pattern-capture` | 교훈을 버퍼에 모으고 패턴 파일로 승격 |
| `/decision-log:concept-update` | 이미 확정된 결정을 미리보기와 함께 변경 |
| `/decision-log:decision-lookup` | 결정 문서에서 "왜"에 답변 |
| `/decision-log:decision-index` | 결정 폴더의 `INDEX.md` 생성 |

대부분의 스킬은 대화가 설명과 맞으면 스스로 시작되기도 합니다.

## 설정

설정 없이도 동작합니다. 파일 위치를 바꾸려면 프로젝트 루트에 `.claude-kit.json`을 만드세요. 복사본이 `templates/claude-kit.example.json`에 있습니다.

```json
{
  "progress_file": "docs/progress/current.md",
  "decisions_dir": "docs/decisions",
  "enhancement_file": "docs/enhancement-list.md"
}
```

| 키 | 의미 | 기본값 |
|----|------|--------|
| `progress_file` | 작업 노트를 저장할 곳(진행 기록 파일) | `docs/progress/current.md`, `progress.md` 순으로 처음 있는 것 |
| `decisions_dir` | 결정 문서 폴더 | `docs/decisions` |
| `enhancement_file` | 고도화 목록 | `docs/enhancement-list.md` |

진행 기록 파일이 없으면 스킬은 그 단계를 건너뛰고 알려 줍니다. 스스로 만들지는 않습니다. 시작용 템플릿은 `templates/progress.template.md`에 있습니다.

## 세션 시작 안내

세션이 시작되면 작은 훅이 프로젝트의 `.claude/memory/pattern_candidates.md`를 찾습니다. `- [pending]`으로 시작하는 줄이 있으면 Claude가 검토할지 물어보도록 안내합니다. 이 훅은 아무것도 막지 않고 파일을 쓰지도 않습니다.

끄려면 환경 변수 `DECISION_LOG=off`(`0`, `false`, `no`, `disable`, `disabled`도 가능)를 쓰거나 `/plugin disable decision-log`로 플러그인 전체를 끄세요.

## 템플릿과 예시

- `templates/pattern_candidates.md` — 패턴 후보 버퍼 파일
- `templates/PATTERN_INDEX.md` — 비어 있는 패턴 색인
- `templates/progress.template.md` — 작업 노트 구역이 있는 진행 기록 시작용 파일
- `examples/` — 패턴 파일 형식과 파일 이름을 보여 주는 예시 2개

## 개발

```
python3 -m unittest discover -s tests -v
claude plugin validate ./plugins/decision-log --strict
```

## 라이선스

MIT, 저장소의 `LICENSE`를 참고하세요.
