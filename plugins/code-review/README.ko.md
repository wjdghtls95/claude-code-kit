# code-review

[English](README.md) | [한국어](README.ko.md)

코드 리뷰를 위한 스킬과 리뷰어 에이전트입니다.

- **리뷰 종류 추천** — 변경의 크기와 성격을 보고 알맞은 리뷰 수준(생략, 표준, 심층)을 추천하고, 어떤 지적은 바로 고치고 어떤 지적은 먼저 물을지 알려 줍니다.
- **PR 리뷰** — 네 명의 독립 리뷰어(아키텍처, 백엔드와 AI, 프런트엔드, 보안)가 병렬로 검토하고 결과를 하나의 보고서로 합칩니다. 모든 지적은 AUTO-FIX, USE-EXISTING, ASK, FUTURE-RISK 중 하나입니다. 지적은 file:line 근거와 확신도를 적고, 미래 위험은 대신 발생 조건을 적습니다.
- **디자인 리뷰** — UI 변경이 브라우저에서 실제로 어떻게 보이는지 데스크톱과 휴대폰 폭의 스크린샷으로 검사합니다.
- **리뷰 후속 처리** — 해결된 지적을 마무리합니다. 진행 기록을 체크하고, 해결과 결과를 적고, 수정이 버그만 닫는 것이 아니라 코드를 낫게 만드는지 확인합니다.
- **REVIEW.md** — 리뷰 명령이 읽는 파일의 템플릿과 스킬. 치명적인 것, 사소한 것, 의도된 것, 무시할 것의 구역이 있습니다.
- **리뷰어 에이전트** — 읽기 전용인 서버, 프런트엔드, AI, 인프라 리뷰어와 체크리스트.

## 설치

```
/plugin marketplace add wjdghtls95/claude-code-kit
/plugin install code-review@claude-code-kit
```

다른 것은 필요 없습니다. 이 플러그인에는 훅이 없고 `python3`도 필요하지 않습니다.

## 스킬

스킬 이름 앞에는 플러그인 이름이 붙습니다.

| 스킬 | 용도 |
|------|------|
| `/code-review:review-routing` | 변경에 필요한 리뷰, 지적 처리 방법 |
| `/code-review:pr-review` | 네 리뷰어의 PR 리뷰. 선택 인자: `arch`, `backend`, `frontend`, `security`, `all` |
| `/code-review:design-review` | 바뀐 화면의 시각 품질 |
| `/code-review:review-followup` | 해결된 지적의 마무리 |
| `/code-review:review-checklist` | 프로젝트의 `REVIEW.md` 생성과 갱신 |

## 에이전트

`reviewer-server`, `reviewer-front`, `reviewer-ai`, `reviewer-infra`. 한 분야를 집중해서 보는 별도의 역할 리뷰어이고 Critical, Warning, Suggestion으로 보고합니다. `pr-review` 스킬은 자체 네 역할을 씁니다. 파일을 읽을 수만 있어서(Read, Grep, Glob) 코드를 바꾸지 못합니다. 예를 들어 "reviewer-server로 리뷰해줘"처럼 요청하세요.

## 실행하는 것

스킬이 실행하는 명령은 본문에 모두 보입니다. `pr-review`의 `git` 명령, 죽은 코드 점검용 `npx knip`과 `vulture`, 요청 시 `npm audit`이나 `pip check`, `design-review`의 `npx playwright`와 프로젝트 자체의 개발 서버 명령입니다. `npx`는 처음에 패키지를 내려받을 수 있습니다. 리뷰 자체는 코드를 고치지 않습니다.

## 설정

설정 없이도 동작합니다. 프로젝트 루트의 `.claude-kit.json`에 선택 키를 둘 수 있습니다.

| 키 | 의미 | 기본값 |
|----|------|--------|
| `progress_file` | `review-followup`이 쓰는 진행 기록 파일 | `docs/progress/current.md`, `progress.md` 순으로 처음 있는 것 |
| `design_system_file` | `design-review`가 쓰는 디자인 시스템 문서 | 프로젝트에서 처음 찾은 `DESIGN_SYSTEM.md` |

파일이 없으면 스킬은 그 단계를 건너뛰고 한 줄로 알립니다.

## 템플릿

- `templates/REVIEW.template.md` — 저장소 루트에 복사해서 프로젝트에 맞게 고치는 범용 `REVIEW.md`
- `templates/progress.template.md` — `review-followup`을 위한 진행 기록 시작용 파일

## 개발

```
python3 -m unittest discover -s tests -v
claude plugin validate ./plugins/code-review --strict
```

## 라이선스

MIT, 저장소의 `LICENSE`를 참고하세요.
