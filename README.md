# Fog Forge

Source of [fogforge.app](https://fogforge.app): the landing page for [Fog Scout](https://github.com/senisinx/fog-scout) and [Fog Translate](https://github.com/senisinx/fog-translate).

Static pages served by GitHub Pages, in the 13 languages Fog Translate translates into:
English, German, French, Spanish, Italian, Portuguese (Brazil), Polish, Russian, Turkish, Dutch,
Chinese (Simplified), Japanese and Korean. Screenshots and icons are in `img/`.

## Editing

The HTML in the repository root and in the language folders (`de/`, `fr/`, …) is **generated**. Do not edit it.

- `src/index.html`, `src/contact/index.html`, `src/maps/index.html`: the English pages, the source of every language.
- `i18n/<code>.json`: one file per language. The English text is the key, the value its translation.
- `tools/build.py`: writes all pages (needs only Python 3).
- `data/maps.json`, `img/maps/`: three callout maps in the six map styles for `/maps/`, made from Fog Scout. Do not edit
  them; run `python3 tools/import_maps.py <path to a fog-scout checkout>` to show other maps or after a change to the
  styles (needs Pillow, NumPy and OpenCV), then the build.

After a change:

```bash
python3 tools/build.py
```

New or changed English text has to be added to every `i18n/*.json`; the build stops and names the
missing texts. `python3 tools/build.py --template` prints all keys, `--check` fails if a page is out of date.

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
`tools/og.html`; open it in a browser window of 1200×630 and save a screenshot as `img/og.jpg`. After a change,
raise `?v=` at `og:image` in the three `src/` pages so that sites fetch the new picture.

English visitors whose browser prefers one of the other languages are sent to that version once;
a choice in the language menu is remembered.
