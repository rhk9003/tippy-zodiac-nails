"""Build embed.html (paste into Shopline custom HTML block) and index.html (preview).

Usage:
  python3 tools/build.py            # build from data/zodiac.json
  python3 tools/build.py --fetch    # fill product name/image from product URLs, then build
"""
import html
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "zodiac.json"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/128 Safari/537.36"
OWNER = "65d6c326714802005d9980e5"

CSS = """
.tpz{--tpz-ink:#2b2b2b;--tpz-muted:#7a7a7a;--tpz-line:#ececec;--tpz-accent:#c58a6a;--tpz-pink:#e8b7a8;--tpz-blush:#faf1ee;color:var(--tpz-ink);font-size:15px;line-height:1.8;max-width:1100px;margin:0 auto;text-align:left}
.tpz *,.tpz *::before,.tpz *::after{box-sizing:border-box}
.tpz h1,.tpz h2,.tpz p,.tpz ul,.tpz li,.tpz dl,.tpz dt,.tpz dd{margin:0;padding:0;border:0;font-size:inherit;font-weight:inherit;line-height:inherit;color:inherit;text-transform:none}
.tpz ul{list-style:none}
.tpz a{color:inherit;text-decoration:none}
.tpz img{display:block;max-width:100%;border:0}
.tpz .tpz-hero{text-align:center;padding:24px 0 4px}
.tpz .tpz-kicker{font-size:12px;letter-spacing:.3em;color:var(--tpz-accent)}
.tpz .tpz-title{font-size:30px;font-weight:500;letter-spacing:.3em;padding-left:.3em;line-height:1.4;margin:8px 0 4px}
.tpz .tpz-sub{font-size:14px;letter-spacing:.08em;color:var(--tpz-muted)}
.tpz .tpz-lead{max-width:32em;margin:18px auto 0}
.tpz .tpz-nav{display:grid;grid-template-columns:repeat(12,1fr);gap:8px;margin:32px 0 16px}
.tpz .tpz-nav a{display:flex;flex-direction:column;align-items:center;gap:6px;font-size:13px;line-height:1.4}
.tpz .tpz-dot{width:56px;height:56px;border-radius:50%;background:var(--tpz-blush);color:var(--tpz-accent);display:flex;align-items:center;justify-content:center;font-size:24px;line-height:1;transition:background-color .2s,color .2s}
.tpz .tpz-nav a:hover .tpz-dot{background:var(--tpz-pink);color:#fff}
.tpz .tpz-sign{padding:44px 0;border-top:1px solid var(--tpz-line);scroll-margin-top:110px}
.tpz .tpz-sign-head{text-align:center;margin-bottom:28px}
.tpz .tpz-sign-glyph{display:inline-flex;width:44px;height:44px;border-radius:50%;background:var(--tpz-blush);color:var(--tpz-accent);align-items:center;justify-content:center;font-size:20px;line-height:1;margin-bottom:8px}
.tpz .tpz-sign-name{font-size:22px;font-weight:500;letter-spacing:.25em;padding-left:.25em;line-height:1.4}
.tpz .tpz-sign-en{font-size:12px;letter-spacing:.2em;color:var(--tpz-muted);margin-top:2px}
.tpz .tpz-sign-body{display:grid;grid-template-columns:1fr 1fr;gap:48px;align-items:start}
.tpz .tpz-tagline{font-size:18px;font-weight:500;line-height:1.6;margin-bottom:10px}
.tpz .tpz-sign-text p+p{margin-top:8px}
.tpz .tpz-meta{margin-top:20px;border-top:1px solid var(--tpz-line)}
.tpz .tpz-meta div{display:flex;gap:16px;padding:10px 0;border-bottom:1px solid var(--tpz-line);font-size:14px;line-height:1.6}
.tpz .tpz-meta dt{flex:0 0 5.5em;color:var(--tpz-muted)}
.tpz .tpz-meta dd{display:flex;flex-wrap:wrap;align-items:center;gap:4px 14px}
.tpz .tpz-color{display:inline-flex;align-items:center;gap:6px}
.tpz .tpz-sw{display:inline-block;width:14px;height:14px;border-radius:50%;box-shadow:inset 0 0 0 1px rgba(0,0,0,.12)}
.tpz .tpz-picks-title{font-size:13px;letter-spacing:.15em;color:var(--tpz-muted);text-align:center;margin-bottom:12px}
.tpz .tpz-cards{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.tpz .tpz-card{display:block;text-align:center}
.tpz .tpz-card-img{display:block;position:relative;width:100%;padding-top:100%;background:var(--tpz-blush);overflow:hidden}
.tpz .tpz-card-img img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transition:transform .4s}
.tpz a.tpz-card:hover .tpz-card-img img{transform:scale(1.03)}
.tpz .tpz-card-name{display:block;font-size:14px;line-height:1.5;margin-top:10px}
.tpz .tpz-empty{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;border:1px dashed var(--tpz-pink);color:var(--tpz-accent);font-size:13px;letter-spacing:.2em}
.tpz .is-empty .tpz-card-name{color:var(--tpz-muted)}
.tpz .tpz-cta{text-align:center;padding:40px 0 8px;border-top:1px solid var(--tpz-line)}
.tpz .tpz-btn{display:inline-block;background:var(--tpz-accent);color:#fff;font-size:14px;line-height:1.5;padding:10px 44px;border-radius:4px;letter-spacing:.05em;transition:opacity .2s}
.tpz .tpz-btn:hover{opacity:.85;color:#fff}
.tpz .tpz-more{margin-top:40px;padding-top:28px;border-top:1px solid var(--tpz-line)}
.tpz .tpz-more-title{font-size:18px;font-weight:500;text-align:center;letter-spacing:.2em;padding-left:.2em;margin-bottom:12px}
.tpz .tpz-more ul{display:grid;grid-template-columns:1fr 1fr;gap:0 32px;max-width:760px;margin:0 auto}
.tpz .tpz-more a{display:flex;justify-content:space-between;gap:12px;padding:12px 0;border-bottom:1px solid var(--tpz-line)}
.tpz .tpz-more a:hover{color:var(--tpz-accent)}
.tpz .tpz-note{text-align:center;font-size:12px;line-height:1.7;color:var(--tpz-muted);padding:20px 0 8px}
.tpz .tpz-note a{text-decoration:underline;text-underline-offset:2px}
@media (max-width:900px){.tpz .tpz-nav{grid-template-columns:repeat(6,1fr);gap:16px 8px}.tpz .tpz-sign-body{gap:32px}}
@media (max-width:640px){.tpz .tpz-title{font-size:26px}.tpz .tpz-nav{grid-template-columns:repeat(4,1fr)}.tpz .tpz-dot{width:52px;height:52px;font-size:22px}.tpz .tpz-sign{padding:36px 0}.tpz .tpz-sign-body{grid-template-columns:1fr;gap:24px}.tpz .tpz-more ul{grid-template-columns:1fr}}
""".strip()

TEXT_GLYPH = "︎"  # 以文字樣式顯示星座符號，避免被當成 emoji


def esc(s):
    return html.escape(s or "", quote=True)


def resized(image_url):
    m = re.search(r"media/image_clips/([0-9a-f]{24})/original\.(\w+)", image_url or "")
    if not m:
        return image_url
    return f"https://shoplineimg.com/{OWNER}/{m.group(1)}/800x.webp?source_format={m.group(2)}"


def fetch_product(url):
    raw = subprocess.run(["curl", "-sL", "-A", UA, url], capture_output=True, text=True, timeout=60).stdout
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', raw, re.S):
        try:
            d = json.loads(block)
        except json.JSONDecodeError:
            continue
        if isinstance(d, dict) and d.get("@type") == "Product":
            img = d.get("image")
            img = img[0] if isinstance(img, list) and img else img
            return d.get("name", ""), resized(img or "")
    return "", ""


def card(p):
    if not p.get("url"):
        return ('<div class="tpz-card is-empty"><span class="tpz-card-img"><span class="tpz-empty">待提品</span></span>'
                '<span class="tpz-card-name">商品名稱</span></div>')
    img = f'<img src="{esc(p.get("image"))}" alt="{esc(p.get("name"))}" loading="lazy">' if p.get("image") else ""
    return (f'<a class="tpz-card" href="{esc(p["url"])}"><span class="tpz-card-img">{img}</span>'
            f'<span class="tpz-card-name">{esc(p.get("name"))}</span></a>')


def sign_block(s, picks_title):
    colors = "".join(
        f'<span class="tpz-color"><span class="tpz-sw" style="background:{esc(c)}"></span>{esc(n)}</span>'
        for n, c in s["colors"])
    text = "".join(f"<p>{esc(t)}</p>" for t in s["text"])
    cards = "".join(card(p) for p in s["products"])
    return f"""
<section class="tpz-sign" id="tpz-{s['id']}">
<div class="tpz-sign-head"><span class="tpz-sign-glyph" aria-hidden="true">{s['glyph']}{TEXT_GLYPH}</span><h2 class="tpz-sign-name">{esc(s['name'])}</h2><p class="tpz-sign-en">{esc(s['en'])}　{esc(s['dates'])}</p></div>
<div class="tpz-sign-body">
<div class="tpz-sign-text"><p class="tpz-tagline">{esc(s['tagline'])}</p>{text}
<dl class="tpz-meta">
<div><dt>元素・守護星</dt><dd>{esc(s['element'])}・{esc(s['ruler'])}</dd></div>
<div><dt>適合風格</dt><dd>{'・'.join(esc(x) for x in s['styles'])}</dd></div>
<div><dt>適合顏色</dt><dd>{colors}</dd></div>
<div><dt>幸運物</dt><dd>{esc(s['item'])}</dd></div>
</dl></div>
<div class="tpz-picks"><p class="tpz-picks-title">{esc(picks_title)}</p><div class="tpz-cards">{cards}</div></div>
</div>
</section>"""


def build_embed(d):
    h = d["hero"]
    nav = "".join(
        f'<a href="#tpz-{s["id"]}"><span class="tpz-dot" aria-hidden="true">{s["glyph"]}{TEXT_GLYPH}</span>{esc(s["name"][:-1])}</a>'
        for s in d["signs"])
    signs = "".join(sign_block(s, d["picks_title"]) for s in d["signs"])
    src = d["sources"]
    sources = esc(src["label"]) + "：" + "、".join(
        f'<a href="{esc(l["url"])}" target="_blank" rel="noopener nofollow">{esc(l["title"])}</a>（{esc(l["about"])}）'
        for l in src["links"]) + "。" + esc(src["footnote"])
    reads = "".join(f'<li><a href="{esc(r["url"])}"><span>{esc(r["title"])}</span><span aria-hidden="true">→</span></a></li>'
                    for r in d["reads"])
    return f"""<!-- tippy 星座幸運甲｜貼進 Shopline 自訂 HTML 區塊。樣式都在 .tpz 底下，不影響官網其他區塊。 -->
<div class="tpz">
<style>{CSS}</style>
<header class="tpz-hero"><p class="tpz-kicker">{esc(h['kicker'])}</p><h1 class="tpz-title">{esc(h['title'])}</h1><p class="tpz-sub">{esc(h['sub'])}</p><p class="tpz-lead">{esc(h['lead'])}</p></header>
<nav class="tpz-nav" aria-label="星座選單">{nav}</nav>
{signs}
<div class="tpz-cta"><a class="tpz-btn" href="{esc(d['cta']['url'])}">{esc(d['cta']['label'])}</a></div>
<section class="tpz-more"><h2 class="tpz-more-title">{esc(d['more_title'])}</h2><ul>{reads}</ul></section>
<p class="tpz-note">{sources}</p>
</div>
"""


def build_preview(embed):
    return f"""<!doctype html>
<html lang="zh-Hant-TW">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>星座幸運甲｜預覽</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap" rel="stylesheet">
<style>
body{{margin:0;background:#fff;font-family:Lato,system-ui,-apple-system,"Segoe UI","PingFang TC","Microsoft JhengHei","Microsoft YaHei","Helvetica Neue",Arial,sans-serif;-webkit-font-smoothing:antialiased}}
.preview-bar{{background:#f4f4f4;color:#666;font-size:13px;line-height:1.6;text-align:center;padding:8px 16px}}
.preview-page{{max-width:1170px;margin:0 auto;padding:30px 15px 60px}}
</style>
</head>
<body>
<div class="preview-bar">預覽頁：下方內容就是貼進官網後的樣子（官網的導覽列與頁尾不在預覽裡）。每個星座請提 2 款，給商品網址即可。</div>
<main class="preview-page">
{embed}
</main>
</body>
</html>
"""


def main():
    d = json.loads(DATA.read_text(encoding="utf-8"))
    if "--fetch" in sys.argv:
        changed = False
        for s in d["signs"]:
            for p in s["products"]:
                if p.get("url") and not (p.get("name") and p.get("image")):
                    name, image = fetch_product(p["url"])
                    p["name"] = p.get("name") or name
                    p["image"] = p.get("image") or image
                    changed = True
                    print(f"fetched {s['name']}: {p['name'] or '(找不到商品資料)'}")
        if changed:
            DATA.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    embed = build_embed(d)
    (ROOT / "embed.html").write_text(embed, encoding="utf-8")
    (ROOT / "index.html").write_text(build_preview(embed), encoding="utf-8")
    filled = sum(1 for s in d["signs"] for p in s["products"] if p.get("url"))
    print(f"built embed.html + index.html（已提品 {filled}／{len(d['signs']) * 2}）")


if __name__ == "__main__":
    main()
