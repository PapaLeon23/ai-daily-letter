#!/usr/bin/env python3
"""홈 화면 시안(preview/index.html) 생성 — 최신 data/*.json 사용."""
import json, glob, os, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORDER = ["ICT/통신", "미디어", "AI/빅데이터", "모빌리티", "로봇", "헬스케어", "소비재", "금융", "제조·에너지", "공공·정책"]
SLUG = {"ICT/통신": "ict", "미디어": "media", "AI/빅데이터": "ai-data", "모빌리티": "mobility", "로봇": "robot",
        "헬스케어": "health", "소비재": "consumer", "금융": "finance", "제조·에너지": "industry", "공공·정책": "policy"}
E = lambda s: html.escape(str(s), quote=True)

files = sorted(glob.glob(os.path.join(ROOT, "data", "*.json")))
d = json.load(open(files[-1], encoding="utf-8"))
y, m, dd = d["date"].split("-")
datestr = f"{int(y)}년 {int(m)}월 {int(dd)}일 ({d['weekday']})"
day = f"../{d['date']}.html"

def first_sentence(p):
    return p["points"][0]

p1 = d["picks"][0]
hero = f"""<a class="hero-main" href="{day}#pick-1">
<span class="kick">Today's Pick 1 · {E(p1['sec'])} · {E(p1['type'])}</span>
<h2>{E(p1['title'])}</h2>
<ul class="pts">{"".join(f"<li>{E(t)}</li>" for t in p1['points'])}</ul>
<p class="why"><b>왜 중요한가</b> {E(p1['why'])}</p>
<span class="meta">{E(p1['region'])} · {E(p1['date'])} · 출처 {len(p1['sources'])}건</span></a>"""
side = "".join(f"""<li><a href="{day}#pick-{i}"><span class="num">{i}</span><span><span class="kick">{E(p['sec'])} · {E(p['type'])}</span><strong>{E(p['title'])}</strong><span class="meta">{E(p['region'])} · {E(p['date'])}</span></span></a></li>""" for i, p in enumerate(d["picks"][1:], 2))

cards = []
for sec in ORDER:
    items = [(p["title"], p["date"], f"{day}#pick-{i}", "Pick") for i, p in enumerate(d["picks"], 1) if p["sec"] == sec]
    items += [(o["title"], o["date"], o["src_url"], "") for o in d["others"] if o["sec"] == sec]
    rows = "".join(f"""<li><a href="{E(u)}">{'<em>Pick</em> ' if t else ''}{E(ti)}</a><span>{E(dt)}</span></li>""" for ti, dt, u, t in items[:3])
    if not rows:
        rows = '<li class="empty">이번 호에는 주요 소식이 없습니다</li>'
    cards.append(f"""<section class="sec-card"><header><a href="#" title="{E(sec)} 분야 페이지(본 제작 시 연결)">{E(sec)}</a><span>{len(items)}건</span></header><ul>{rows}</ul></section>""")

week = "".join(f"""<li><a href="{day}#pick-{i}"><span class="rank">{i}</span><span>{E(p['title'])}<small>{E(p['sec'])} · {E(p['date'])}</small></span></a></li>""" for i, p in enumerate(d["picks"], 1))

search_data = [{"t": p["title"], "s": p["sec"], "y": p["type"], "d": p["date"], "u": f"{day}#pick-{i}", "x": " ".join(p["points"])} for i, p in enumerate(d["picks"], 1)]
search_data += [{"t": o["title"], "s": o["sec"], "y": "", "d": o["date"], "u": o["src_url"], "x": o["summary"]} for o in d["others"]]
nav = "".join(f'<a href="#">{E(s)}</a>' for s in ORDER)
total = len(d["picks"]) + len(d["others"])

page = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>SKTL AI Daily Letter</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@600;700&family=Noto+Sans+KR:wght@400;500;700&display=swap" rel="stylesheet">
<style>
/* VOICE: 조간 경제지 1면 — 단정하고 빠르게 훑어지는 사내 브리핑 홈
   IDEA: 신문 1면: 큰 톱기사 + 우측 단신, 아래 섹션면 미리보기, 하단 주간 랭킹·월간지
   PICTURE: 톱기사 블록(빨간 번호와 굵은 세리프 제목)이 첫 화면의 중심
   COLOUR and TYPE: 흰 바탕, 먹색 #121212, 신문 빨강 #e3120b, 슬레이트 #2e6f8e, 패널 #e3ecf0 / Noto Serif KR + Noto Sans KR
   LAYOUT: 마스트헤드·검색 → 분야 내비 → 톱기사|단신 → 분야 카드 그리드 → 주간 주요 소식|월간 리뷰·지난 호 → 푸터 */
:root{{color-scheme:light dark;--bg:light-dark(#fff,#10191e);--ink:light-dark(#121212,#e9eef1);--mute:light-dark(#5b6670,#9fb0bb);--red:#e3120b;--slate:light-dark(#2e6f8e,#7fb6d2);--panel:light-dark(#eef3f6,#18262e);--rule:light-dark(#dbe2e7,#2a3a44)}}
:root[data-theme=light]{{color-scheme:light}}:root[data-theme=dark]{{color-scheme:dark}}
*{{box-sizing:border-box;min-width:0}}
body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 "Noto Sans KR",system-ui,sans-serif;overflow-x:clip}}
a{{color:inherit;text-decoration:none}}
a:hover strong,a:hover h2,.sec-card li a:hover,.week a:hover span{{text-decoration:underline;text-underline-offset:3px}}
a:focus-visible,input:focus-visible,button:focus-visible{{outline:3px solid var(--slate);outline-offset:2px}}
.wrap{{max-width:1200px;margin:0 auto;padding:0 max(4vw,16px)}}
.notice{{background:var(--panel);font-size:13px;color:var(--mute);text-align:center;padding:6px 12px}}
.top{{display:flex;justify-content:space-between;gap:12px;font-size:13px;color:var(--mute);padding:14px 0 0}}
.mast{{display:flex;align-items:flex-end;justify-content:space-between;gap:20px;flex-wrap:wrap;padding:14px 0 16px;border-bottom:3px solid var(--ink)}}
.logo{{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}}
.logo{{align-items:center!important;gap:14px!important}}.logo img{{height:48px;width:auto;display:block}}
.logo span{{border-left:1.5px solid var(--rule);padding-left:14px}}
@media (prefers-color-scheme:dark){{.logo img{{background:#fff;padding:4px 6px;border-radius:4px}}}}
.logo span{{font:700 clamp(28px,4.4vw,44px)/1 "Noto Serif KR",serif}}
.search{{position:relative;flex:1 1 300px;max-width:420px}}
.search input{{width:100%;height:46px;border:1.5px solid var(--ink);background:var(--bg);color:var(--ink);font:16px "Noto Sans KR",sans-serif;padding:0 46px 0 14px}}
.search button{{position:absolute;right:0;top:0;width:46px;height:46px;border:0;background:var(--ink);color:var(--bg);font-size:18px;cursor:pointer}}
.results{{position:absolute;z-index:5;left:0;right:0;top:50px;background:var(--bg);border:1.5px solid var(--ink);max-height:60vh;overflow:auto;display:none;box-shadow:0 12px 30px rgba(0,0,0,.18)}}
.results.on{{display:block}}
.results a{{display:block;padding:10px 14px;border-top:1px solid var(--rule)}}
.results a:first-child{{border-top:0}}
.results small{{display:block;color:var(--mute);font-size:13px}}
.results p{{margin:0;padding:12px 14px;color:var(--mute);font-size:14px}}
nav.cats{{display:flex;gap:2px;overflow-x:auto;border-bottom:1px solid var(--rule);scrollbar-width:none}}
nav.cats a{{flex:none;padding:12px 14px;font-weight:500;font-size:15px;border-bottom:3px solid transparent}}
nav.cats a:hover{{border-color:var(--red)}}
nav.cats a.hl{{color:var(--red);font-weight:700}}
.label{{display:flex;flex-wrap:wrap;align-items:baseline;justify-content:space-between;gap:4px 12px;margin:34px 0 14px;border-bottom:1px solid var(--ink);padding-bottom:8px}}
.label h3{{margin:0;flex:none;font:700 22px/1.2 "Noto Serif KR",serif}}
.label span{{font-size:14px;color:var(--mute)}}
.label a{{font-size:14px;color:var(--slate)}}
.hero{{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(0,1fr);gap:0;border-bottom:1px solid var(--rule)}}
.hero-main{{display:flex;flex-direction:column;padding:8px 32px 22px 0;border-right:1px solid var(--rule)}}
.hero-main .pts{{margin:0 0 14px;padding-left:1.1em;max-width:62ch}}.hero-main .pts li{{margin:4px 0}}
.hero-main .meta{{margin-top:auto;padding-top:10px}}
.hero-main h2{{font:700 clamp(26px,3.4vw,40px)/1.22 "Noto Serif KR",serif;margin:10px 0 14px;text-wrap:balance}}
.hero-main p{{margin:0 0 12px;max-width:62ch;font-size:17px}}
.hero-main .why{{background:var(--panel);padding:12px 14px;font-size:15px}}
.hero-main .why b{{color:var(--slate);margin-right:6px}}
.kick{{display:block;font-size:13px;font-weight:700;color:var(--red)}}
.meta{{display:block;font-size:13px;color:var(--mute);margin-top:4px}}
.side{{list-style:none;margin:0;padding:0 0 0 28px;display:flex;flex-direction:column}}
.side li{{flex:1;display:flex}}.side li>a{{flex:1;align-content:center}}
.side li{{border-top:1px solid var(--rule)}}
.side li:first-child{{border-top:0}}
.side a{{display:grid;grid-template-columns:30px minmax(0,1fr);gap:8px;padding:14px 0}}
.side .num{{font:700 24px/1 "Noto Serif KR",serif;color:var(--red)}}
.side strong{{display:block;font-size:16px;line-height:1.45;margin-top:2px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:18px}}
.sec-card{{border-top:3px solid var(--ink);padding-top:10px}}
.sec-card header{{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6px}}
.sec-card header a{{font-weight:700;font-size:17px}}
.sec-card header a::after{{content:" ›";color:var(--red)}}
.sec-card header span{{font-size:13px;color:var(--mute)}}
.sec-card ul{{list-style:none;margin:0;padding:0}}
.sec-card li{{display:flex;justify-content:space-between;gap:10px;border-top:1px solid var(--rule);padding:9px 0;font-size:15px;line-height:1.45}}
.sec-card li span{{flex:none;font-size:13px;color:var(--mute)}}
.sec-card em{{font-style:normal;font-size:12px;font-weight:700;color:#fff;background:var(--red);padding:1px 5px;margin-right:4px;vertical-align:1px}}
.sec-card li.empty{{color:var(--mute);font-size:14px}}
.lower{{display:grid;grid-template-columns:minmax(0,1.2fr) minmax(0,1fr);gap:36px}}
.week{{list-style:none;margin:0;padding:0}}
.week a{{display:grid;grid-template-columns:40px minmax(0,1fr);gap:8px;padding:12px 0;border-top:1px solid var(--rule)}}
.week li:first-child a{{border-top:0}}
.rank{{font:700 28px/1 "Noto Serif KR",serif;color:var(--slate)}}
.week li:first-child .rank{{color:var(--red)}}
.week span{{font-weight:500}}
.week small{{display:block;font-weight:400;color:var(--mute);font-size:13px;margin-top:2px}}
.monthly{{background:var(--panel);padding:22px 22px 24px;border-left:4px solid var(--slate)}}
.monthly .kick{{color:var(--slate)}}
.monthly h4{{font:700 24px/1.3 "Noto Serif KR",serif;margin:8px 0 8px}}
.monthly p{{margin:0;font-size:15px;color:var(--mute)}}
.issues{{list-style:none;margin:16px 0 0;padding:0}}
.issues a{{display:flex;justify-content:space-between;gap:10px;padding:11px 0;border-top:1px solid var(--rule);font-size:15px}}
.issues a span{{color:var(--mute);font-size:13px;flex:none}}
footer{{margin-top:48px;border-top:3px solid var(--ink);padding:20px 0 44px;font-size:13px;color:var(--mute);display:flex;flex-wrap:wrap;gap:8px 28px;justify-content:space-between}}
@media(max-width:860px){{.hero,.lower{{grid-template-columns:minmax(0,1fr)}}.hero-main{{border-right:0;padding-right:0;border-bottom:1px solid var(--rule)}}.side{{padding-left:0}}}}
@media(max-width:600px){{.mast{{align-items:stretch}}.search{{max-width:none}}.top{{flex-direction:column;gap:2px}}}}
</style>
</head>
<body>
<div class="notice">홈 화면 시안입니다 · 분야 링크는 본 제작 때 연결</div>
<div class="wrap">
<div class="top"><span>{E(datestr)} · 제{d['issue']}호 발행</span><span>평일 오전 8시(KST) 발행 · 전 세계 AI 도입·활용·규제 소식</span></div>
<header class="mast">
<a class="logo" href="./" aria-label="SKTL AI Daily Letter 홈"><img src="../assets/sktelink-logo.png" alt="SK텔링크" width="104" height="48"><span>AI Daily Letter</span></a>
<form class="search" role="search" id="sf"><input id="q" type="search" placeholder="기사 검색 (예: 로보택시, 규제, 금융)" aria-label="기사 검색" autocomplete="off"><button type="submit" aria-label="검색">⌕</button><div class="results" id="res" aria-live="polite"></div></form>
</header>
<nav class="cats" aria-label="분야">{nav}<a href="#monthly">월간 리뷰</a></nav>

<div class="label"><h3>Today's Pick</h3><span>수집 범위 {E(d['range'])}</span></div>
<div class="hero">{hero}<ol class="side">{side}</ol></div>

<div class="label"><h3>분야별 소식</h3><span>이번 호 {total}건 · 분야를 누르면 해당 분야 전체 기사로 이동</span></div>
<div class="grid">{''.join(cards)}</div>

<div class="lower">
<section><div class="label"><h3>이번 주 주요 소식</h3><span>이번 주 Today's Pick 모음</span></div><ol class="week">{week}</ol></section>
<section>
<div class="label" id="monthly"><h3>월간 리뷰</h3><span>Insight Report 포함</span></div>
<div class="monthly"><span class="kick">AI 월간 리뷰 · 2026년 11월호</span><h4>12월 1일(화) 첫 발행 예정</h4><p>한 달간 가장 임팩트 있었던 흐름을 Insight Report로 깊게 다루고, 10개 분야별 월간 리뷰와 규제 동향을 정리합니다.</p></div>
</section>
</div>

<footer><span>SKTL AI Daily Letter · 팀 내부 공유용 브리핑</span><span>요약은 원문을 바탕으로 새로 작성했으며, 기사 원문의 저작권은 각 매체에 있습니다.</span></footer>
</div>
<script>
{{
const D={json.dumps(search_data, ensure_ascii=False)};
const q=document.getElementById('q'),res=document.getElementById('res'),sf=document.getElementById('sf');
const esc=s=>String(s).replace(/[&<>"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]));
const run=()=>{{const v=q.value.trim().toLowerCase();if(!v){{res.classList.remove('on');res.innerHTML='';return}}
const hit=D.filter(x=>(x.t+' '+x.s+' '+x.y+' '+x.x).toLowerCase().includes(v));
res.innerHTML=hit.length?hit.map(x=>`<a href="${{esc(x.u)}}">${{esc(x.t)}}<small>${{esc(x.s)}}${{x.y?' · '+esc(x.y):''}} · ${{esc(x.d)}}</small></a>`).join(''):'<p>검색 결과가 없습니다</p>';res.classList.add('on')}};
q.addEventListener('input',run);sf.addEventListener('submit',e=>{{e.preventDefault();run()}});
document.addEventListener('click',e=>{{if(!sf.contains(e.target))res.classList.remove('on')}});
document.addEventListener('keydown',e=>{{if(e.key==='Escape')res.classList.remove('on')}});
}}
</script>
</body>
</html>
"""
os.makedirs(os.path.join(ROOT, "preview"), exist_ok=True)
open(os.path.join(ROOT, "preview", "index.html"), "w", encoding="utf-8").write(page)
print("preview/index.html written")
