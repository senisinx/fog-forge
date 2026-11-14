#!/usr/bin/env python3
"""Build the language versions of fogforge.app.

The English pages in src/ are the source. Every text in them (text between tags, alt, aria-label,
data-alt, title, the page description and the texts in the `var S = {...}` line of the scripts) is a key;
i18n/<code>.json maps each key to its translation. The build writes

    index.html, contact/index.html, maps/index.html    English (from src/ as is)
    <code>/index.html, <code>/contact/..., ...         every other language

The pictures and map names on maps/ come from data/maps.json (made by tools/import_maps.py); the build fills them
in at <!-- maps:grid -->, with the names the game uses in that language.

and adds the language menu, hreflang links and, on the English pages, the redirect to the browser's language.
It also writes the self-hosted fonts block (fonts/), the JSON-LD of both tools on the start pages, sitemap.xml,
robots.txt and 404.html (one page for every language; its texts come from i18n/ too).

    python3 tools/build.py              build all pages
    python3 tools/build.py --check      fail if a page is out of date or a translation is missing
    python3 tools/build.py --template   print every key as JSON (start of a new language file)

Only the Python standard library is needed.
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
I18N = ROOT / "i18n"
SITE = "https://fogforge.app"
PAGES = ["index.html", "contact/index.html", "maps/index.html"]
DATA = ROOT / "data"

# code: (html lang, name in its own language, locale for dates)
LANGS = {
    "en": ("en", "English", "en-GB"),
    "de": ("de", "Deutsch", "de-DE"),
    "fr": ("fr", "Français", "fr-FR"),
    "es": ("es", "Español", "es-ES"),
    "it": ("it", "Italiano", "it-IT"),
    "pt": ("pt-BR", "Português", "pt-BR"),
    "pl": ("pl", "Polski", "pl-PL"),
    "ru": ("ru", "Русский", "ru-RU"),
    "tr": ("tr", "Türkçe", "tr-TR"),
    "nl": ("nl", "Nederlands", "nl-NL"),
    "zh": ("zh-Hans", "简体中文", "zh-CN"),
    "ja": ("ja", "日本語", "ja-JP"),
    "ko": ("ko", "한국어", "ko-KR"),
}

# Names and handles stay as they are in every language.
KEEP = {
    "Fog Forge", "Fog", "Forge", "Scout", "Translate", "Fog Scout", "Fog Translate", "GitHub", "Discord", "Claude", "Gemini", "Ollama",
    "senisin", "github.com/senisinx", "hens333.com/callouts", "DBD Map Overlay", "fog-scout", "fog-translate",
}
# Keys that are not text in src/ but made by this build.
# The six map styles of Fog Scout, in the order of data/maps.json "styles"; named as in the app.
MAP_STYLES = ["Original", "Dark", "Grey", "Grey with edge", "Dark lilac", "Lilac see-through"]
# The page GitHub Pages shows for an unknown address (src/404.html): title, text, link. One page for all languages.
NOT_FOUND = ["Page not found", "This page does not exist, or it has moved.", "To the start page"]
EXTRA = ["Language"] + MAP_STYLES + NOT_FOUND

# Self-hosted variable fonts (fonts/, SIL OFL 1.1, from Fontsource): family, file stem, weights, subsets.
# Only latin is preloaded; the other subsets load when a page uses their characters (unicode-range).
FONTS = [
    ("Big Shoulders Display", "big-shoulders-display", "100 900", ["latin", "latin-ext"]),
    ("Instrument Sans", "instrument-sans", "400 700", ["latin", "latin-ext"]),
    ("JetBrains Mono", "jetbrains-mono", "100 800", ["latin", "latin-ext", "cyrillic", "cyrillic-ext"]),
]
PRELOAD = ["big-shoulders-display-latin", "instrument-sans-latin"]
RANGES = {
    "latin": "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,"
             "U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD",
    "latin-ext": "U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,"
                 "U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF",
    "cyrillic": "U+0301,U+0400-045F,U+0490-0491,U+04B0-04B1,U+2116",
    "cyrillic-ext": "U+0460-052F,U+1C80-1C8A,U+20B4,U+2DE0-2DFF,U+A640-A69F,U+FE2E-FE2F",
}

# The two tools for the JSON-LD block of the start pages; the description is a text of the page, so it is translated.
TOOLS = [
    ("Fog Scout", "fog-scout", "Shows the callout map of the map you are on, right when the match starts."),
    ("Fog Translate", "fog-translate", "Translates the Dead by Daylight chat while you play, from any script."),
]

TOKEN = re.compile(r"(<script\b.*?</script>|<style\b.*?</style>|<!--.*?-->|<[^>]+>)", re.S | re.I)
ATTR = re.compile(r'\b(alt|aria-label|data-alt|title)="([^"]*)"')
META = re.compile(r'(<meta (?:name="description"|property="og:title"|property="og:description") content=")([^"]*)(")')
SCRIPT_S = re.compile(r"^(\s*var S = )(\{.*\});$", re.M)


def norm(text):
    return " ".join(text.split())


def wanted(text):
    return bool(text) and text not in KEEP and re.search(r"[A-Za-z]", text) is not None


def keys_of(page):
    """Every translatable text of a source page, in order."""
    out = []
    for part in TOKEN.split(page):
        if not part:
            continue
        low = part[:7].lower()
        if low.startswith("<script"):
            m = SCRIPT_S.search(part)
            if m:
                out += [v for k, v in json.loads(m.group(2)).items() if k != "locale"]
        elif low.startswith("<style") or part.startswith("<!--"):
            continue
        elif part.startswith("<"):
            out += [html.unescape(v) for _, v in ATTR.findall(part)]
            out += [html.unescape(m.group(2)) for m in META.finditer(part)]
        else:
            out.append(html.unescape(norm(part)))
    return [k for k in out if wanted(k)]


def all_keys():
    seen = {}
    for p in PAGES:
        for k in keys_of((SRC / p).read_text(encoding="utf-8")):
            seen.setdefault(k, None)
    for k in EXTRA:
        seen.setdefault(k, None)
    return list(seen)


def page_url(code, page):
    base = "/" if code == "en" else "/%s/" % code
    return base + page[: page.rfind("/") + 1]


def head_block(code, page):
    lines = ['<link rel="alternate" hreflang="%s" href="%s%s">' % (LANGS[c][0], SITE, page_url(c, page)) for c in LANGS]
    lines.append('<link rel="alternate" hreflang="x-default" href="%s%s">' % (SITE, page_url("en", page)))
    # English pages send a first-time visitor to their browser's language; a pick in the menu is remembered.
    lines.append("""<script>
(function () {
  var LANGS = %s, here = "%s", path = "%s";
  var saved = null; try { saved = localStorage.getItem("ff-lang"); } catch (e) {}
  if (here === "en" && !saved) {
    var want = (navigator.languages || [navigator.language || ""]);
    for (var i = 0; i < want.length; i++) {
      var c = String(want[i]).toLowerCase().split("-")[0];
      if (c === "en") break;
      if (LANGS.indexOf(c) > 0) { location.replace("/" + c + path + location.hash); return; }
    }
  }
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest(".lang a");
    if (a) { try { localStorage.setItem("ff-lang", a.getAttribute("data-lang")); } catch (x) {} if (location.hash) a.href = a.href.split("#")[0] + location.hash; return; }
    var open = document.querySelector(".lang[open]");
    if (open && !open.contains(e.target)) open.removeAttribute("open");
  });
})();
</script>""" % (json.dumps(list(LANGS)), code, page_url("en", page)))
    return "\n".join(lines)


def fonts_block():
    def face(family, stem, weight, sub):
        return ("@font-face { font-family: \"%s\"; font-style: normal; font-weight: %s; font-display: swap; "
                "src: url(/fonts/%s-%s-wght-normal.woff2) format(\"woff2\"); unicode-range: %s; }"
                % (family, weight, stem, sub, RANGES[sub]))
    lines = ['<link rel="preload" href="/fonts/%s-wght-normal.woff2" as="font" type="font/woff2" crossorigin>' % p
             for p in PRELOAD]
    lines.append("<style>\n%s\n</style>" % "\n".join(face(f, st, w, sub) for f, st, w, subs in FONTS for sub in subs))
    return "\n".join(lines)


def ld_block(code, tr):
    apps = [{
        "@context": "https://schema.org", "@type": "SoftwareApplication", "name": name,
        "description": tr(desc), "operatingSystem": "Windows",
        "applicationCategory": "UtilitiesApplication", "inLanguage": LANGS[code][0],
        "url": SITE + page_url(code, "index.html") + "#" + repo.split("-")[1],
        "downloadUrl": "https://github.com/senisinx/%s/releases/latest" % repo,
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
        "author": {"@type": "Person", "name": "senisinx", "url": "https://github.com/senisinx"},
    } for name, repo, desc in TOOLS]
    text = json.dumps(apps, ensure_ascii=False, indent=1).replace("</", "<\\/")
    return '<script type="application/ld+json">\n%s\n</script>' % text


def sitemap():
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for page in PAGES:
        alts = ['    <xhtml:link rel="alternate" hreflang="%s" href="%s%s"/>' % (LANGS[c][0], SITE, page_url(c, page))
                for c in LANGS]
        alts.append('    <xhtml:link rel="alternate" hreflang="x-default" href="%s%s"/>' % (SITE, page_url("en", page)))
        for code in LANGS:
            out += ["  <url>", "    <loc>%s%s</loc>" % (SITE, page_url(code, page))] + alts + ["  </url>"]
    out.append("</urlset>")
    return "\n".join(out) + "\n"


def robots():
    return "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % SITE


def not_found(tables):
    """src/404.html with the texts of every language; a script picks the language from the address or the browser."""
    texts = {c: ([k for k in NOT_FOUND] if c == "en" else [tables[c][k] for k in NOT_FOUND]) for c in LANGS}
    script = """<script>
(function () {
  var T = %s;
  var code = (location.pathname.match(/^\\/([a-z]{2})\\//) || [])[1], saved = null;
  try { saved = localStorage.getItem("ff-lang"); } catch (e) {}
  if (!T[code]) code = saved;
  if (!T[code]) {
    var want = navigator.languages || [navigator.language || ""];
    for (var i = 0; i < want.length && !T[code]; i++) code = String(want[i]).toLowerCase().split("-")[0];
  }
  if (!T[code]) return;
  var t = T[code], home = code === "en" ? "/" : "/" + code + "/";
  document.documentElement.lang = %s[code];
  document.title = t[0] + " · Fog Forge";
  document.getElementById("nf-title").textContent = t[0];
  document.getElementById("nf-text").textContent = t[1];
  var a = document.getElementById("nf-home"); a.textContent = t[2]; a.href = home;
  document.getElementById("nf-logo").href = home;
})();
</script>""" % (json.dumps(texts, ensure_ascii=False), json.dumps({c: v[0] for c, v in LANGS.items()}))
    src = (SRC / "404.html").read_text(encoding="utf-8")
    for k in NOT_FOUND:
        if k not in src:
            raise SystemExit("src/404.html must contain %r" % k)
    src = src.replace("<!-- fonts:head -->", fonts_block(), 1).replace("<!-- i18n:404 -->", script, 1)
    note = "<!-- Generated by tools/build.py from src/404.html. Edit the source and i18n/*.json, then run the build. -->\n"
    return src.replace("<!doctype html>\n", "<!doctype html>\n" + note, 1)


def switch_block(code, page, tr):
    items = []
    for c, (hl, name, _) in LANGS.items():
        cur = ' aria-current="true"' if c == code else ""
        items.append('<li><a href="%s" hreflang="%s" lang="%s" data-lang="%s"%s>%s</a></li>'
                     % (page_url(c, page), hl, hl, c, cur, name))
    return ('<details class="lang"><summary aria-label="%s: %s">%s</summary><ul>%s</ul></details>'
            % (html.escape(tr("Language")), LANGS[code][1], code.upper(), "".join(items)))


# The game has no Dutch; its names for the other languages are stored under these keys in data/maps.json.
MAP_LANG = {"pt": "pt-BR", "zh": "zh-Hans", "nl": "en"}
_maps = {}


def maps_data():
    if not _maps:
        _maps.update(json.loads((DATA / "maps.json").read_text(encoding="utf-8")))
    return _maps


def maps_grid(code, tr):
    """One block per map on the map styles page: its name in the game's language, then one picture per style."""
    data, key, out = maps_data(), MAP_LANG.get(code, code), []
    for n, m in enumerate(data["maps"]):
        name, realm = m["names"].get(key) or m["names"]["en"], m["realm"].get(key) or m["realm"]["en"]
        out.append('    <section class="set">\n      <div class="set-head"><h2>%s</h2><p>%s</p></div>\n      <ul class="grid">'
                   % (html.escape(name, quote=False), html.escape(realm, quote=False)))
        for style, label in zip(data["styles"], MAP_STYLES):
            pic = "%s-%s.webp" % (m["id"], style)
            lazy = ' loading="lazy"' if n else ""  # the first map is on screen at once
            out.append('        <li><a href="/img/maps/%s"><img src="/img/maps/t/%s" width="%d" height="%d" alt=""%s decoding="async"><b>%s</b></a></li>'
                       % (pic, pic, m["tw"], m["th"], lazy, html.escape(tr(label), quote=False)))
        out.append("      </ul>\n    </section>")
    return "\n".join(out)


def render(code, page, src, table):
    def tr(key):
        if code == "en":
            return key
        return table[key]

    def tr_text(raw):
        key = html.unescape(norm(raw))
        if not wanted(key):
            return raw
        lead = raw[: len(raw) - len(raw.lstrip())]
        tail = raw[len(raw.rstrip()):]
        return lead + html.escape(tr(key), quote=False) + tail

    def tr_tag(tag):
        if code == "en":
            return tag
        tag = ATTR.sub(lambda m: '%s="%s"' % (m.group(1), html.escape(tr(html.unescape(m.group(2))))
                                              if wanted(html.unescape(m.group(2))) else m.group(2)), tag)
        tag = META.sub(lambda m: m.group(1) + (html.escape(tr(html.unescape(m.group(2))))
                                               if wanted(html.unescape(m.group(2))) else m.group(2)) + m.group(3), tag)
        tag = re.sub(r'href="/((?:contact/|maps/)?(?:#[^"]*)?)"', lambda m: 'href="/%s/%s"' % (code, m.group(1)), tag)
        return tag

    def tr_script(part):
        def swap(m):
            data = json.loads(m.group(2))
            data = {k: (LANGS[code][2] if k == "locale" else tr(v)) for k, v in data.items()}
            return m.group(1) + json.dumps(data, ensure_ascii=False) + ";"
        return SCRIPT_S.sub(swap, part)

    out = []
    for part in TOKEN.split(src):
        if not part:
            continue
        low = part[:7].lower()
        if low.startswith("<script"):
            out.append(tr_script(part))
        elif low.startswith("<style"):
            out.append(part)
        elif part == "<!-- i18n:head -->":
            out.append(head_block(code, page))
        elif part == "<!-- i18n:switch -->":
            out.append(switch_block(code, page, tr))
        elif part == "<!-- maps:grid -->":
            out.append(maps_grid(code, tr))
        elif part == "<!-- fonts:head -->":
            out.append(fonts_block())
        elif part == "<!-- ld:json -->":
            out.append(ld_block(code, tr))
        elif part.startswith("<!--"):
            out.append(part)
        elif part.startswith("<"):
            out.append(tr_tag(part))
        else:
            out.append(tr_text(part))
    text = "".join(out)
    text = text.replace('<html lang="en">', '<html lang="%s">' % LANGS[code][0], 1)
    url = SITE + page_url(code, page)
    text = re.sub(r'(<link rel="canonical" href=")[^"]*(")', r"\g<1>%s\g<2>" % url, text, count=1)
    text = re.sub(r'(<meta property="og:url" content=")[^"]*(")', r"\g<1>%s\g<2>" % url, text, count=1)
    note = "<!-- Generated by tools/build.py from src/%s. Edit the source and i18n/*.json, then run the build. -->\n" % page
    return text.replace("<!doctype html>\n", "<!doctype html>\n" + note, 1)


def main(argv):
    keys = all_keys()
    if "--template" in argv:
        print(json.dumps({k: "" for k in keys}, ensure_ascii=False, indent=2))
        return 0
    check = "--check" in argv
    problems, outputs, tables = [], {}, {}
    for code in LANGS:
        table = {}
        if code != "en":
            f = I18N / ("%s.json" % code)
            table = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
            missing = [k for k in keys if not str(table.get(k, "")).strip()]
            unused = [k for k in table if k not in keys]
            if missing:
                problems.append("%s: %d missing, e.g. %r" % (f.name, len(missing), missing[0]))
                continue
            if unused:
                print("note: %s has %d unused keys, e.g. %r" % (f.name, len(unused), unused[0]))
            for k in keys:  # a placeholder must survive the translation
                if k.count("%s") != table[k].count("%s"):
                    problems.append("%s: %%s in %r" % (f.name, k))
        tables[code] = table
        for page in PAGES:
            src = (SRC / page).read_text(encoding="utf-8")
            dest = ROOT / page if code == "en" else ROOT / code / page
            outputs[dest] = render(code, page, src, table)
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1
    outputs[ROOT / "404.html"] = not_found(tables)
    outputs[ROOT / "sitemap.xml"] = sitemap()
    outputs[ROOT / "robots.txt"] = robots()
    stale = []
    for dest, text in outputs.items():
        if check:
            if not dest.exists() or dest.read_text(encoding="utf-8") != text:
                stale.append(str(dest.relative_to(ROOT)))
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(text, encoding="utf-8")
    if stale:
        print("out of date, run tools/build.py: " + ", ".join(stale), file=sys.stderr)
        return 1
    print("%d files %s, %d texts per language" % (len(outputs), "up to date" if check else "written", len(keys)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
