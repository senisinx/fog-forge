// Renders tools/icons/*.svg to tools/icons/png/ at every size the programs and the site use.
// Each size is drawn by Chromium from the vector picture, not scaled from a bigger PNG.
//     node tools/icons/render.mjs
import { createRequire } from 'module';
import { readFileSync, readdirSync, mkdirSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const { chromium } = createRequire(import.meta.url)('playwright');
const here = dirname(fileURLToPath(import.meta.url));
const SMALL = [16, 20, 24, 32];
const LARGE = [40, 48, 64, 128, 180, 256, 512];

mkdirSync(join(here, 'png'), { recursive: true });
const browser = await chromium.launch();
for (const file of readdirSync(here).filter(f => f.endsWith('.svg'))) {
  const svg = readFileSync(join(here, file), 'utf8');
  const base = file.slice(0, -4);
  for (const size of base.endsWith('-small') ? SMALL : LARGE) {
    const page = await browser.newPage({ viewport: { width: size, height: size } });
    await page.setContent(`<style>html,body{margin:0;background:transparent}svg{display:block;width:${size}px;height:${size}px}</style>${svg}`);
    await page.screenshot({ path: join(here, 'png', `${base}-${size}.png`), omitBackground: true });
    await page.close();
  }
}
await browser.close();
