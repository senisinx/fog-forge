#!/usr/bin/env python3
"""Build the language versions of fogforge.app.

The English pages in src/ are the source. Every text in them (text between tags, alt, aria-label,
data-alt, title, the page description and the texts in the `var S = {...}` line of the scripts) is a key;
i18n/<code>.json maps each key to its translation. The build writes

    index.html, contact/index.html           English (from src/ as is)
    <code>/index.html, <code>/contact/...    every other language

and adds the language menu, hreflang links and, on the English pages, the redirect to the browser's language.

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
PAGES = ["index.html", "contact/index.html"]

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
    "Fog Forge", "Fog", "Forge", "Fog Scout", "Fog Translate", "GitHub", "Discord", "Claude", "Gemini", "Ollama",
    "senisin", "github.com/senisinx", "hens333.com/callouts", "DBD Map Overlay", "fog-scout", "fog-translate",
}
# Keys that are not text in src/ but made by this build.
EXTRA = ["Language"]

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
    return base + ("contact/" if page.startswith("contact/") else "")


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


def switch_block(code, page, tr):
    items = []
    for c, (hl, name, _) in LANGS.items():
        cur = ' aria-current="true"' if c == code else ""
        items.append('<li><a href="%s" hreflang="%s" lang="%s" data-lang="%s"%s>%s</a></li>'
                     % (page_url(c, page), hl, hl, c, cur, name))
    return ('<details class="lang"><summary aria-label="%s: %s">%s</summary><ul>%s</ul></details>'
            % (html.escape(tr("Language")), LANGS[code][1], code.upper(), "".join(items)))


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
        tag = re.sub(r'href="/((?:contact/)?(?:#[^"]*)?)"', lambda m: 'href="/%s/%s"' % (code, m.group(1)), tag)
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
    problems, outputs = [], {}
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
        for page in PAGES:
            src = (SRC / page).read_text(encoding="utf-8")
            dest = ROOT / page if code == "en" else ROOT / code / page
            outputs[dest] = render(code, page, src, table)
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1
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
    print("%d pages %s, %d texts per language" % (len(outputs), "up to date" if check else "written", len(keys)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
