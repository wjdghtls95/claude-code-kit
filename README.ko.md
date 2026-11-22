# claude-code-kit

[English](README.md) | [한국어](README.ko.md)

일상적인 개발을 위한 가드레일과 워크플로를 담은 작은 Claude Code 플러그인 모음입니다. 각 플러그인은 `plugins/` 아래 자기 폴더에 있고 따로 설치할 수 있습니다.

## 설치

```
/plugin marketplace add wjdghtls95/claude-code-kit
/plugin install <플러그인 이름>@claude-code-kit
```

## 플러그인

| 플러그인 | 하는 일 | 문서 |
|----------|---------|------|
| `quality-guard` | 소스 파일을 수정하기 전에 티어를 선언하게 하고, 위험한 변경에는 6라운드 프로토콜을 거치게 하고, 테스트를 먼저 쓰게 합니다 | [README](plugins/quality-guard/README.ko.md) |
| `code-review` | 알맞은 리뷰 수준을 고르고, 네 리뷰어의 PR 리뷰를 돌리고, UI가 어떻게 보이는지 검사하고, 프로젝트 REVIEW.md를 관리합니다. 읽기 전용 리뷰어 에이전트 포함 | [README](plugins/code-review/README.ko.md) |
| `decision-log` | 결정, 열린 토픽, 미룬 작업, 교훈이 사라지지 않게 합니다: 토픽 추적, 고도화 목록, 패턴 수집, 결정 조회 | [README](plugins/decision-log/README.ko.md) |

플러그인은 하나씩 추가됩니다.

## 공통 설정

프로젝트 파일을 읽거나 쓰는 플러그인은 프로젝트 루트의 선택 파일 `.claude-kit.json`을 찾습니다. 모든 키는 선택이고, 파일이 없어도 플러그인은 동작합니다.

```json
{
  "progress_file": "docs/progress/current.md",
  "decisions_dir": "docs/decisions",
  "enhancement_file": "docs/enhancement-list.md",
  "design_system_file": "docs/DESIGN_SYSTEM.md"
}
```

스킬이 읽어야 할 파일이 없으면 그 단계를 건너뛰고 한 줄로 알린 뒤 계속합니다. 스킬은 자기 일에 해당하는 파일(예: 고도화 목록, 패턴 파일, `INDEX.md`, `REVIEW.md`, 요청받은 진행 기록 항목)만 쓰고, 무엇을 어디에 썼는지 한 줄로 알립니다. 진행 기록 파일은 대신 만들어 주지 않습니다.

## 필요한 것

훅이 들어 있는 플러그인은 `PATH`에 `python3`가 필요합니다. 훅은 표준 라이브러리만 사용합니다.

## 개발

```
python3 -m unittest discover -s tests -v
claude plugin validate . --strict
claude plugin validate ./plugins/quality-guard --strict
claude plugin validate ./plugins/decision-log --strict
claude plugin validate ./plugins/code-review --strict
```

## 보안

취약점은 공개하지 말고 비공개로 알려 주세요. [SECURITY.md](SECURITY.md)를 참고하세요.

## 라이선스

MIT, [LICENSE](LICENSE)를 참고하세요.
