# AI Daily Letter

평일 오전 8시(KST) 발행되는 AI 도입·활용·규제 브리핑의 상세 페이지 사이트입니다.
사이트: https://papaleon23.github.io/ai-daily-letter/

## 구조
- `data/YYYY-MM-DD.json` — 호별 데이터 (Today's Pick 5건 + 분야별 소식)
- `YYYY-MM-DD.html` — `scripts/build.py`가 JSON에서 생성하는 호별 상세 페이지
- `monthly/YYYY-MM.html` — 월간 간행물 (Insight Report 포함)
- `index.html` — 발행 목록 (build.py가 생성)

## 발행
1. `data/`에 새 JSON 추가 (기존 파일 형식 참고)
2. `python3 scripts/build.py`
3. commit & push → GitHub Pages 자동 반영
