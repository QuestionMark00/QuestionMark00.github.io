# QuestionMark

직접 만든 게임과 개발 중인 임시 버전을 브라우저에서 바로 플레이할 수 있는 사이트입니다.
GitHub Pages로 배포되며, 빌드 도구나 외부 서비스 없이 정적 파일만으로 돌아갑니다.

## 구조

| 경로 | 내용 |
|---|---|
| `index.html` | 게임 목록 (`games.json`을 읽어서 그림) |
| `game.html?g=<slug>` | 게임별 소개 · 조작 · 버전 목록 |
| `games.json` | 게임과 버전 정보 전부. 버전은 최신순, 첫 번째가 "최신" |
| `games/<slug>/play/` | 최신 정식 버전 (고정 주소 - 웹 저장이 다음 버전으로 이어짐) |
| `games/<slug>/<버전 id>/` | 그 밖의 버전, Unity WebGL 빌드 그대로 (`index.html` + `Build/`) |
| `games/<slug>/cover.png` 등 | 표지 · 스크린샷 |
| `tools/add_build.py` | 빌드 추가/삭제 + `games.json` 갱신 |

## 새 버전 올리기

```
python tools/add_build.py prismix <WebGL 빌드 폴더> --id 2026-10-20 --label "0.2 테스트판" --notes "바뀐 점 한 줄" --temporary
git add -A && git commit -m "Add Prismix 0.2 test build" && git push
```

- `--temporary`를 붙이면 "임시 버전" 표시가 붙습니다. 정식 버전이면 빼세요.
- 정식 버전은 `games/<slug>/play/`에 들어가고, `games.json`의 `"play"`가 그 버전을 가리킵니다. 전에 `play/`에
  있던 버전은 자기 `games/<slug>/<id>/` 폴더로 옮겨집니다. Unity 웹 빌드는 저장(PlayerPrefs)을 빌드 폴더
  주소마다 따로 두므로, 최신 정식 버전을 늘 같은 주소에 두어야 웹 진행이 다음 버전으로 이어집니다.
  임시 버전은 자기 폴더에 들어가고 `play/`는 그대로입니다.
- 새 게임은 같은 명령에 `--title "제목" --tagline "한 줄 소개"`를 더하면 카드가 생깁니다.
  그다음 `games.json`에서 설명 · 조작 · 표지 · 플랫폼을 채웁니다.
- 오래된 임시 버전 정리: `python tools/add_build.py prismix --remove 2026-10-20`

## 한도

- 파일 하나 100 MB 미만 (GitHub 제한), 사이트 전체 1 GB 권장 (Pages 제한).
  Prismix 빌드 하나가 약 20 MB이므로, 임시 버전이 쌓이면 가끔 정리합니다.
- Unity WebGL 빌드는 gzip + decompression fallback 설정이어야 합니다
  (Pages는 Content-Encoding 헤더를 못 붙임). Prismix의 `PRISM/Build Web Player`가 이미 그렇게 빌드합니다.

## 개인정보

사이트와 커밋 기록에는 실명 · 학교 · 개인 이메일을 넣지 않습니다.
이 저장소는 로컬 git 설정으로 `QuestionMark <noreply@questionmark.invalid>`로 커밋합니다.
