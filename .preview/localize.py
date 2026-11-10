"""Download and localise hall.html's external assets (fonts, ScrollTrigger, hero photo)."""
import urllib.request, re, os, json
from pathlib import Path
from PIL import Image

ROOT = Path(r"C:\Users\yang\Desktop\mswh")
PUB = ROOT / "public"
FONTS = PUB / "fonts"
FONTS.mkdir(exist_ok=True)

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")


def get(url, ua=UA):
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    return urllib.request.urlopen(req, timeout=40).read()


html = (PUB / "hall.html").read_text(encoding="utf-8")

# ---------------------------------------------------------------- charset
chars = sorted({c for c in html if not c.isspace() and (ord(c) > 127 or c.isalnum())})
cjk = [c for c in chars if ord(c) > 127]
latin = [c for c in chars if ord(c) <= 127]
print("charset:", len(chars), "non-ascii:", len(cjk))

text_uri = urllib.parse.quote("".join(cjk), safe="")

# ---------------------------------------------------------------- fonts
weights = [400, 500, 600, 900]
report = []
for w in weights:
    if w == 400:
        url = ("https://fonts.googleapis.com/css2?family=Noto+Serif+SC&text=" + text_uri)
    else:
        url = ("https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@%d&text=%s" % (w, text_uri))
    css = get(url).decode("utf-8")
    m = re.search(r"url\((https://[^)]+)\)", css)
    if not m:
        print("no font url for", w, css[:200]); continue
    data = get(m.group(1))
    out = FONTS / ("notoserif-sc-%d.woff2" % w)
    out.write_bytes(data)
    report.append((out.name, len(data)))

latin_extra = "\u2014\u00b7\u00d7\u2197\u2715"
_base = sorted(set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 .,:;/~-()" + latin_extra))
latin_uri = urllib.parse.quote("".join(_base), safe="")
for w in (400, 600):
    url = "https://fonts.googleapis.com/css2?family=Cinzel:wght@%d&text=%s" % (w, latin_uri)
    css = get(url).decode("utf-8")
    m = re.search(r"url\((https://[^)]+)\)", css)
    data = get(m.group(1))
    out = FONTS / ("cinzel-%d.woff2" % w)
    out.write_bytes(data)
    report.append((out.name, len(data)))

# ---------------------------------------------------------------- ScrollTrigger
js = get("https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js")
(PUB / "js" / "ScrollTrigger.min.js").write_bytes(js)
report.append(("ScrollTrigger.min.js", len(js)))

# ---------------------------------------------------------------- hero photo
img_url = ("https://images.unsplash.com/photo-1547981609-4b6bfe67ca0b"
           "?auto=format&fit=crop&w=2400&q=80")
raw = PUB / "images" / "_bg_raw.jpg"
raw.write_bytes(get(img_url))
im = Image.open(raw).convert("RGB")
# keep it light enough for a local demo but still crisp on wide screens
im = im.resize((2200, round(2200 * im.height / im.width)), Image.LANCZOS)
out = PUB / "images" / "hall-hero.jpg"
im.save(out, quality=82, optimize=True, progressive=True)
raw.unlink()
report.append((out.name, out.stat().st_size))

for name, size in report:
    print("%-28s %8.1f KB" % (name, size / 1024))
