# SKTL AI Daily Letter

평일 오전 8시(KST) 발행되는 전 세계 AI 도입·활용·규제 브리핑 사이트입니다.
사이트: https://papaleon23.github.io/ai-daily-letter/

## 구조
- `data/YYYY-MM-DD.json` — 호별 데이터 (Today's Pick 5건 + 분야별 소식). 형식은 기존 파일 참고.
  - picks[]: sec, type, region, date(M/D), title, points[3], why, sources[{name,url}]
  - others[]: sec, type, region, date(M/D), title, summary(1문장), detail(2~3문장), src_name, src_url, (선택) more_sources[{name,url}]
  - sec 값(정확히): ICT/통신(위성통신·우주 인프라 포함), 미디어, AI/빅데이터, 모빌리티, 로봇, 헬스케어, 소비재, 금융, 제조·에너지, 공공·정책
  - (상세 페이지용, picks·others 공통) subtitle(소제목 1줄), body[](상세 본문 문단: Pick 4~6개, 분야별 2~3개), implications[](시사점 1~2문단)
    → 목록 화면은 points/why/summary만 쓰고, 기사 페이지는 subtitle/body/implications를 보여준다(목록과 같은 문장을 반복하지 말 것)
  - numbers[] (선택, 3~4개): value(예: "127%"), label(한 줄 설명), ref(연결 기사: Pick은 "p1"~"p5", 분야별은 "01"~), source(수치 출처 기관)
  - type 값: 도입, 활용, 결합·제휴, 인수·투자, 규제·정책, 기술·연구
- `scripts/build.py` — 아래 전부를 생성
  - `index.html` 홈, `search.html` + `search-index.json` 검색
  - `sectors/<slug>.html` 분야 페이지 10개
  - `articles/<YYYY-MM-DD>-p1..p5.html` Today's Pick 기사, `articles/<YYYY-MM-DD>-01..NN.html` 분야별 소식 기사
  - `YYYY-MM-DD.html` 호별 Daily Letter
  - `letters.html` 지난 호 목록
  - `monthly/index.html` 월간 리뷰 목록 (`monthly/YYYY-MM.html`은 월간 작업이 직접 작성, 스타일은 `assets/site.css` 사용)
- `assets/site.css` 공통 스타일, `assets/sktelink-logo.png` CI

## 발행 절차
1. `data/`에 새 JSON 추가
2. `python3 scripts/build.py`
3. commit & push → GitHub Pages 자동 반영
