#!/usr/bin/env python3
"""Make the pictures of the map styles page from a Fog Scout checkout.

    python3 tools/import_maps.py <path to a fog-scout checkout>

Takes the maps named in SHOWN from maps.json and maps/ there, draws each in the six map styles with Fog Scout's own
code (fogscout/mapstyle.py) and writes

    data/maps.json                  the maps with their names per language
    img/maps/<map>-<style>.webp     the pictures
    img/maps/t/<map>-<style>.webp   small pictures for the page

Run it again to show other maps or after a change to the styles, then run tools/build.py.
Needs Pillow, NumPy and OpenCV (opencv-python-headless), as Fog Scout does.
"""
import json
import shutil
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "img" / "maps"
THUMB_W = 360
SHOWN = [("rotten-fields", "1"), ("dead-dawg-saloon", "1"), ("groaning-storehouse", "1")]   # map id, layout
STYLES = ["classic", "dark", "grey", "grey_edge", "lilac", "lilac_glass"]                    # as in the app's menu


def main(argv):
    if len(argv) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    src = Path(argv[0]).resolve()
    sys.path.insert(0, str(src))
    from fogscout import mapstyle
    cat = json.loads((src / "maps.json").read_text(encoding="utf-8"))
    by_id = {m["id"]: m for m in cat["maps"]}
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "t").mkdir(parents=True)
    maps = []
    for map_id, layout in SHOWN:
        m = by_id[map_id]
        im = Image.open(src / "maps" / m["variants"][layout]).convert("RGBA")
        for style in STYLES:
            pic = im if style == "classic" else mapstyle.restyle(im, style=style)
            name = "%s-%s.webp" % (map_id, style.replace("_", "-"))
            pic.save(OUT / name, "WEBP", quality=90, method=4)
            w, h = pic.size
            pic.resize((THUMB_W, round(h * THUMB_W / w)), Image.LANCZOS).save(OUT / "t" / name, "WEBP", quality=82, method=4)
        maps.append({"id": map_id, "names": m["names"], "realm": cat["realms"][m["realm"]], "w": w, "h": h,
                     "tw": THUMB_W, "th": round(h * THUMB_W / w)})
    data = {"_info": "Made by tools/import_maps.py from Fog Scout. Do not edit.",
            "styles": [s.replace("_", "-") for s in STYLES], "maps": maps}
    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "data" / "maps.json").write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("%d maps in %d styles" % (len(maps), len(STYLES)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
