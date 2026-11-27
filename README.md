# Fog Forge

Source of [fogforge.app](https://fogforge.app): the landing page for [Fog Scout](https://github.com/senisinx/fog-scout) and [Fog Translate](https://github.com/senisinx/fog-translate).

Static pages served by GitHub Pages, in the 13 languages Fog Translate translates into:
English, German, French, Spanish, Italian, Portuguese (Brazil), Polish, Russian, Turkish, Dutch,
Chinese (Simplified), Japanese and Korean. Screenshots and icons are in `img/`.

## Editing

The HTML in the repository root and in the language folders (`de/`, `fr/`, …) is **generated**. Do not edit it.

- `src/index.html` (start page), `src/scout/index.html`, `src/translate/index.html` (one page per tool),
  `src/maps/index.html`, `src/contact/index.html`: the English pages, the source of every language.
- `css/site.css`, `js/site.js`: the one stylesheet and the one script of every page (not translated; the texts the script
  shows are in `var S` of each page).
- `i18n/<code>.json`: one file per language. The English text is the key, the value its translation.
- `src/404.html`: the page for unknown addresses; one page for all languages, its three texts are in `i18n/` too.
- `tools/build.py`: writes all pages, `404.html`, `sitemap.xml` and `robots.txt` (needs only Python 3), plus the fonts
  block and the JSON-LD of both tools.
- `fonts/`: Archivo as a variable WOFF2 with weight and width axis, latin and latin-ext, from Fontsource, under the SIL
  Open Font License (`fonts/OFL-archivo.txt`). The page loads nothing from Google.
- Design: fog over a match. Deep slate (`#0e1418`), mist for text (`#d4dfdf`) and the amber of the app icons
  (`#eaa25d`) for buttons and links. One family, Archivo; headlines use its wide cut. One moment of motion: on the start
  page the fog clears once over the game picture (off with "reduce motion"). The start page is short: hero, one block per
  tool with three points, fair play, download. Everything else is on the tool pages `/scout/` and `/translate/`, with a
  bar to jump between their sections.
- Game picture of the start page: `img/match-rotten-fields.webp`, also as `-960` and `-1600` for `srcset`; after a new
  screenshot, make both sizes (WebP, quality 80). It is also the picture at the top of `/scout/`. The other
  `img/match-*.webp` are not shown at the moment.
- Pictures of the programs (`img/maps.webp`, `overlay`, `statistics`, `recordings`, `calculator`, `overview`, `server`,
  `overlay-system`, `stats-rounds`, `stats-waiting`, `settings`, `setup`, `translate-app`): screenshots of the real windows with made-up data, 1560×1180 for Fog Scout. No real rounds, pings
  or keys may be in them.
- `img/score.webp`: the score tracker of Fog Scout in its three looks, drawn by `fogscout.scoreview.picture` with made-up points and Fog Scout's own icons (never the game's). After a change to the look, draw it again the same way.
- `data/maps.json`, `img/maps/`: three callout maps in the six map styles for `/maps/`, made from Fog Scout. Do not edit
  them; run `python3 tools/import_maps.py <path to a fog-scout checkout>` to show other maps or after a change to the
  styles (needs Pillow, NumPy and OpenCV), then the build.

After a change:

```bash
python3 tools/build.py
```

New or changed English text has to be added to every `i18n/*.json`; the build stops and names the
missing texts. `python3 tools/build.py --template` prints all keys, `--check` fails if a page is out of date,
`--only en` builds only the English pages (a preview while translations are still missing; never push that state).

## Icons

`tools/icons/` is the one source of the icons of Fog Forge, Fog Scout, Fog Translate and Fog Launch: one family
(the same tile, glow, fog and amber, one picture each) and a simpler variant for 16–32 px. After a change:

```bash
python3 tools/icons/icons.py
```

```bash
node tools/icons/render.mjs
```

```bash
python3 tools/icons/icons.py tidy
```

```bash
python3 tools/icons/icons.py site
```

The first writes the SVGs, the second renders every size to `tools/icons/png/` (needs Playwright with Chromium),
the third clears the faint edge Chromium leaves in the transparent corners, the fourth copies the Fog Forge icon into `img/` (`icon.svg` is the small variant for the tab and the header).
The programs ship the PNGs from `tools/icons/png/`; copy them into each repository. Then redraw the link preview.

## Link preview

`img/og.jpg` (1200×630) is the picture Discord and other sites show for a link to the page. Its source is
`tools/og.html`, in the look of the start page; it uses the fonts in `fonts/` and loads nothing from the net. Render it
at 1200×630 with a Chromium browser without a window, for example Edge on Windows, and save the PNG as JPEG
(quality 88) to `img/og.jpg`:

```bash
msedge --headless=new --hide-scrollbars --force-device-scale-factor=1 --window-size=1200,630 --screenshot=og.png tools/og.html
```

After a change, raise `?v=` at `og:image` in the `src/` pages so that sites fetch the new picture.

English visitors whose browser prefers one of the other languages are sent to that version once;
a choice in the language menu is remembered.
