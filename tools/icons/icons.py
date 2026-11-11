"""The icons of Fog Forge, Fog Scout, Fog Translate and Fog Launch: one family, one source.

    python3 tools/icons/icons.py           writes tools/icons/<name>.svg and <name>-small.svg
    node tools/icons/render.mjs            renders them to tools/icons/png/ (needs Playwright with Chromium)
    python3 tools/icons/icons.py tidy      clears the faint edge Chromium leaves outside the rounded tile
    python3 tools/icons/icons.py site      copies the Fog Forge icon into img/
    python3 tools/icons/icons.py ico NAME FILE   writes a Windows .ico (16-256 px) for NAME

All four share the tile (dark ground with depth, a warm glow behind the picture, fog at the bottom, a sheen on
top) and the amber; each has its own picture: anvil, compass, speech bubbles, play arrows. The small variant
(16-32 px: taskbar, Explorer, browser tab) leaves out the fog, the spark and the blur and draws the picture
larger, so it stays sharp. The programs ship the rendered PNGs; change the pictures here and copy them over.
"""
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SMALL_SIZES = (16, 20, 24, 32)
LARGE_SIZES = (40, 48, 64, 128, 180, 256, 512)
NAMES = ("fog-forge", "fog-scout", "fog-translate", "fog-launch")

DEFS = """
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#22303a"/><stop offset=".55" stop-color="#141c21"/><stop offset="1" stop-color="#0b0f12"/>
  </linearGradient>
  <radialGradient id="glow" cx=".5" cy=".42" r=".5">
    <stop offset="0" stop-color="#e39a55" stop-opacity=".30"/><stop offset="1" stop-color="#e39a55" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="amber" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#f7c58c"/><stop offset=".45" stop-color="#eaa25d"/><stop offset="1" stop-color="#c8743a"/>
  </linearGradient>
  <linearGradient id="amberDeep" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#c98447"/><stop offset="1" stop-color="#8e4f25"/>
  </linearGradient>
  <linearGradient id="mist" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#e3ecec"/><stop offset="1" stop-color="#a9b9bb"/>
  </linearGradient>
  <linearGradient id="sheen" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fff" stop-opacity=".10"/><stop offset=".35" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="fade" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".18" stop-color="#fff"/>
    <stop offset=".82" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <mask id="fadeMask"><rect width="512" height="512" fill="url(#fade)"/></mask>
  <clipPath id="tile"><rect width="512" height="512" rx="114"/></clipPath>
  <filter id="soft" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="7"/></filter>
  <filter id="shadow" x="-30%" y="-30%" width="160%" height="170%">
    <feDropShadow dx="0" dy="10" stdDeviation="12" flood-color="#000" flood-opacity=".55"/>
  </filter>
  <filter id="sparkGlow" x="-100%" y="-100%" width="300%" height="300%">
    <feGaussianBlur stdDeviation="9" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
</defs>"""

FOG = """
<g clip-path="url(#tile)" mask="url(#fadeMask)">
  <path d="M-10 418 C 70 392, 140 446, 230 418 S 390 390, 522 416 L 522 466 C 400 442, 330 484, 230 462 S 60 438, -10 466 Z"
        fill="#c9d6d6" opacity=".30" filter="url(#soft)"/>
  <path d="M34 424 C 112 400, 172 450, 256 424 S 400 398, 478 422" fill="none" stroke="#dbe5e5" stroke-width="18"
        stroke-linecap="round" opacity=".80"/>
  <path d="M90 466 C 154 446, 200 486, 268 466 S 384 446, 434 464" fill="none" stroke="#8fa2a5" stroke-width="14"
        stroke-linecap="round" opacity=".70"/>
</g>"""


def tile(glyph, fog=True, spark=None):
    sparkle = ""
    if spark:
        x, y, r = spark
        sparkle = (f'<path filter="url(#sparkGlow)" fill="#fbe0bd" d="M{x} {y-r} L{x+r*.24} {y-r*.24} L{x+r} {y} '
                   f'L{x+r*.24} {y+r*.24} L{x} {y+r} L{x-r*.24} {y+r*.24} L{x-r} {y} L{x-r*.24} {y-r*.24} Z"/>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">{DEFS}
<rect width="512" height="512" rx="114" fill="url(#bg)"/>
<rect width="512" height="512" rx="114" fill="url(#glow)"/>
{FOG if fog else ""}
<g filter="url(#shadow)"><g transform="translate(0 -6)">{glyph}</g></g>
{sparkle}
<rect width="512" height="512" rx="114" fill="url(#sheen)"/>
<rect x="3" y="3" width="506" height="506" rx="111" fill="none" stroke="#fff" stroke-opacity=".07" stroke-width="6"/>
</svg>"""


def small(glyph):
    """16–32 px: no fog, no blur, the glyph alone and larger, with a crisp edge."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">{DEFS}
<rect width="512" height="512" rx="114" fill="url(#bg)"/>
{glyph}
<rect x="6" y="6" width="500" height="500" rx="108" fill="none" stroke="#fff" stroke-opacity=".10" stroke-width="12"/>
</svg>"""


ANVIL = """<path fill="url(#amber)" d="M92 150 H388 V214 H330 C306 214 292 228 292 252 V284 L340 316 V352 H170 V316
L218 284 V252 C218 228 204 214 180 214 H168 C128 214 102 188 92 150 Z"/>
<path fill="#fff" opacity=".22" d="M92 150 H388 V162 H98 Z"/>"""
ANVIL_SMALL = """<g transform="translate(-6 34) scale(1.06)"><path fill="url(#amber)" d="M80 140 H410 V218 H340 C316 218 300 234 300 258
V292 L350 326 V372 H162 V326 L212 292 V258 C212 234 196 218 172 218 H160 C116 218 90 186 80 140 Z"/></g>"""

COMPASS = """<g transform="translate(256 228) scale(.86) translate(-256 -256)"><path fill="url(#mist)" d="M256 136 L292 256 L256 376 L220 256 Z" transform="rotate(90 256 256)"/>
<path fill="url(#amber)" d="M256 92 L296 256 H216 Z"/>
<path fill="url(#mist)" d="M216 256 H296 L256 420 Z"/>
<circle cx="256" cy="256" r="34" fill="#141c21"/><circle cx="256" cy="256" r="15" fill="#f4dcbc"/></g>"""
COMPASS_SMALL = """<path fill="#c9d6d6" d="M70 256 L256 214 L442 256 L256 298 Z"/>
<path fill="url(#amber)" d="M256 48 L310 256 H202 Z"/><path fill="#e3ecec" d="M202 256 H310 L256 464 Z"/>
<circle cx="256" cy="256" r="44" fill="#141c21"/><circle cx="256" cy="256" r="20" fill="#f4dcbc"/>"""

BUBBLES = """<g transform="translate(256 220) scale(.92) translate(-256 -256)"><path fill="url(#mist)" d="M96 96 H300 A34 34 0 0 1 334 130 V226 A34 34 0 0 1 300 260 H168 L120 304 L128 260 H96
A34 34 0 0 1 62 226 V130 A34 34 0 0 1 96 96 Z"/>
<g stroke="#2a363c" stroke-width="20" stroke-linecap="round"><path d="M110 150 H262"/><path d="M110 206 H210"/></g>
<path fill="url(#amber)" stroke="#141c21" stroke-width="14" d="M214 196 H418 A36 36 0 0 1 454 232 V328 A36 36 0 0 1 418 364
H392 L400 410 L350 364 H214 A36 36 0 0 1 178 328 V232 A36 36 0 0 1 214 196 Z"/>
<g fill="none" stroke="#2b1a0b" stroke-width="24" stroke-linecap="round" stroke-linejoin="round">
<path d="M246 280 H384"/><path d="M342 240 L386 280 L342 320"/></g></g>"""
BUBBLES_SMALL = """<path fill="#c9d6d6" d="M70 70 H310 A40 40 0 0 1 350 110 V220 A40 40 0 0 1 310 260 H150 L96 310 L106 260 H70
A40 40 0 0 1 30 220 V110 A40 40 0 0 1 70 70 Z"/>
<path fill="url(#amber)" stroke="#141c21" stroke-width="22" d="M196 196 H442 A40 40 0 0 1 482 236 V350 A40 40 0 0 1 442 390
H410 L420 446 L360 390 H196 A40 40 0 0 1 156 350 V236 A40 40 0 0 1 196 196 Z"/>
<g fill="none" stroke="#2b1a0b" stroke-width="34" stroke-linecap="round" stroke-linejoin="round">
<path d="M222 293 H400"/><path d="M350 245 L402 293 L350 341"/></g>"""

PLAY = """<path fill="url(#amberDeep)" stroke="url(#amberDeep)" stroke-width="30" stroke-linejoin="round" d="M98 126 V318 L250 222 Z"/>
<path fill="url(#amber)" stroke="url(#amber)" stroke-width="30" stroke-linejoin="round" d="M210 110 V334 L388 222 Z"/>
<path fill="#fff" opacity=".18" d="M196 104 L392 216 L384 222 L210 124 Z"/>"""
PLAY_SMALL = """<path fill="#a0602d" stroke="#a0602d" stroke-width="40" stroke-linejoin="round" d="M60 120 V392 L262 256 Z"/>
<path fill="url(#amber)" stroke="url(#amber)" stroke-width="40" stroke-linejoin="round" d="M200 100 V412 L452 256 Z"/>"""

ICONS = {
    "fog-forge": (ANVIL, ANVIL_SMALL, (322, 86, 40)),
    "fog-scout": (COMPASS, COMPASS_SMALL, (404, 112, 30)),
    "fog-translate": (BUBBLES, BUBBLES_SMALL, None),
    "fog-launch": (PLAY, PLAY_SMALL, (420, 112, 38)),
}


def png(name, size):
    small = size in SMALL_SIZES
    return HERE / "png" / f"{name}{'-small' if small else ''}-{size}.png"


def write_svgs():
    for name, (big, little, spark) in ICONS.items():
        (HERE / f"{name}.svg").write_text(tile(big, spark=spark), encoding="utf-8")
        (HERE / f"{name}-small.svg").write_text(small(little), encoding="utf-8")


def write_ico(name, target):
    from PIL import Image

    pictures = [Image.open(png(name, size)).convert("RGBA") for size in (16, 20, 24, 32, 40, 48, 64, 128, 256)]
    pictures[-1].save(target, format="ICO", sizes=[p.size for p in pictures], append_images=pictures[:-1])


def tidy():
    """Chromium's antialiasing leaves an alpha of 1-3 of 255 in pixels outside the rounded tile (the transparent
    corners); clear it, so the corners are really transparent."""
    from PIL import Image

    for file in sorted((HERE / "png").glob("*.png")):
        with Image.open(file) as picture:
            img = picture.convert("RGBA")
        alpha = img.getchannel("A").point(lambda a: 0 if a <= 3 else a)
        clean = Image.new("RGBA", img.size, (0, 0, 0, 0))
        clean.paste(img, mask=alpha.point(lambda a: 255 if a else 0))
        clean.putalpha(alpha)
        clean.save(file, optimize=True)


def copy_site():
    img = ROOT / "img"
    shutil.copyfile(HERE / "fog-forge-small.svg", img / "icon.svg")
    shutil.copyfile(png("fog-forge", 32), img / "favicon-32.png")
    shutil.copyfile(png("fog-forge", 180), img / "apple-touch-icon.png")
    shutil.copyfile(png("fog-forge", 512), img / "icon-512.png")


if __name__ == "__main__":
    command = sys.argv[1:] or ["svg"]
    if command[0] == "svg":
        write_svgs()
    elif command[0] == "tidy":
        tidy()
    elif command[0] == "site":
        copy_site()
    elif command[0] == "ico" and len(command) == 3:
        write_ico(command[1], command[2])
    else:
        sys.exit(__doc__)
