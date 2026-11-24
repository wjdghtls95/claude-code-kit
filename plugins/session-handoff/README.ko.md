# session-handoff

[English](README.md) | [한국어](README.ko.md)

작업을 한 세션에서 다음 세션으로 넘기기 위한 스킬입니다. 모두 진행 기록 파일을 기준으로 동작합니다.

- **wrap-up** — 세션을 끝내기 전에 진행 기록을 맞추고, 한 일을 요약하고, 다음 세션의 첫 작업을 알려 주고, git 상태를 읽기 전용으로 보고합니다.
- **resume** — 돌아왔을 때 최근 진행 기록과 git 상태를 보여 주고, 끝나지 않은 작업을 짚고, 다음에 무엇을 할지 묻습니다.
- **next-task-check** — "다음 할 일은?"에 답합니다. PR 상태를 먼저 확인하고, 진행 기록을 읽고, 사용자만 할 수 있는 일과 Claude가 다음에 할 수 있는 일을 나눠 보여 줍니다.

## 설치

```
/plugin marketplace add wjdghtls95/claude-code-kit
/plugin install session-handoff@claude-code-kit
```

다른 것은 필요 없습니다. 훅이 없고 `python3`도 필요하지 않습니다. GitHub CLI `gh`가 있으면 씁니다.

## 스킬

스킬 이름 앞에는 플러그인 이름이 붙습니다.

| 스킬 | 용도 |
|------|------|
| `/session-handoff:wrap-up` | 세션 마무리 |
| `/session-handoff:resume` | 쉬었다가 다시 시작 |
| `/session-handoff:next-task-check` | 다음에 할 일 정하기 |

대부분의 스킬은 대화가 설명과 맞으면 스스로 시작되기도 합니다.

## 프로젝트에 하는 일

- `wrap-up`은 진행 기록 파일과, 새 규칙이나 스킬을 만들었다면 프로젝트의 그 목록 파일을 고치고 무엇을 바꿨는지 한 줄로 알립니다. git은 읽기만 하고, 푸시나 머지나 PR 생성은 하지 않습니다(그건 git 워크플로의 일). 진행 기록이 아주 길면 오래된 항목을 보관 파일로 옮기기 전에 먼저 묻습니다.
- `resume`은 읽기만 합니다. 브랜치를 바꾸거나 pull하지 않습니다.
- `next-task-check`는 `gh pr list`(읽기 전용)를 실행하고, 머지된 PR이 있으면 진행 기록을 고치고 그렇게 말합니다.

## 설정

필요한 설정은 없습니다. 진행 기록 파일은 `.claude-kit.json`의 `progress_file`, `docs/progress/current.md`, `progress.md` 순서로 찾습니다. 없으면 그 단계를 건너뛰고 알립니다. 시작용 템플릿은 `templates/progress.template.md`에 있습니다.

## 개발

```
python3 -m unittest discover -s tests -v
claude plugin validate ./plugins/session-handoff --strict
```

## 라이선스

MIT, 저장소의 `LICENSE`를 참고하세요.
