// Historical builder is retained for provenance; current UI publication is owned by v10.
{
  console.error('Historical UI writes are disabled. From the repository root, follow qdao_ui_style_recut_v10/README.md: extract_art.py, build_common_legacy.py, build_attributes.py, build_composites.mjs, validate_staged.py, then publish_staged.py --apply.');
  process.exit(process.argv.includes('--help') ? 0 : 1);
}

/** 五行奇谈 · 主城三入口 HUD. Only writes hud/* and source/04_main_city_hud.png. */
import fs from 'node:fs/promises';
// Windows viewers can briefly hold a generated asset while it is refreshed.
const rawWriteFile = fs.writeFile.bind(fs);
fs.writeFile = async (...params) => {
  for (let attempt=0;;attempt++) {
    try { return await rawWriteFile(...params); }
    catch (error) {
      if (attempt>=12 || !['UNKNOWN','EBUSY','EPERM'].includes(error.code)) throw error;
      await new Promise(resolve=>setTimeout(resolve,250));
    }
  }
};

import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
const root = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(root, '../..');
const require = createRequire(import.meta.url);
const args = process.argv.slice(2);
if (args.includes('--help')) { console.log('node build.mjs [--sharp <installed sharp directory>]\nBuilds a transparent three-button HUD and composites it onto the unchanged city preview. No network calls.'); process.exit(0); }
const i = args.indexOf('--sharp');
if (i >= 0 && !args[i + 1]) throw new Error('--sharp requires an installed package directory');
let sharp;
for (const candidate of [i >= 0 ? args[i + 1] : null, 'sharp', path.join(os.homedir(), '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp')].filter(Boolean)) { try { sharp = require(candidate); break; } catch {} }
if (!sharp) throw new Error('Sharp unavailable; pass --sharp <installed package directory>. This script does not download packages.');
const backgroundPath = path.join(repo, 'qdao_chibi_game_pack_v4/preview-main-city_2560x1080.png');
const background = await fs.readFile(backgroundPath);
const sha = buffer => crypto.createHash('sha256').update(buffer).digest('hex');
const backgroundHash = sha(background);
const metadata = await sharp(background).metadata();
if (metadata.width !== 2560 || metadata.height !== 1080) throw new Error('Expected immutable 2560 × 1080 city preview');
const skinPath = path.resolve(root, '../components/svg/primary_button_normal.svg');
const skinSource = await fs.readFile(skinPath, 'utf8');
if (!/width="460" height="112"/.test(skinSource)) throw new Error('Unexpected source component dimensions');
const originalBody = skinSource.replace(/^<svg\b[^>]*>/, '').replace(/<\/svg>\s*$/, '').replace(/<title>[\s\S]*?<\/title>/, '');
const font = 'Microsoft YaHei,Noto Sans CJK SC,Source Han Sans SC,sans-serif';
const buttons = [
  { id: 'battle', label: '战斗', x: 2160, y: 176, width: 336, height: 81.6 },
  { id: 'spectate', label: '观战', x: 2160, y: 280, width: 336, height: 81.6 },
  { id: 'character', label: '角色', x: 2160, y: 384, width: 336, height: 81.6 }
];
const skins = buttons.map(b => {
  // Prefix gradient IDs per instance; keep every source geometry coordinate unchanged.
  const body = originalBody.replace(/id="([^"]+)"/g, (_, id) => `id="${b.id}_${id}"`).replace(/url\(#([^)]+)\)/g, (_, id) => `url(#${b.id}_${id})`);
  return `<g id="skin_${b.id}" transform="translate(${b.x} ${b.y}) scale(${b.width / 460})">${body}</g>`;
}).join('');
const labels = buttons.map(b => `<text id="label_${b.id}" x="${b.x + b.width / 2}" y="${b.y + b.height / 2 - 1}" text-anchor="middle" dominant-baseline="central" font-family="${font}" font-size="36" font-weight="600" fill="#FFF7DE">${b.label}</text>`).join('');
const svg = (body, title) => `<svg xmlns="http://www.w3.org/2000/svg" width="2560" height="1080" viewBox="0 0 2560 1080" role="img"><title>${title}</title>${body}</svg>`;
const sources = {
  hud_skin: svg(`<g id="button_skins">${skins}</g>`, '五行奇谈 主城 HUD 无文字控件层'),
  hud_labels: svg(`<g id="native_labels">${labels}</g>`, '五行奇谈 主城 HUD 独立文字层：战斗、观战、角色'),
  hud_overlay: svg(`<g id="button_skins">${skins}</g><g id="native_labels">${labels}</g>`, '五行奇谈 主城 HUD：战斗、观战、角色')
};
for (const [name, source] of Object.entries(sources)) {
  await fs.writeFile(path.join(root, `${name}.svg`), source, 'utf8');
  await fs.writeFile(path.join(root, `${name}.png`), await sharp(Buffer.from(source)).png({ compressionLevel: 9 }).toBuffer());
}
const overlay = await fs.readFile(path.join(root, 'hud_overlay.png'));
const fullPath = path.resolve(root, '../source/04_main_city_hud.png');
await fs.writeFile(fullPath, await sharp(background).composite([{ input: overlay, left: 0, top: 0 }]).removeAlpha().png({ compressionLevel: 9 }).toBuffer());
const originalRaw = await sharp(background).removeAlpha().raw().toBuffer();
const composedRaw = await sharp(fullPath).removeAlpha().raw().toBuffer();
const overlayRaw = await sharp(overlay).ensureAlpha().raw().toBuffer();
let unchangedOutside = true, changedPixels = 0, overlayPixels = 0;
for (let px = 0; px < 2560 * 1080; px++) {
  const differs = originalRaw[px * 3] !== composedRaw[px * 3] || originalRaw[px * 3 + 1] !== composedRaw[px * 3 + 1] || originalRaw[px * 3 + 2] !== composedRaw[px * 3 + 2];
  if (differs) changedPixels++;
  if (overlayRaw[px * 4 + 3] > 0) overlayPixels++;
  else if (differs) unchangedOutside = false;
}
if (!unchangedOutside) throw new Error('Background pixels changed outside the overlay');
if (sha(await fs.readFile(backgroundPath)) !== backgroundHash) throw new Error('Background source hash changed');
const checks = [];
for (const name of Object.keys(sources)) {
  const meta = await sharp(path.join(root, `${name}.png`)).metadata();
  const stats = await sharp(path.join(root, `${name}.png`)).stats();
  if (meta.width !== 2560 || meta.height !== 1080 || !meta.hasAlpha || stats.channels[3].min !== 0 || stats.channels[3].max !== 255) throw new Error(`Invalid transparent layer ${name}`);
  checks.push({ file: `${name}.png`, size: [2560, 1080], rgba: true, alpha_range: [0, 255] });
}
const placement = {
  product: '五行奇谈', version: 5, canvas: { width: 2560, height: 1080 },
  source_background: { path: '../../qdao_chibi_game_pack_v4/preview-main-city_2560x1080.png', sha256: backgroundHash, unchanged: true, resampled: false },
  source_component: { path: '../components/svg/primary_button_normal.svg', sha256: sha(Buffer.from(skinSource)), size: [460, 112], modified: false },
  layout: { anchor: 'right-top', right_margin: 64, top: 176, button_gap: 22.4, uniform_skin_scale: 336 / 460, button_height_exact: 81.6, center_city_and_hero_uncovered: true },
  text: { native_layer: 'hud_labels.svg', skin_without_labels: 'hud_skin.svg', font_family: font, font_size: 36, weight: 600, color: '#FFF7DE', separate_from_skin: true },
  buttons: buttons.map(b => ({ ...b, state: 'normal', label_source: 'existing repository movement screenshot', action_binding: null })),
  artifacts: { overlay_svg: 'hud_overlay.svg', overlay_png: 'hud_overlay.png', skin_svg: 'hud_skin.svg', skin_png: 'hud_skin.png', labels_svg: 'hud_labels.svg', labels_png: 'hud_labels.png', composed_preview: '../source/04_main_city_hud.png', html: 'preview.html' },
  validation: { renderer: { sharp: sharp.versions.sharp, vips: sharp.versions.vips }, layers: checks, background_sha_unchanged: true, exact_original_pixels_outside_overlay: unchangedOutside, overlay_pixels: overlayPixels, changed_composite_pixels: changedPixels },
  scope: 'Visual HUD only. These are the three actions observed in the baseline 60134a6 movement diagnostic screenshot, which was removed after final asset validation. No other screens, interaction logic, or action bindings are implemented.'
};
await fs.writeFile(path.join(root, 'placement.json'), JSON.stringify(placement, null, 2) + '\n', 'utf8');
await fs.writeFile(path.join(root, 'preview.html'), `<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>五行奇谈 · 主城 HUD</title><style>body{margin:0;background:#173f35;color:#fff7de;font:16px/1.6 "Microsoft YaHei",sans-serif}header{padding:18px 32px;display:flex;gap:24px;align-items:center;flex-wrap:wrap}h1{margin:0;font-size:23px}p{margin:0;opacity:.85}.scene{position:relative;width:100%;aspect-ratio:2560/1080}.scene img{position:absolute;inset:0;width:100%;height:100%;display:block}a{color:#ead093}</style><header><h1>五行奇谈 · 主城 HUD</h1><p>战斗 / 观战 / 角色 · 三入口视觉预览</p><a href="placement.json">位置清单</a><a href="README.md">接入与重建</a></header><main class="scene"><img src="../../qdao_chibi_game_pack_v4/preview-main-city_2560x1080.png" alt="保留原像素的主城背景"><img src="hud_overlay.svg" alt="右侧竖排三个按钮：战斗、观战、角色"></main></html>`, 'utf8');
console.log(JSON.stringify({ layers: 3, transparent_svg: 3, transparent_png: 3, composite: 'source/04_main_city_hud.png', background_unchanged: true, exact_pixels_outside_overlay: true, buttons: buttons.map(b => b.label) }));
