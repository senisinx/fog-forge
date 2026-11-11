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
- `data/maps.json`, `img/maps/`: the callout maps on `/maps/`, copied from Fog Scout. Do not edit them; run
  `python3 tools/import_maps.py <path to a fog-scout checkout>` when Fog Scout gets new maps (needs Pillow), then the build.

After a change:

```bash
python3 tools/build.py
```

New or changed English text has to be added to every `i18n/*.json`; the build stops and names the
missing texts. `python3 tools/build.py --template` prints all keys, `--check` fails if a page is out of date.

English visitors whose browser prefers one of the other languages are sent to that version once;
a choice in the language menu is remembered.
