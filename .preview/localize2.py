"""Localise the remaining pages: three.js + font subsets shared by index/craftsman."""
import urllib.request, urllib.parse, re
from pathlib import Path

PUB = Path(r"C:\Users\yang\Desktop\mswh\public")
FONTS = PUB / "fonts"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=60).read()


pages = [PUB / "index.html", PUB / "craftsman.html"]
chars = set()
for p in pages:
    chars |= {c for c in p.read_text(encoding="utf-8") if not c.isspace() and ord(c) > 127}
chars |= {c for c in "0123456789" if c}
text_uri = urllib.parse.quote("".join(sorted(chars)), safe="")
print("unicode chars:", len(chars), "url len:", len(text_uri))

for w in (400, 600, 900):
    fam = "Noto+Serif+SC" if w == 400 else "Noto+Serif+SC:wght@%d" % w
    css = get("https://fonts.googleapis.com/css2?family=%s&text=%s" % (fam, text_uri)).decode()
    url = re.search(r"url\((https://[^)]+)\)", css).group(1)
    data = get(url)
    out = FONTS / ("notoserif-ui-%d.woff2" % w)
    out.write_bytes(data)
    print(out.name, round(len(data) / 1024, 1), "KB")

three = get("https://lib.baomitu.com/three.js/0.160.0/three.min.js")
(PUB / "js" / "three.min.js").write_bytes(three)
print("three.min.js", round(len(three) / 1024, 1), "KB")
