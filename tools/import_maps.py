#!/usr/bin/env python3
"""Copy the callout maps of Fog Scout into this site.

    python3 tools/import_maps.py <path to a fog-scout checkout>

Reads maps.json and maps/ there and writes

    data/maps.json          realms and maps with their names per language and their pictures
    img/maps/<slug>.webp    the pictures as they are (a .gif stays a .gif)
    img/maps/t/<slug>.webp  small pictures for the grid

Run it again when Fog Scout gets new maps, then run tools/build.py. Needs Pillow.
"""
import json
import shutil
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "img" / "maps"
THUMB_W = 360
ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII"]


def main(argv):
    if len(argv) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    src = Path(argv[0])
    cat = json.loads((src / "maps.json").read_text(encoding="utf-8"))
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "t").mkdir(parents=True)
    realms, maps = [], []
    for m in cat["maps"]:
        if m["realm"] not in realms:
            realms.append(m["realm"])
        many = len(m["variants"]) > 1
        for n, rel in sorted(m["variants"].items(), key=lambda kv: int(kv[0])):
            slug = "%s-%s" % (m["id"], n) if many else m["id"]
            path = src / "maps" / rel
            full = slug + path.suffix.lower()
            shutil.copyfile(path, OUT / full)
            im = Image.open(path)
            im.seek(0)
            im = im.convert("RGBA")
            w, h = im.size
            th = im.resize((THUMB_W, round(h * THUMB_W / w)), Image.LANCZOS)
            th.save(OUT / "t" / (slug + ".webp"), "WEBP", quality=82, method=6)
            maps.append({"slug": slug, "file": full, "layout": ROMAN[int(n)] if many else "",
                         "realm": realms.index(m["realm"]), "names": m["names"], "w": w, "h": h,
                         "tw": th.width, "th": th.height})
    data = {"_info": "Made by tools/import_maps.py from maps.json of Fog Scout. Do not edit.",
            "realms": [cat["realms"][r] for r in realms], "maps": maps}
    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "data" / "maps.json").write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("%d pictures of %d maps in %d realms" % (len(maps), len(cat["maps"]), len(realms)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
