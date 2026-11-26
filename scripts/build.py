#!/usr/bin/env python3
"""AI Link (SK텔링크 AI 소식 포털) 사이트 빌더.

python3 scripts/build.py 한 번으로 data/*.json 전체에서 아래를 생성한다.
  index.html                       홈
  search.html, search-index.json   검색
  sectors/<slug>.html              분야 페이지 10개
  articles/<id>.html               기사(소식 1건)별 페이지
  YYYY-MM-DD.html                  호별 Daily Letter (#pick-1..5 / #sectors 유지)
  monthly/index.html               월간 리뷰 목록 (monthly/YYYY-MM.html 은 월간 작업이 직접 작성)
"""
import json, glob, os, re, html, datetime, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_NAME = "AI Link"
SECTORS = [("ICT/통신", "ict"), ("미디어", "media"), ("AI/빅데이터", "ai-data"), ("모빌리티", "mobility"),
           ("로봇", "robot"), ("헬스케어", "health"), ("소비재", "consumer"), ("금융", "finance"),
           ("제조·에너지", "industry"), ("공공·정책", "policy")]
SLUG = dict(SECTORS)
TYPES = ["도입", "활용", "결합·제휴", "인수·투자", "규제·정책", "기술·연구"]
WD = "월화수목금토일"
CSS_VER = hashlib.md5(open(os.path.join(ROOT, "assets", "site.css"), "rb").read()).hexdigest()[:8]
E = lambda s: html.escape(str(s), quote=True)


def kdate(iso, wd=True):
    y, m, d = map(int, iso.split("-"))
    s = f"{y}년 {m}월 {d}일"
    return s + f" ({WD[datetime.date(y, m, d).weekday()]})" if wd else s


def short(iso):
    return iso.replace("-", ".")


def md(iso):
    return f"{int(iso[5:7])}/{int(iso[8:10])}"


def tagline(a):
    return " · ".join(x for x in [a["sec"], a["type"], a["region"]] if x)


# ---------- data ----------
def to_iso(year, mdstr):
    m, d = mdstr.split("/")
    return f"{year}-{int(m):02d}-{int(d):02d}"


def load():
    issues, arts = [], []
    for f in sorted(glob.glob(os.path.join(ROOT, "data", "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        y = d["date"][:4]
        d["arts"] = []
        for i, p in enumerate(d["picks"], 1):
            d["arts"].append(dict(id=f"{d['date']}-p{i}", issue=d["issue"], idate=d["date"], pick=i, sec=p["sec"],
                                  type=p.get("type", ""), region=p.get("region", ""), title=p["title"],
                                  points=p.get("points", []), why=p.get("why", ""), detail="",
                                  summary=(p.get("points") or [""])[0], sources=p.get("sources", []),
                                  subtitle=p.get("subtitle", ""), body=p.get("body", []), impl=p.get("implications", []),
                                  date=to_iso(y, p["date"])))
        for j, o in enumerate(d["others"], 1):
            d["arts"].append(dict(id=f"{d['date']}-{j:02d}", issue=d["issue"], idate=d["date"], pick=0, sec=o["sec"],
                                  type=o.get("type", ""), region=o.get("region", ""), title=o["title"], points=[],
                                  why="", detail=o.get("detail", ""), summary=o["summary"],
                                  sources=[{"name": o["src_name"], "url": o["src_url"]}] + o.get("more_sources", []),
                                  subtitle=o.get("subtitle", ""), body=o.get("body", []), impl=o.get("implications", []),
                                  date=to_iso(y, o["date"])))
        arts += d["arts"]
        issues.append(d)
    issues.sort(key=lambda x: x["date"])
    arts.sort(key=lambda a: (a["date"], a["idate"], 1 if a["pick"] else 0, -a["pick"]), reverse=True)
    return issues, arts


# ---------- layout ----------
def head(title, R):
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>{E(title)}</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@600;700&family=Noto+Sans+KR:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{R}assets/site.css?v={CSS_VER}">
</head>
<body>
<div class="wrap">"""


def header(R, latest, current=None):
    nav = "".join(f'<a href="{R}sectors/{s}.html"{" aria-current=page" if current == n else ""}>{E(n)}</a>' for n, s in SECTORS)
    nav += f'<a href="{R}monthly/"{" aria-current=page" if current == "monthly" else ""}>월간 리뷰</a>'
    return f"""
<div class="top"><span><b id="today">{E(kdate(latest['date']))}</b> <span class="latest">· 최신 <a class="u" href="{R}{latest['date']}.html">제{latest['issue']}호</a> {md(latest['date'])} 발행</span></span></div>
<header class="mast">
<a class="logo" href="{R}index.html" aria-label="{SITE_NAME} 홈"><img src="{R}assets/sktelink-logo.png" alt="SK텔링크" width="96" height="46"><span>AI Link</span></a>
<form class="search" role="search" action="{R}search.html" method="get" data-root="{R}"><input name="q" type="search" placeholder="기사 검색 (예: 로보택시, 규제, 금융)" aria-label="기사 검색" autocomplete="off"><button type="submit">검색</button><div class="drop" aria-live="polite"></div></form>
</header>
<nav class="cats" aria-label="분야">{nav}</nav>"""


SEARCH_JS = """<script>
{
const td=document.getElementById('today');
if(td){try{const p=new Intl.DateTimeFormat('ko-KR',{timeZone:'Asia/Seoul',year:'numeric',month:'numeric',day:'numeric',weekday:'short'}).formatToParts(new Date());const g=t=>(p.find(x=>x.type===t)||{}).value||'';td.textContent=`${g('year')}년 ${g('month')}월 ${g('day')}일 (${g('weekday')})`}catch(e){}}
}
{
const f=document.querySelector('form.search');
if(f){const R=f.dataset.root,q=f.querySelector('input'),dr=f.querySelector('.drop');let D=null;
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const load=()=>D?Promise.resolve(D):fetch(R+'search-index.json').then(r=>r.json()).then(j=>D=j).catch(()=>D=[]);
const run=()=>{const v=q.value.trim().toLowerCase();if(!v){dr.classList.remove('on');return}
load().then(d=>{const h=d.filter(x=>(x.t+' '+x.s+' '+x.y+' '+x.x).toLowerCase().includes(v)).slice(0,8);
dr.innerHTML=h.length?h.map(x=>`<a href="${R}articles/${esc(x.id)}.html">${esc(x.t)}<small>${esc(x.s)}${x.y?' · '+esc(x.y):''} · ${esc(x.d)}</small></a>`).join('')+`<a href="${R}search.html?q=${encodeURIComponent(q.value.trim())}"><small>전체 결과 보기 →</small></a>`:'<p>검색 결과가 없습니다</p>';dr.classList.add('on')})};
q.addEventListener('input',run);
document.addEventListener('click',e=>{if(!f.contains(e.target))dr.classList.remove('on')});
document.addEventListener('keydown',e=>{if(e.key==='Escape')dr.classList.remove('on')});}
}
</script>"""


def footer():
    return f"""
<footer class="site"><span>{SITE_NAME} · 평일 오전 8시(KST) 발행 · 전 세계 AI 도입·활용·규제 소식</span><span>요약은 원문을 바탕으로 새로 작성했으며, 기사 원문의 저작권은 각 매체에 있습니다.</span></footer>
</div>
{SEARCH_JS}
</body>
</html>
"""


def write(rel, text):
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(text)


def item_li(a, R):
    pk = '<em class="pick">Pick</em>' if a["pick"] else ""
    return f"""<li data-type="{E(a['type'])}"><span class="d">{short(a['date'])}</span><div><span class="kick s">{pk}{E(tagline(a))}</span><h3><a class="t" href="{R}articles/{a['id']}.html">{E(a['title'])}</a></h3><p>{E(a['summary'])}</p></div></li>"""


# ---------- pages ----------
def number_cards(d, R, title="숫자로 보는 오늘"):
    amap = {a["id"]: a for a in d["arts"]}
    cards = []
    for nb in d.get("numbers", []):
        a = amap.get(f"{d['date']}-{nb['ref']}")
        if not a:
            continue
        cards.append(f"""<a class="ncard" href="{R}articles/{a['id']}.html"><strong class="nv">{E(nb['value'])}</strong><span class="nl">{E(nb['label'])}</span><span class="ns">{E(nb.get('source', ''))} · <span class="u">관련 기사 →</span></span></a>""")
    if not cards:
        return ""
    return f"""<div class="label"><h2>{title}</h2></div><div class="ngrid">{''.join(cards)}</div>"""


def build_home(issues, arts, monthly):
    L = issues[-1]
    picks = [a for a in L["arts"] if a["pick"]]
    p1 = picks[0]
    hero = f"""<a class="hero-main" href="articles/{p1['id']}.html">
<span class="kick"><span class="num big1">1</span>{E(p1['sec'])} · {E(p1['type'])}</span>
<h2 class="t">{E(p1['title'])}</h2>
<ul class="pts">{''.join(f'<li>{E(t)}</li>' for t in p1['points'])}</ul>
<p class="why"><b>왜 중요한가</b>{E(p1['why'])}</p>
<span class="meta">{E(p1['region'])} · {md(p1['date'])} · 출처 {len(p1['sources'])}건</span></a>"""
    side = "".join(f"""<li><a href="articles/{a['id']}.html"><span class="num">{a['pick']}</span><span><span class="kick">{E(a['sec'])} · {E(a['type'])}</span><strong class="t">{E(a['title'])}</strong><span class="meta">{E(a['region'])} · {md(a['date'])}</span></span></a></li>""" for a in picks[1:])
    cards = []
    for n, s in SECTORS:
        its = [a for a in arts if a["sec"] == n]
        rows = "".join(f"""<li><a class="t" href="articles/{a['id']}.html">{'<em class="pick">Pick</em>' if a['pick'] and a['issue'] == L['issue'] else ''}{E(a['title'])}</a><span>{md(a['date'])}</span></li>""" for a in its[:3])
        cards.append(f"""<section class="sec-card"><header><a href="sectors/{s}.html">{E(n)}</a><span>전체 {len(its)}건</span></header><ul>{rows or '<li class="empty">아직 등록된 소식이 없습니다</li>'}</ul></section>""")
    y, w, _ = datetime.date.fromisoformat(L["date"]).isocalendar()
    wk = [a for a in arts if a["pick"] and datetime.date.fromisoformat(a["idate"]).isocalendar()[:2] == (y, w)][:10]
    week = "".join(f"""<li><a href="articles/{a['id']}.html"><span class="rank">{i}</span><span><span class="t">{E(a['title'])}</span><small>{E(a['sec'])} · {md(a['date'])}</small></span></a></li>""" for i, a in enumerate(wk, 1))
    if monthly:
        mf, mt = monthly[0]
        mblock = f"""<a class="monthly" href="monthly/{E(mf)}" style="display:block"><span class="kick s">최신호</span><h4 class="t">{E(mt)}</h4><p>Insight Report와 10개 분야별 월간 리뷰, 규제 동향을 정리했습니다.</p></a>"""
    else:
        mblock = """<div class="monthly"><span class="kick s">AI Link 월간 리뷰 · 2026년 11월호</span><h4>12월 1일(화) 첫 발행 예정</h4><p>한 달간 가장 임팩트 있었던 흐름을 Insight Report로 깊게 다루고, 10개 분야별 월간 리뷰와 규제 동향을 정리합니다.</p></div>"""
    nums = number_cards(L, "")
    past = "".join(f'<li><a href="{x["date"]}.html"><span class="t">제{x["issue"]}호 · {E(kdate(x["date"]))}</span><small>{E(x["picks"][0]["title"])} 외 Pick 4건</small></a></li>' for x in reversed(issues[-5:]))
    out = head(SITE_NAME, "") + header("", L) + f"""
<div class="label"><h2>Today's Pick</h2><span>제{L['issue']}호 · 수집 범위 {E(L['range'])} · <a href="{L['date']}.html">이번 호 전체 보기</a></span></div>
<div class="hero">{hero}<ol class="side">{side}</ol></div>
{nums}
<div class="label"><h2>분야별 소식</h2></div>
<div class="grid">{''.join(cards)}</div>
<div class="lower">
<section><div class="label"><h3>이번 주 주요 소식</h3></div><ol class="week">{week}</ol></section>
<section><div class="label"><h3>월간 리뷰</h3><a href="monthly/">전체 보기 ›</a></div>{mblock}
<div class="label"><h3>Daily Letter 지난 호</h3><a href="letters.html">전체 보기 ›</a></div><ul class="issues dl">{past}</ul></section>
</div>""" + footer()
    write("index.html", out)


def build_sectors(issues, arts):
    R = "../"
    L = issues[-1]
    for n, s in SECTORS:
        its = [a for a in arts if a["sec"] == n]
        types = [t for t in TYPES if any(a["type"] == t for a in its)]
        btns = '<button type="button" aria-pressed="true" data-f="">전체</button>' + "".join(f'<button type="button" aria-pressed="false" data-f="{E(t)}">{E(t)}</button>' for t in types)
        out = head(f"{n} · {SITE_NAME}", R) + header(R, L, n) + f"""
<div class="page-head"><h1>{E(n)}</h1><p>{E(n)} 분야의 AI 도입·활용·규제 소식 · 전체 {len(its)}건 · 최신순</p></div>
<div class="filters" role="group" aria-label="유형 필터">{btns if its else ''}</div>
<ul class="list" id="lst">{''.join(item_li(a, R) for a in its)}</ul>
{'' if its else '<p class="empty-msg">아직 등록된 소식이 없습니다.</p>'}
<script>
{{const b=document.querySelectorAll('.filters button'),li=document.querySelectorAll('#lst>li');
b.forEach(x=>x.addEventListener('click',()=>{{b.forEach(y=>y.setAttribute('aria-pressed',y===x));const f=x.dataset.f;li.forEach(l=>l.hidden=!!f&&l.dataset.type!==f)}}))}}
</script>""" + footer()
        write(f"sectors/{s}.html", out)


def build_articles(issues, arts):
    R = "../"
    L = issues[-1]
    for d in issues:
        A = d["arts"]
        for k, a in enumerate(A):
            if a["body"]:
                body = (f'<h2 class="subt">{E(a["subtitle"])}</h2>' if a["subtitle"] else "") + \
                       "".join(f"<p>{E(t)}</p>" for t in a["body"]) + \
                       (f'<h2 class="imp">시사점</h2>' + "".join(f"<p>{E(t)}</p>" for t in a["impl"]) if a["impl"] else "")
                body = f'<div class="prose">{body}</div>'
            elif a["pick"]:
                body = f"""<ul class="pts">{''.join(f'<li>{E(t)}</li>' for t in a['points'])}</ul>
<p class="why"><b>왜 중요한가</b>{E(a['why'])}</p>"""
            else:
                body = f"""<p class="lead">{E(a['detail'] or a['summary'])}</p>"""
            srcs = "".join(f'<li><a href="{E(s["url"])}">{E(s["name"])}</a></li>' for s in a["sources"])
            rel = [x for x in arts if x["sec"] == a["sec"] and x["id"] != a["id"]][:4]
            prv = A[k - 1] if k > 0 else None
            nxt = A[k + 1] if k + 1 < len(A) else None
            pn = '<div class="pn">' + (f'<a href="{prv["id"]}.html"><small>← 이전 기사</small><span class="t">{E(prv["title"])}</span></a>' if prv else '<span></span>') + \
                 (f'<a class="next" href="{nxt["id"]}.html"><small>다음 기사 →</small><span class="t">{E(nxt["title"])}</span></a>' if nxt else '<span></span>') + '</div>'
            kick = f"Today's Pick {a['pick']} · " if a["pick"] else ""
            ipicks = [x for x in A if x["pick"]]
            side_picks = "".join(f'<li><a href="{x["id"]}.html"{" aria-current=page" if x["id"] == a["id"] else ""}><span class="n2">{x["pick"]}</span><span><span class="t">{E(x["title"])}</span><small>{E(x["sec"])}</small></span></a></li>' for x in ipicks)
            latest = [x for x in arts if x["id"] != a["id"] and not (x["issue"] == a["issue"] and x["pick"])][:6]
            side_latest = "".join(f'<li><a href="{x["id"]}.html"><span><span class="t">{E(x["title"])}</span><small>{E(x["sec"])} · {md(x["date"])}</small></span></a></li>' for x in latest)
            chips = "".join(f'<a href="{R}sectors/{sl}.html">{E(n)}</a>' for n, sl in SECTORS)
            out = head(f"{a['title']} · {SITE_NAME}", R) + header(R, L, a["sec"]) + f"""
<div class="crumb"><a href="{R}index.html">홈</a> › <a href="{R}sectors/{SLUG[a['sec']]}.html">{E(a['sec'])}</a></div>
<header class="post-head">
<span class="kick">{E(kick)}{E(tagline(a))}</span>
<h1>{E(a['title'])}</h1>
<span class="meta">{E(kdate(a['date']))} · <a class="u" href="{R}{a['idate']}.html">제{a['issue']}호 Daily Letter에 수록</a></span>
</header>
<div class="post-grid">
<div>
<article class="post">
{body}
<div class="srcs"><h2>원 출처</h2><ul>{srcs}</ul></div>
</article>
{pn}
<section class="related"><div class="label"><h3>{E(a['sec'])} 관련 소식</h3><a href="{R}sectors/{SLUG[a['sec']]}.html">전체 보기 ›</a></div><ul class="list">{''.join(item_li(x, R) for x in rel) or '<li><span></span><p>아직 다른 소식이 없습니다.</p></li>'}</ul></section>
</div>
<aside class="post-side" aria-label="함께 볼 소식">
<section class="side-box"><h2>제{a['issue']}호 Today's Pick <a href="{R}{a['idate']}.html">전체 ›</a></h2><ol>{side_picks}</ol></section>
<section class="side-box"><h2>최신 소식</h2><ul>{side_latest}</ul></section>
<section class="side-box"><h2>분야별 보기</h2><div class="secchips">{chips}</div></section>
</aside>
</div>
""" + footer()
            write(f"articles/{a['id']}.html", out)


def build_letters(issues, monthly):
    L = issues[-1]
    for d in issues:
        picks = [a for a in d["arts"] if a["pick"]]
        p1 = picks[0]
        lead = f"""<a class="hero-main" id="pick-1" href="articles/{p1['id']}.html" style="border-right:0;padding-right:0">
<span class="kick"><span class="num big1">1</span>{E(tagline(p1))}</span>
<h2 class="t">{E(p1['title'])}</h2>
<ul class="pts">{''.join(f'<li>{E(t)}</li>' for t in p1['points'])}</ul>
<p class="why"><b>왜 중요한가</b>{E(p1['why'])}</p>
<span class="meta">{md(p1['date'])} · 출처 {len(p1['sources'])}건 · <span class="u" style="color:var(--slate)">기사 보기 →</span></span></a>"""
        rest = "".join(f"""<a class="pcard" id="pick-{a['pick']}" href="articles/{a['id']}.html"><span class="pnum">{a['pick']}</span><span class="kick">{E(tagline(a))}</span><strong class="t">{E(a['title'])}</strong><span class="pw">{E(a['why'])}</span><span class="meta">{md(a['date'])} · <span class="u" style="color:var(--slate)">기사 보기 →</span></span></a>""" for a in picks[1:])
        cards, toc = [], []
        for n, s_ in SECTORS:
            its = [a for a in d["arts"] if not a["pick"] and a["sec"] == n]
            rows = "".join(f"""<li class="lc"><a href="articles/{a['id']}.html"><span class="t">{E(a['title'])}</span><small>{E(a['summary'])}</small></a></li>""" for a in its)
            cards.append(f"""<section class="sec-card" id="sec-{s_}"><header><a href="sectors/{s_}.html">{E(n)}</a><span>{len(its)}건</span></header><ul>{rows or '<li class="empty">해당 기간 주요 소식 없음</li>'}</ul></section>""")
            toc.append(f'<li><a href="#sec-{s_}"><span><span class="t">{E(n)}</span></span><small style="margin:0">{len(its)}건</small></a></li>')
        past = "".join(f'<li><a href="{x["date"]}.html"{" aria-current=page" if x["date"] == d["date"] else ""}><span><span class="t">제{x["issue"]}호 · {E(kdate(x["date"]))}</span><small>Pick 5 · 분야별 {len(x["others"])}건</small></span></a></li>' for x in list(reversed(issues))[:6])
        if monthly:
            mf, mt = monthly[0]
            mon = f'<li><a href="monthly/{E(mf)}"><span><span class="t">{E(mt)}</span><small>Insight Report 포함</small></span></a></li>'
        else:
            mon = '<li><span class="meta" style="display:block;padding:10px 0">11월호는 12월 1일(화)에 발행됩니다</span></li>'
        out = head(f"제{d['issue']}호 · {SITE_NAME}", "") + header("", L) + f"""
<div class="page-head"><span class="kick">Daily Letter</span><h1>제{d['issue']}호 · {E(kdate(d['date']))}</h1><p>수집 범위 {E(d['range'])} · Today's Pick 5건 · 분야별 소식 {len(d['others'])}건</p></div>
<div class="label" id="picks"><h2>Today's Pick</h2></div>
<div class="letter-lead">{lead}</div>
<div class="pgrid">{rest}</div>
<div class="label" id="sectors"><h2>분야별 소식</h2><span>Today's Pick에 실린 소식은 제외</span></div>
<div class="grid lgrid">{''.join(cards)}</div>""" + footer()
        write(f"{d['date']}.html", out)


def build_search(issues, arts):
    L = issues[-1]
    idx = [{"id": a["id"], "t": a["title"], "s": a["sec"], "y": a["type"], "d": short(a["date"]),
            "x": " ".join([a["summary"], a["detail"], a["why"], a["region"], a["subtitle"]] + a["points"] + a["body"])} for a in arts]
    write("search-index.json", json.dumps(idx, ensure_ascii=False))
    opts_s = "".join(f'<option>{E(n)}</option>' for n, _ in SECTORS)
    opts_t = "".join(f'<option>{E(t)}</option>' for t in TYPES)
    fld = "height:44px;border:1.5px solid var(--ink);padding:0 12px;font:16px 'Noto Sans KR',sans-serif;background:var(--bg);color:var(--ink)"
    out = head(f"검색 · {SITE_NAME}", "") + header("", L) + f"""
<div class="page-head"><h1>기사 검색</h1><p>제목·요약·분야·유형에서 찾습니다</p></div>
<form class="filters" role="search" onsubmit="return false">
<input id="sq" type="search" placeholder="검색어" aria-label="검색어" style="{fld};flex:1 1 260px">
<select id="ss" aria-label="분야" style="{fld}"><option value="">전체 분야</option>{opts_s}</select>
<select id="st" aria-label="유형" style="{fld}"><option value="">전체 유형</option>{opts_t}</select>
</form>
<p class="meta" id="cnt"></p>
<ul class="list" id="out"></ul>
<script>
{{
const esc=s=>String(s).replace(/[&<>"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]));
const q=document.getElementById('sq'),ss=document.getElementById('ss'),st=document.getElementById('st'),out=document.getElementById('out'),cnt=document.getElementById('cnt');
let D=[];
q.value=new URLSearchParams(location.search).get('q')||'';
const run=()=>{{const v=q.value.trim().toLowerCase();const h=D.filter(x=>(!v||(x.t+' '+x.s+' '+x.y+' '+x.x).toLowerCase().includes(v))&&(!ss.value||x.s===ss.value)&&(!st.value||x.y===st.value));
cnt.textContent=h.length+'건';
out.innerHTML=h.map(x=>`<li><span class="d">${{esc(x.d)}}</span><div><span class="kick s">${{esc(x.s)}}${{x.y?' · '+esc(x.y):''}}</span><h3><a class="t" href="articles/${{esc(x.id)}}.html">${{esc(x.t)}}</a></h3></div></li>`).join('')||'<li><span></span><p class="empty-msg">검색 결과가 없습니다</p></li>'}};
fetch('search-index.json').then(r=>r.json()).then(j=>{{D=j;run()}}).catch(()=>{{cnt.textContent='검색 데이터를 불러오지 못했습니다'}});
[q,ss,st].forEach(e=>e.addEventListener('input',run));
}}
</script>""" + footer()
    write("search.html", out)


def build_monthly_index(issues):
    L = issues[-1]
    files = sorted([f for f in glob.glob(os.path.join(ROOT, "monthly", "*.html")) if os.path.basename(f) != "index.html"], reverse=True)
    monthly = []
    for f in files:
        t = re.search(r"<title>(.*?)</title>", open(f, encoding="utf-8").read(), re.S)
        monthly.append((os.path.basename(f), t.group(1).strip() if t else os.path.basename(f)))
    rows = "".join(f'<li><span class="d">{E(n[:7].replace("-", "."))}</span><div><h3><a class="t" href="{E(n)}">{E(t)}</a></h3><p>Insight Report 포함</p></div></li>' for n, t in monthly)
    out = head(f"월간 리뷰 · {SITE_NAME}", "../") + header("../", L, "monthly") + f"""
<div class="page-head"><h1>월간 리뷰</h1><p>매월 첫 영업일 발행 · 한 달의 핵심 흐름과 Insight Report</p></div>
<ul class="list">{rows}</ul>
{'' if monthly else '<p class="empty-msg">첫 호(2026년 11월호)는 12월 1일(화)에 발행됩니다.</p>'}""" + footer()
    write("monthly/index.html", out)
    return monthly


def build_letter_index(issues):
    L = issues[-1]
    rows = "".join(f'<li><span class="d">{short(d["date"])}</span><div><h3><a class="t" href="{d["date"]}.html">제{d["issue"]}호 · {E(kdate(d["date"]))}</a></h3><p>{E(" · ".join(p["title"] for p in d["picks"][:3]))}</p></div></li>' for d in reversed(issues))
    out = head(f"지난 호 · {SITE_NAME}", "") + header("", L) + f"""
<div class="page-head"><h1>지난 호</h1><p>Daily Letter 전체 {len(issues)}호 · 최신순</p></div>
<ul class="list">{rows}</ul>""" + footer()
    write("letters.html", out)


def main():
    issues, arts = load()
    monthly = build_monthly_index(issues)
    build_home(issues, arts, monthly)
    build_sectors(issues, arts)
    build_articles(issues, arts)
    build_letters(issues, monthly)
    build_search(issues, arts)
    build_letter_index(issues)
    print(f"built: {len(issues)} issue(s), {len(arts)} article(s), {len(monthly)} monthly")


if __name__ == "__main__":
    main()
