#!/usr/bin/env python3
"""AI Daily Letter 정적 사이트 빌더.

사용법: python3 scripts/build.py
- data/YYYY-MM-DD.json 을 모두 읽어 같은 이름의 YYYY-MM-DD.html 을 만들고
- index.html(발행 목록)을 최신 호가 위로 오도록 다시 만든다.
JSON 형식은 data/ 안의 기존 파일을 참고.
"""
import json, glob, os, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORDER = ["ICT/모바일", "미디어", "AI/빅데이터", "모빌리티", "로봇", "헬스케어", "소비재", "금융", "제조·에너지", "공공·정책"]
E = lambda s: html.escape(str(s), quote=True)

CSS = """:root{color-scheme:light dark;--bg:light-dark(#ffffff,#10191e);--ink:light-dark(#121212,#e9eef1);--mute:light-dark(#55606a,#9fb0bb);--red:#e3120b;--slate:light-dark(#2e6f8e,#7fb6d2);--panel:light-dark(#e3ecf0,#18262e);--rule:light-dark(#d5dde2,#2a3a44)}
*{box-sizing:border-box;min-width:0}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.65 "Noto Sans KR",system-ui,sans-serif;overflow-x:clip}
html{scroll-padding-top:24px;scroll-behavior:smooth}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
a{color:var(--slate)}
.wrap{max-width:1080px;margin:0 auto;padding:0 max(5vw,16px)}
.mast{border-bottom:3px solid var(--ink);padding:28px 0 14px}
.tab{display:inline-block;background:var(--red);color:#fff;font-weight:700;font-size:14px;padding:4px 12px}
h1{font:700 clamp(30px,5vw,46px)/1.1 "Noto Serif KR",serif;margin:12px 0 6px}
.meta{color:var(--mute);font-size:14px;display:flex;flex-wrap:wrap;gap:4px 16px}
.front{padding:28px 0;border-bottom:1px solid var(--rule);max-width:760px}
h2{font:700 24px/1.2 "Noto Serif KR",serif;margin:0 0 14px}
.picks{list-style:none;margin:0;padding:0}
.picks li{border-top:1px solid var(--rule);padding:12px 0;display:grid;grid-template-columns:28px minmax(0,1fr);gap:8px}
.picks .n{font:700 22px/1 "Noto Serif KR",serif;color:var(--red)}
.picks a{color:var(--ink);text-decoration:none;font-weight:700;font-size:17px;line-height:1.45}
.picks a:hover,.picks a:focus-visible{text-decoration:underline}
.tag{display:block;font-size:13px;color:var(--slate);margin-top:4px}
.story{padding:32px 0;border-bottom:1px solid var(--rule)}
.kicker{font-size:14px;color:var(--red);font-weight:700}
.story h3{font:700 clamp(22px,3vw,30px)/1.25 "Noto Serif KR",serif;margin:6px 0 12px}
.story ul{padding-left:1.2em;margin:0 0 14px;max-width:70ch}
.story li{margin:4px 0}
.why{background:var(--panel);padding:14px 16px;max-width:70ch;margin:0 0 14px}
.why b{color:var(--slate)}
.src{font-size:14px;color:var(--mute)}
.src a{overflow-wrap:anywhere}
.top{font-size:14px}
.sector{padding:28px 0}
.sector h4{font-size:16px;margin:22px 0 4px;color:var(--slate)}
.item{border-top:1px solid var(--rule);padding:10px 0}
.item strong{display:block;font-size:16px}
.item p{margin:2px 0 4px;max-width:75ch}
footer{padding:28px 0 48px;font-size:14px;color:var(--mute)}
.list li{display:block}"""

HEAD = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>{title}</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@700&family=Noto+Sans+KR:wght@400;700&display=swap" rel="stylesheet">
<style>
""" + CSS + """
</style>
</head>
<body>
<div class="wrap">
"""


def build_issue(d):
    y, m, dd = d["date"].split("-")
    out = [HEAD.replace("{title}", f"AI Daily Letter 제{d['issue']}호")]
    out.append(f"""<header class="mast"><span class="tab">AI Daily Letter</span>
<h1>AI Daily Letter 제{d['issue']}호</h1>
<div class="meta"><span>{int(y)}년 {int(m)}월 {int(dd)}일 ({E(d['weekday'])})</span><span>수집 범위: {E(d['range'])}</span></div></header>
<section class="front" id="picks"><h2>Today's Pick</h2><ol class="picks">""")
    for i, p in enumerate(d["picks"], 1):
        out.append(f"""<li><span class="n">{i}</span><div><a href="#pick-{i}">{E(p['title'])}</a><span class="tag">{E(p['sec'])} · {E(p['type'])} · {E(p['region'])}</span></div></li>""")
    out.append("</ol></section>\n<main>")
    for i, p in enumerate(d["picks"], 1):
        pts = "".join(f"<li>{E(t)}</li>" for t in p["points"])
        srcs = " · ".join(f'<a href="{E(s["url"])}">{E(s["name"])}</a>' for s in p["sources"])
        out.append(f"""<article class="story" id="pick-{i}">
<div class="kicker">Today's Pick {i} · {E(p['sec'])} · {E(p['type'])} · {E(p['region'])} · {E(p['date'])}</div>
<h3>{E(p['title'])}</h3>
<ul>{pts}</ul>
<div class="why"><b>왜 중요한가</b> {E(p['why'])}</div>
<div class="src">출처: {srcs}</div>
<p class="top"><a href="#picks">↑ Today's Pick 목록으로</a></p>
</article>""")
    out.append(f"""</main>
<section class="sector" id="sectors"><h2>분야별 소식</h2>
<p class="src">수집 범위: {E(d['range'])} · Today's Pick에 실린 소식은 제외</p>""")
    for sec in ORDER:
        its = [o for o in d["others"] if o["sec"] == sec]
        out.append(f"<h4>{E(sec)}</h4>")
        if not its:
            out.append('<div class="item"><p>해당 기간 주요 소식 없음 (Today\'s Pick 제외)</p></div>')
        for o in its:
            out.append(f"""<div class="item"><strong>{E(o['title'])}</strong><p>{E(o['summary'])}</p><span class="src">{E(o['date'])} · 출처: <a href="{E(o['src_url'])}">{E(o['src_name'])}</a></span></div>""")
    notion = d.get("notion")
    out.append(f"""</section>
<footer>
<p><a href="./">← 지난 호 목록</a></p>
{f'<p>전체 소식은 Notion의 <a href="{E(notion)}">AI Daily Letter 아카이브</a>에서 분야별로 볼 수 있습니다.</p>' if notion else ''}
<p>요약은 원문을 바탕으로 새로 작성한 것이며, 기사 원문의 저작권은 각 매체에 있습니다. 자세한 내용은 출처 링크에서 확인하세요.</p>
</footer>
</div>
</body>
</html>
""")
    return "\n".join(out)


def build_index(issues):
    import re
    out = [HEAD.replace("{title}", "AI Daily Letter")]
    out.append("""<header class="mast"><span class="tab">AI Daily Letter</span><h1>발행 목록</h1>
<div class="meta"><span>평일 오전 8시(KST) 발행 · 전 세계 AI 도입·활용·규제 소식</span></div></header>
""")
    monthly = sorted(glob.glob(os.path.join(ROOT, "monthly", "*.html")), reverse=True)
    if monthly:
        out.append('<section class="front"><h2>월간 간행물</h2><ul class="picks list">')
        for f in monthly:
            t = re.search(r"<title>(.*?)</title>", open(f, encoding="utf-8").read(), re.S)
            name = os.path.basename(f)
            out.append(f'<li><a href="monthly/{E(name)}">{E(t.group(1).strip() if t else name)}</a></li>')
        out.append("</ul></section>")
    out.append("""<section class="front"><h2>Daily Letter</h2><ul class="picks list">""")
    for d in issues:
        y, m, dd = d["date"].split("-")
        heads = " · ".join(p["title"].split("…")[0] for p in d["picks"])
        out.append(f"""<li><a href="{d['date']}.html">제{d['issue']}호 · {int(y)}년 {int(m)}월 {int(dd)}일 ({E(d['weekday'])})</a><span class="tag">{E(heads)}</span></li>""")
    out.append("</ul></section>\n</div>\n</body>\n</html>\n")
    return "\n".join(out)


def main():
    issues = []
    for f in sorted(glob.glob(os.path.join(ROOT, "data", "*.json"))):
        with open(f, encoding="utf-8") as fh:
            d = json.load(fh)
        with open(os.path.join(ROOT, d["date"] + ".html"), "w", encoding="utf-8") as fh:
            fh.write(build_issue(d))
        issues.append(d)
    issues.sort(key=lambda x: x["date"], reverse=True)
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(build_index(issues))
    print(f"built {len(issues)} issue(s)")


if __name__ == "__main__":
    main()
