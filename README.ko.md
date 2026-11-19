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

플러그인은 하나씩 추가됩니다.

## 필요한 것

훅이 들어 있는 플러그인은 `PATH`에 `python3`가 필요합니다. 훅은 표준 라이브러리만 사용합니다.

## 개발

```
python3 -m unittest discover -s tests -v
claude plugin validate . --strict
claude plugin validate ./plugins/quality-guard --strict
```

## 보안

취약점은 공개하지 말고 비공개로 알려 주세요. [SECURITY.md](SECURITY.md)를 참고하세요.

## 라이선스

MIT, [LICENSE](LICENSE)를 참고하세요.
