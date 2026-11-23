# git-workflow

[English](README.md) | [한국어](README.ko.md)

마지막 수정부터 머지된 PR까지, git 전달 과정을 위한 스킬입니다.

- **ship** — 커밋(메시지는 확인받음), 푸시, PR 생성을 한 번에 하고 변경에 필요한 리뷰 수준을 고릅니다.
- **land** — 리뷰가 끝난 PR을 확인받은 뒤 squash 머지하고, 브랜치를 지우고, 기본 브랜치로 돌아옵니다.
- **브랜치 점검** — 열린 PR, 남은 로컬과 원격 브랜치, 실패한 CI, 규칙을 어긴 커밋, 푸시하지 않은 커밋을 보여 줍니다.
- **안전한 git 규칙** — 기본 브랜치 동기화, 작업 하나에 브랜치 하나, 머지 대신 rebase, 승인 없는 force-push 금지, 충돌 자동 해결 금지.
- **ship 알림** — 코딩 작업이 끝나면 답변 끝에 한 줄로 알려 줍니다.
- **규칙** — 브랜치 이름, 커밋 메시지 형식과 scope, 머지 방식, PR 체크리스트의 기본값입니다. 기본값이므로 프로젝트 자체 규칙이 우선입니다.

## 설치

```
/plugin marketplace add wjdghtls95/claude-code-kit
/plugin install git-workflow@claude-code-kit
```

필요한 것: `git`, 그리고 PR 단계를 위한 GitHub CLI `gh`(로그인된 상태). 이 플러그인에는 훅이 없고 `python3`도 필요하지 않습니다.

## 스킬

스킬 이름 앞에는 플러그인 이름이 붙습니다.

| 스킬 | 용도 |
|------|------|
| `/git-workflow:ship` | 커밋, 푸시, PR 생성. 인자: 따옴표로 감싼 메시지 또는 `--no-review` |
| `/git-workflow:land` | PR 머지, 브랜치 삭제, 기본 브랜치로 복귀 |
| `/git-workflow:pr-check` | 열린 PR, 남은 브랜치, CI, 규칙 점검 |
| `/git-workflow:git-rules` | 안전한 일상 git 규칙 |
| `/git-workflow:ship-reminder` | 작업 완료 알림 |
| `/git-workflow:git-conventions` | 브랜치 이름, 커밋 형식, 머지 방식 |

대부분의 스킬은 대화가 설명과 맞으면 스스로 시작되기도 합니다.

## 저장소에 하는 일

- `ship`은 파일 이름을 지정한 `git add`(`git add -A`는 쓰지 않음), `git commit`, `git push`, `gh pr create`를 실행하고, 직접 만든 커밋 메시지는 먼저 확인을 받습니다(직접 넘긴 메시지는 그대로 씁니다).
- `land`는 `gh pr merge --squash --delete-branch`, `git checkout`, `git pull`을 실행하고, 먼저 확인을 받습니다.
- `pr-check`는 `git fetch --prune`(원격 추적 참조만 갱신)을 실행하고 PR과 브랜치 상태를 읽습니다. 브랜치는 승인 뒤에만 지우고, 진행 기록 파일에는 동의할 때만 한 줄을 추가합니다.
- 스킬은 기본 브랜치에 직접 푸시하지 않습니다. force-push는 매번 승인이 필요합니다.

## 설정

필요한 설정은 없습니다. 스킬은 저장소의 기본 브랜치를 알아냅니다. 진행 기록 파일(`docs/progress/current.md`, `progress.md`, 또는 `.claude-kit.json`의 `progress_file`)이 있으면 `pr-check`가 한 줄을 추가합니다. 시작용 템플릿은 `templates/progress.template.md`에 있습니다.

## 개발

```
python3 -m unittest discover -s tests -v
claude plugin validate ./plugins/git-workflow --strict
```

## 라이선스

MIT, 저장소의 `LICENSE`를 참고하세요.
