// Historical builder is retained for provenance; current UI publication is owned by v10.
{
  console.error('Historical UI writes are disabled. From the repository root, follow qdao_ui_style_recut_v10/README.md: extract_art.py, build_common_legacy.py, build_attributes.py, build_composites.mjs, validate_staged.py, then publish_staged.py --apply.');
  process.exit(process.argv.includes('--help') ? 0 : 1);
}

/** 五行奇谈 · 原生 UI 控件。 Node >= 22; PNG export requires Sharp. */
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
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

const root = path.dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
const args = process.argv.slice(2);
if (args.includes('--help')) {
  console.log('node build.mjs [--sharp <installed-sharp-directory>] [--svg-only]\nWrites only inside this components directory. No downloads or external requests.');
  process.exit(0);
}
const svgOnly = args.includes('--svg-only');
const sharpArg = args.indexOf('--sharp');
if (sharpArg >= 0 && !args[sharpArg + 1]) throw new Error('--sharp requires a package directory');
let sharp;
if (!svgOnly) {
  const candidates = [args[sharpArg + 1], 'sharp', path.join(os.homedir(), '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp')].filter((v, i) => v && (i !== 0 || sharpArg >= 0));
  for (const candidate of candidates) { try { sharp = require(candidate); break; } catch {} }
  if (!sharp) throw new Error('Sharp is unavailable. Supply --sharp <installed-sharp-directory> or use --svg-only. No packages were downloaded.');
}
await fs.mkdir(path.join(root, 'svg'), { recursive: true });
if (!svgOnly) await fs.mkdir(path.join(root, 'png'), { recursive: true });

const palette = { jade: '#176C5F', jadeLight: '#438E78', ivory: '#FFF7DE', gold: '#C59645', wood: '#795638', ink: '#344D43', disabled: '#D7DBD1', disabledInk: '#536254' };
const assets = [];
const defs = `<defs>
  <linearGradient id="jade" x2="0" y2="1"><stop stop-color="#438E78"/><stop offset=".52" stop-color="#287660"/><stop offset="1" stop-color="#176C5F"/></linearGradient>
  <linearGradient id="ivory" x2="0" y2="1"><stop stop-color="#FFFBEF"/><stop offset="1" stop-color="#F3E7CB"/></linearGradient>
  <linearGradient id="gold" x2="0" y2="1"><stop stop-color="#F3DE9C"/><stop offset=".45" stop-color="#C59645"/><stop offset="1" stop-color="#9E7037"/></linearGradient>
  <linearGradient id="wood" x2="0" y2="1"><stop stop-color="#9A7350"/><stop offset="1" stop-color="#68462E"/></linearGradient>
  <linearGradient id="muted" x2="0" y2="1"><stop stop-color="#E7E9DD"/><stop offset="1" stop-color="#C7CFC3"/></linearGradient>
</defs>`;
const escape = s => String(s).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('"', '&quot;');
const svg = (w, h, body, title) => `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" role="img"><title>${escape(title)}</title>${defs}${body}</svg>`;
const round = (x, y, w, h, r, fill, stroke = 'none', sw = 0, extra = '') => `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${r}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}" ${extra}/>`;
const check = (x, y, size = 30, dark = false) => `<g transform="translate(${x} ${y}) scale(${size / 48})"><circle cx="24" cy="24" r="20" fill="${dark ? '#FFF7DE' : '#176C5F'}" stroke="#C59645" stroke-width="3"/><path d="m14 24 7 7 14-15" fill="none" stroke="${dark ? '#176C5F' : '#FFF7DE'}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></g>`;
const lock = (x, y, size = 30) => `<g transform="translate(${x} ${y}) scale(${size / 48})" fill="none" stroke="#536254" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><path d="M15 21v-7a9 9 0 0 1 18 0v7"/><rect x="9" y="20" width="30" height="23" rx="6" fill="#E7E9DD"/><circle cx="24" cy="29" r="2.2" fill="#536254" stroke="none"/><path d="M24 30v5"/></g>`;
const cloud = (x, y, scale = 1, flip = false, color = '#D8C38E', opacity = .5) => `<g transform="translate(${x} ${y}) scale(${flip ? -scale : scale} ${scale})" fill="none" stroke="${color}" stroke-width="2.1" stroke-linecap="round" opacity="${opacity}"><path d="M0 25h27c12 0 14-16 3-16-8 0-9 10-2 10h20c11 0 13-16 2-16-6 0-9 4-8 9M5 33h42c13 0 16-13 27-13 10 0 12 13 3 13H57M17 41h44"/></g>`;
const corner = (x, y, sx = 1, sy = 1, extent = 36) => `<g transform="translate(${x} ${y}) scale(${sx} ${sy})" fill="none" stroke="#E2C87D" stroke-width="2"><path d="M0 ${extent}V10Q0 0 10 0h${extent - 10}"/><path d="M7 ${extent - 7}V14q0-7 7-7h${extent - 21}"/><path d="m0 14 8-6 6-8"/></g>`;

function surface(w, h, state, kind) {
  const primary = kind === 'primary_button';
  const selected = state === 'selected';
  const disabled = state === 'disabled';
  const jade = !disabled && (primary || selected);
  const r = kind === 'search' ? 27 : kind.startsWith('server') ? 25 : kind === 'tab' ? 24 : 28;
  const outer = disabled ? '#A8B1A1' : 'url(#gold)';
  const fill = disabled ? 'url(#muted)' : jade ? 'url(#jade)' : 'url(#ivory)';
  let b = round(7, 12, w - 14, h - 16, r, '#543D2A', 'none', 0, 'opacity=".12"');
  b += round(5, 7, w - 10, h - 16, r + 2, disabled ? '#82907C' : 'url(#wood)');
  b += round(6, 5, w - 12, h - 17, r, outer);
  b += round(10, 9, w - 20, h - 25, Math.max(8, r - 4), fill, disabled ? '#8B9A86' : '#8D672F', 1);
  b += round(15, 14, w - 30, h - 35, Math.max(6, r - 9), 'none', disabled ? '#F1F1E4' : jade ? '#D9C790' : '#CFB57F', 1.3);
  b += `<path d="M${r + 8} 12H${w - r - 8}" stroke="#FFFADE" stroke-width="2" opacity="${disabled ? .45 : .7}" stroke-linecap="round"/>`;
  if (kind.startsWith('server')) {
    b += cloud(w - 103, h - 65, .82, false, jade ? '#DCC689' : '#D1BC8A', .36);
    b += `<path d="M${w - 145} 30v${h - 66}" stroke="${disabled ? '#9AA794' : '#C8B17D'}" opacity=".6"/>`;
  } else if (kind !== 'search') {
    b += cloud(w - 78, h - 56, .64, false, jade ? '#E5D39C' : '#C7B785', .3);
  }
  if (selected) {
    b += `<path d="M20 ${h / 2 - 13}v26" stroke="#F5DE92" stroke-width="4" stroke-linecap="round"/>`;
    b += check(kind === 'search' ? w - 49 : 30, (h - 40) / 2 - 2, 32, jade);
    b += `<path d="M38 ${h - 12}h24l-12-6z" fill="#EDD48B"/>`;
  }
  if (disabled) b += lock(kind === 'search' ? w - 49 : 30, (h - 40) / 2 - 2, 32);
  if (kind === 'search') b += `<g fill="none" stroke="${disabled ? '#697764' : selected ? '#FFF7DE' : '#795638'}" stroke-width="3.5" stroke-linecap="round"><circle cx="39" cy="${h / 2 - 5}" r="10"/><path d="m47 ${h / 2 + 3} 8 8"/></g>`;
  return b;
}

function panel(w, h, frame) {
  let b = round(9, 14, w - 18, h - 20, 43, '#523E2C', 'none', 0, 'opacity=".15"');
  b += round(6, 6, w - 12, h - 20, 40, frame ? 'url(#wood)' : 'url(#gold)');
  b += round(11, 10, w - 22, h - 29, 35, 'url(#gold)');
  b += round(17, 16, w - 34, h - 41, 30, frame ? 'url(#jade)' : 'url(#ivory)', '#8F703A', 1.5);
  b += round(frame ? 36 : 25, frame ? 35 : 24, w - (frame ? 72 : 50), h - (frame ? 80 : 57), frame ? 22 : 23, 'url(#ivory)', '#D9C18A', frame ? 3 : 1.5);
  if (frame) b += round(44, 43, w - 88, h - 96, 16, 'none', '#A68B54', 1);
  for (const [x, y, sx, sy] of [[27, 27, 1, 1], [w - 27, 27, -1, 1], [27, h - 37, 1, -1], [w - 27, h - 37, -1, -1]]) b += corner(x, y, sx, sy, frame ? 53 : 38);
  b += cloud(58, 61, 1, false, '#D4C59C', .33) + cloud(w - 58, h - 114, 1, true, '#D4C59C', .33);
  return b;
}

function badge(symbol) {
  const emblems = {
    taiji: `<circle cx="60" cy="57" r="29" fill="#FFF7DE"/><path d="M60 28a29 29 0 0 1 0 58 14.5 14.5 0 0 1 0-29 14.5 14.5 0 0 0 0-29" fill="#176C5F"/><circle cx="60" cy="42.5" r="5" fill="#176C5F"/><circle cx="60" cy="71.5" r="5" fill="#FFF7DE"/><circle cx="60" cy="57" r="29" fill="none" stroke="#E8D197" stroke-width="1.5"/>`,
    pagoda: `<g fill="#FFF7DE" stroke="#E8D197" stroke-width="1.4" stroke-linejoin="round"><path d="M58 28h4v8h-4z"/><path d="M35 47q14-3 25-17 11 14 25 17l-3 5H38z"/><path d="M31 66q16-4 29-15 13 11 29 15l-4 5H35z"/><path d="M44 51h32v12H44zM41 71h38v13H41z"/></g><g stroke="#176C5F" stroke-width="4"><path d="M51 54v9m18-9v9M50 74v10m20-10v10M60 72v12"/></g><path d="M34 87h52" stroke="#FFF7DE" stroke-width="3" stroke-linecap="round"/>`,
    lotus: `<g stroke="#E8D197" stroke-width="1.5" stroke-linejoin="round"><path d="M60 75C37 58 47 38 60 29c13 9 23 29 0 46" fill="#FFF7DE"/><path d="M60 77C36 77 27 61 30 43c20 4 29 14 30 34" fill="#E6E6BE"/><path d="M60 77c24 0 33-16 30-34-20 4-29 14-30 34" fill="#E6E6BE"/><path d="M60 81c-19 6-33-4-37-18 17-2 28 3 37 18m0 0c19 6 33-4 37-18-17-2-28 3-37 18" fill="#FFF7DE"/></g><path d="M38 90h44" stroke="#E8D197" stroke-width="2" stroke-linecap="round"/>`,
    mountain: `<path d="m25 84 24-39 10 16 13-31 25 54z" fill="#F7EFCE" stroke="#E8D197" stroke-width="2" stroke-linejoin="round"/><path d="m62 55 10-25 12 26-10-6-5 8z" fill="#FFFDF0"/><path d="m39 61 10-16 8 13-8-4-4 9z" fill="#FFFDF0"/><path d="m49 57-8 27m31-31-10 31m15-14 10 14" fill="none" stroke="#679682" stroke-width="3" stroke-linecap="round"/><path d="M34 91h52" stroke="#E8D197" stroke-width="2" stroke-linecap="round"/>`,
    furnace: `<g stroke="#E8D197" stroke-width="2" stroke-linejoin="round"><path d="M39 51c-17-17-22 12-5 14m47-14c17-17 22 12 5 14" fill="none" stroke="#FFF7DE" stroke-width="5" stroke-linecap="round"/><path d="m43 76-5 13h10l4-11m16 0 4 11h10l-5-13m-21 3-1 12h10l-1-12" fill="#E8D197"/><path d="M34 48h52l-3 22c-3 16-43 16-46 0z" fill="#FFF7DE"/><path d="M35 43q9-13 25-13t25 13z" fill="#FFF7DE"/><path d="M57 31c-7-5-3-11 3-13 6 2 10 8 3 13z" fill="#E8D197"/></g><path d="M39 52h42" stroke="#176C5F" stroke-width="3"/><path d="M59 58c1 6-6 7-5 13 1 7 14 7 14-2 0-4-3-6-4-8 0 4-2 5-3 5 1-3 0-6-2-8z" fill="#176C5F"/>`,
    sword: `<g stroke="#E8D197" stroke-width="1.8" stroke-linejoin="round"><path d="M54 43h12v34l-6 15-6-15z" fill="#FFF7DE"/><path d="M54 24h12v20H54z" fill="#E8D197"/><path d="m60 18 8 7-8 5-8-5z" fill="#FFF7DE"/><path d="M37 43q8-8 16-2l7 4 7-4q8-6 16 2l-4 7-7-4-12 7-12-7-7 4z" fill="#FFF7DE"/></g><path d="M57 31h6m-6 6h6M60 55v26" stroke="#176C5F" stroke-width="2.3" stroke-linecap="round"/>`,
    water: `<path d="M30 70c-13-24 5-47 29-45 17 1 28 13 29 25-9-12-23-18-36-11-12 6-12 22-2 27-2-9 4-19 15-18 12 1 21 12 18 24-4 17-26 24-43 13 17 4 34-5 34-17 0-7-8-12-14-8 9 2 8 11 1 16-11 8-24 3-31-6z" fill="#FFF7DE" stroke="#E8D197" stroke-width="1.7" stroke-linejoin="round"/><path d="M30 73c-5-9-6-20-1-28m60 12c4 15-6 29-19 33" fill="none" stroke="#E8D197" stroke-width="3" stroke-linecap="round"/><path d="m41 32 1 6m14-11-1 7m15-3-3 6" stroke="#176C5F" stroke-width="3" stroke-linecap="round"/>`,
    compass: `<path d="m60 21 9 13 16-2-2 16 13 9-13 9 2 16-16-2-9 13-9-13-16 2 2-16-13-9 13-9-2-16 16 2z" fill="#E8D197" stroke="#FFF7DE" stroke-width="1.5" stroke-linejoin="round"/><circle cx="60" cy="57" r="25" fill="#176C5F" stroke="#FFF7DE" stroke-width="3"/><path d="m60 36 7 16 14 5-16 6-5 15-6-16-15-5 15-5z" fill="#FFF7DE"/><path d="m60 39 1 18 6-5zM61 58l-1 17-6-13z" fill="#E8D197"/><circle cx="60" cy="57" r="4" fill="#176C5F" stroke="#E8D197" stroke-width="1.5"/>`,
    peach_spirit: `<path d="M60 39c-7-9-6-17-2-20 8 2 12 8 9 17 4-12 12-13 20-12-1 12-9 18-23 16z" fill="#E8D197" stroke="#FFF7DE" stroke-width="1.5" stroke-linejoin="round"/><path d="M60 33c-6 12-20 9-27 25-8 20 5 30 27 36 23-6 35-16 27-36-6-16-20-13-27-25z" fill="#FFF7DE" stroke="#E8D197" stroke-width="2" stroke-linejoin="round"/><path d="M60 39c-7 10-2 19 4 28 6 8 2 17-4 22" fill="none" stroke="#679682" stroke-width="3" stroke-linecap="round"/><path d="M39 57q-5 9-2 17" fill="none" stroke="#E8D197" stroke-width="2.4" stroke-linecap="round"/>`,
    flame: `<path d="M62 21c8 14-9 21-2 33 7-5 8-13 10-18 13 9 6 20 11 25 5-4 7-9 6-13 15 30-4 44-25 44-22 0-35-13-33-30 1-10 8-17 14-24-1 13 3 17 7 18-7-16 14-20 12-35z" fill="#FFF7DE" stroke="#E8D197" stroke-width="1.8" stroke-linejoin="round"/><path d="M59 87c-12-3-17-14-8-24 0 8 5 11 8 10-3-7 3-13 8-18-1 10 11 14 7 24-2 5-7 8-11 8 4-5 1-9-2-10 0 6-3 6-2 10z" fill="#176C5F"/>`
  };
  return `<circle cx="60" cy="64" r="52" fill="#503C2B" opacity=".17"/><circle cx="60" cy="59" r="52" fill="url(#wood)"/><circle cx="60" cy="57" r="51" fill="url(#gold)"/><circle cx="60" cy="57" r="46" fill="url(#jade)" stroke="#82622E" stroke-width="1.5"/><circle cx="60" cy="57" r="41.5" fill="none" stroke="#E3CB8C" stroke-width="1.2"/>${emblems[symbol]}<path d="M32 20a46 46 0 0 1 56 0" fill="none" stroke="#FFF4C3" stroke-width="2" stroke-linecap="round"/>`;
}

function register(id, w, h, body, extra = {}) {
  assets.push({ id, width: w, height: h, title: id, svg: `svg/${id}.svg`, png: svgOnly ? null : `png/${id}.png`, state: 'normal', dynamic_text_baked: false, ...extra, body });
}
function slices(w, h, left, top, right, bottom) { return { left, top, right, bottom, center: { x: left, y: top, width: w - left - right, height: h - top - bottom } }; }
const specs = [
  ['primary_button', 460, 112, 82, 30, 82, 34],
  ['tab', 360, 114, 82, 30, 82, 34],
  ['list_row', 360, 96, 82, 27, 82, 31],
  ['server_card_wide', 640, 141, 82, 30, 156, 35],
  ['server_card_medium', 520, 126, 82, 30, 156, 35],
  ['search', 420, 84, 70, 26, 64, 29]
];
for (const [kind, w, h, l, t, r, b] of specs) {
  for (const state of ['normal', 'selected', 'disabled']) register(`${kind}_${state}`, w, h, surface(w, h, state, kind), {
    category: kind, state, resize_axes: 'horizontal', fixed_height: h, nine_slice: slices(w, h, l, t, r, b), minimum_size: [l + r + 40, h],
    content_insets: { left: kind === 'search' ? 70 : 76, top: 22, right: kind.startsWith('server') ? 156 : kind === 'search' ? 62 : 64, bottom: 27 },
    text_color: state === 'disabled' ? palette.disabledInk : kind === 'primary_button' || state === 'selected' ? palette.ivory : palette.ink,
    selection_marker: state === 'selected' ? 'check + left rail + bottom notch' : null,
    disabled_marker: state === 'disabled' ? 'lock; client must also supply a readable reason' : null
  });
}
register('summary_bar', 1280, 79, surface(1280, 79, 'normal', 'summary_bar'), { category: 'summary_bar', resize_axes: 'horizontal', fixed_height: 79, nine_slice: slices(1280, 79, 90, 24, 94, 28), minimum_size: [400, 79], content_insets: { left: 32, top: 17, right: 100, bottom: 22 }, text_color: palette.ink });
register('main_frame', 1440, 840, panel(1440, 840, true), { category: 'main_frame', resize_axes: 'both', nine_slice: slices(1440, 840, 148, 112, 148, 125), minimum_size: [420, 320], content_insets: { left: 56, top: 56, right: 56, bottom: 66 }, text_color: palette.ink });
register('content_panel', 1080, 620, panel(1080, 620, false), { category: 'content_panel', resize_axes: 'both', nine_slice: slices(1080, 620, 145, 108, 145, 122), minimum_size: [380, 290], content_insets: { left: 44, top: 44, right: 44, bottom: 54 }, text_color: palette.ink });
for (const icon of ['taiji', 'pagoda', 'lotus', 'mountain', 'furnace', 'sword', 'water', 'compass', 'peach_spirit', 'flame']) register(`round_badge_${icon}`, 120, 120, badge(icon), { category: 'round_badge', symbol: icon, nine_slice: null });
for (const [state, fill, glyph] of [['green', '#308B68', '<path d="m10 16 4 4 8-9"/>'], ['orange', '#BD741E', '<path d="M16 9v8m0 5v.1"/>'], ['gray', '#6F7A6A', '<path d="M10 16h12"/>']]) register(`status_dot_${state}`, 32, 32, `<circle cx="16" cy="18" r="13.5" fill="#594530" opacity=".15"/><circle cx="16" cy="16" r="13" fill="url(#gold)"/><circle cx="16" cy="16" r="10" fill="${fill}"/><g fill="none" stroke="#FFFBE7" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">${glyph}</g>`, { category: 'status_dot', state, nine_slice: null, meaning: { green: 'available', orange: 'busy', gray: 'unavailable' }[state], semantics: 'Design semantics only; bind to real server states in the client.' });
register('recommend_badge', 96, 40, `<path d="M5 6h86v24H53l-5 6-5-6H5z" fill="url(#gold)" stroke="#8C6933" stroke-width="1.5"/><path d="M9 10h78v16H9z" fill="#FFF7DE" opacity=".55"/><path d="m18 13 1.7 3.6 4 .6-2.8 2.7.7 4-3.6-1.9-3.6 1.9.7-4-2.8-2.7 4-.6z" fill="#795638"/>`, { category: 'recommend_badge', nine_slice: null, content_insets: { left: 29, top: 8, right: 12, bottom: 12 }, text_color: '#674B2F' });
register('check', 48, 48, check(0, 0, 48), { category: 'check', nine_slice: null });
register('lock', 48, 48, lock(0, 0, 48), { category: 'lock', nine_slice: null });
register('gold_flower', 120, 120, `<g fill="url(#gold)" stroke="#9D733B" stroke-width="1.4">${Array.from({ length: 8 }, (_, i) => `<path d="M60 55C43 42 48 21 60 12c12 9 17 30 0 43Z" transform="rotate(${i * 45} 60 60)"/>`).join('')}</g><circle cx="60" cy="60" r="19" fill="url(#jade)" stroke="#E3CA83" stroke-width="3"/><circle cx="60" cy="60" r="10" fill="url(#gold)"/><circle cx="57" cy="57" r="3" fill="#FFF5CC"/>`, { category: 'gold_flower', nine_slice: null });
register('cloud_corner', 160, 160, `<g fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M12 142V54Q12 14 53 14h94" stroke="#795638" stroke-width="8" opacity=".2"/><path d="M12 136V48Q12 10 51 10h91" stroke="url(#gold)" stroke-width="6"/><path d="M23 133V51q0-29 29-29h81" stroke="#D5B36C" stroke-width="2"/><path d="M30 88h38c19 0 22-27 2-27-13 0-16 18-3 18h35c21 0 24-32 3-32-12 0-17 10-12 19" stroke="#C59645" stroke-width="4"/><path d="M42 105h55c25 0 28-27 49-27" stroke="#C59645" stroke-width="3"/><path d="M34 120h41" stroke="#C59645" stroke-width="2"/></g>`, { category: 'cloud_corner', nine_slice: null });

// v7 artwork: newly generated built-in image_gen inputs, prepared at fixed dimensions.
const aiRoot = path.resolve(root, '../../qdao_gpt_image2_refresh_v7/ui');
const aiSourceMap = JSON.parse(await fs.readFile(path.join(aiRoot, 'source-map.json'), 'utf8'));
for (const a of assets) {
  const painted = await fs.readFile(path.join(aiRoot, 'derived/components', `${a.id}.png`));
  a.body = `<image x="0" y="0" width="${a.width}" height="${a.height}" href="data:image/png;base64,${painted.toString('base64')}"/>`;
  a.authoring = 'New built-in image_gen artwork; deterministic alpha cleanup, nine-slice layout and status placement; portable embedded PNG in SVG.';
  a.v7_sources = aiSourceMap.derivatives[a.id];
  const source = svg(a.width, a.height, a.body, `五行奇谈 ${a.id}`);
  await fs.writeFile(path.join(root, a.svg), source, 'utf8');
  if (sharp) await fs.writeFile(path.join(root, a.png), await sharp(Buffer.from(source)).png({ compressionLevel: 9 }).toBuffer());
}

// An annotated review board. Labels are separate from the actual export assets.
const boardW = 1800;
let board = `<rect width="1800" height="2360" fill="#F3EFE0"/><path d="M0 0h1800v205H0z" fill="#164D43"/><text x="65" y="83" font-family="Microsoft YaHei,Noto Sans CJK SC,sans-serif" font-size="40" font-weight="700" fill="#FFF7DE">五行奇谈 · 通用界面控件</text><text x="65" y="135" font-family="Microsoft YaHei,Noto Sans CJK SC,sans-serif" font-size="23" fill="#DDD1AB">玉绿 · 米白 · 暖金 · 桃木 / ${assets.length} 个无动态文字资产</text>`;
const text = (x, y, t, size = 22, fill = '#344D43') => `<text x="${x}" y="${y}" font-family="Microsoft YaHei,Noto Sans CJK SC,sans-serif" font-size="${size}" fill="${fill}">${escape(t)}</text>`;
const place = (a, x, y, w, h) => `<svg x="${x}" y="${y}" width="${w}" height="${h}" viewBox="0 0 ${a.width} ${a.height}">${defs}${a.body}</svg>`;
board += text(70, 252, '控件 / 原始尺寸', 19) + text(575, 252, '普通', 21) + text(1090, 252, '已选：勾记 + 边缘标识', 21) + text(1498, 252, '不可用：锁形', 21);
const reviewLabels = { primary_button: '进入游戏', tab: '全部区服', list_row: '最近登录', server_card_wide: '服务器名称', server_card_medium: '服务器名称', search: '搜索服务器' };
for (const [i, [kind, w, h]] of specs.entries()) {
  const y = 288 + i * 145;
  board += text(70, y + 38, kind, 19) + text(70, y + 69, `${w} × ${h}`, 18, '#756B53');
  for (const [j, state] of ['normal', 'selected', 'disabled'].entries()) {
    const a = assets.find(a => a.id === `${kind}_${state}`);
    const scale = Math.min(1, 420 / w, 105 / h);
    const ww = w * scale, hh = h * scale, x = 365 + j * 470;
    board += place(a, x, y, ww, hh);
    // Board-only native text proves the usable label area; labels never enter the asset.
    const tx = x + (kind === 'search' ? 80 : 92) * scale;
    const ty = y + h * scale / 2 + 4;
    board += text(tx, ty, state === 'disabled' ? '暂不可用' : reviewLabels[kind], Math.max(18, 25 * scale), a.text_color);
  }
}
board += text(70, 1210, '面板、框架与摘要栏', 26);
board += place(assets.find(a => a.id === 'main_frame'), 60, 1250, 620, 360);
board += place(assets.find(a => a.id === 'content_panel'), 725, 1270, 485, 278);
board += text(107, 1320, '主框架', 25) + text(770, 1340, '内容面板', 25);
board += text(107, 1360, '1440 × 840 · 四角固定', 19) + text(770, 1380, '1080 × 620 · 九宫格', 19);
board += place(assets.find(a => a.id === 'summary_bar'), 70, 1650, 1280, 79);
board += text(105, 1697, '当前选择：服务器名称', 24);
board += text(1270, 1300, '灰阶与形状仍可辨认', 22) + text(1270, 1340, '文字由客户端绘制', 20) + text(1270, 1378, '圆徽标与状态点独立叠放', 20) + text(1270, 1416, '边距与九宫格见 manifest.json', 19);
board += text(70, 1820, '徽标、状态与装饰', 26);
const icons = assets.filter(a => ['round_badge', 'status_dot', 'recommend_badge', 'check', 'lock', 'gold_flower', 'cloud_corner'].includes(a.category));
for (const [i, a] of icons.entries()) {
  const col = i % 7, row = Math.floor(i / 7), cx = 100 + col * 235, cy = 1810 + row * 165;
  const scale = Math.min(1, 90 / a.width, 90 / a.height);
  board += place(a, cx + (90 - a.width * scale) / 2, cy, a.width * scale, a.height * scale);
  board += text(cx - 15, cy + 116, a.id, 14) + text(cx + 15, cy + 142, `${a.width} × ${a.height}`, 14, '#756B53');
}
const overview = svg(boardW, 2360, board, '五行奇谈 通用 UI 控件总览');
await fs.writeFile(path.join(root, 'overview.svg'), overview, 'utf8');
if (sharp) await fs.writeFile(path.join(root, 'overview.png'), await sharp(Buffer.from(overview)).png({ compressionLevel: 9 }).toBuffer());
// All ten symbols at delivery size and two small sizes; labels stay on the review sheet.
const badgeNames = { taiji: '太极', pagoda: '楼阁', lotus: '莲花', mountain: '山', furnace: '炼丹炉', sword: '剑', water: '水纹', compass: '罗盘', peach_spirit: '桃灵', flame: '火焰' };
const badgeLegacyNames = { taiji: 'icon_yin_yang.png', pagoda: 'icon_pagoda.png', lotus: 'icon_lotus.png', mountain: 'icon_mountain.png', furnace: 'icon_cauldron.png', sword: 'icon_sword.png', water: 'icon_water.png', compass: 'icon_compass.png', peach_spirit: 'icon_peach_spirit.png', flame: 'icon_fire.png' };
const badges = assets.filter(a => a.category === 'round_badge');
let badgeBoard = `<rect width="1200" height="880" fill="#F3EFE0"/><path d="M0 0h1200v145H0z" fill="#164D43"/>${text(46, 62, '五行奇谈 · 十枚圆徽标', 34, '#FFF7DE')}${text(46, 105, '120 × 120 透明资产 · 同一玉绿金框 · 等比缩放', 22, '#DDD1AB')}`;
badgeBoard += text(46, 181, '原始尺寸 / 120 px', 21);
for (const [i, a] of badges.entries()) {
  const x = 46 + (i % 5) * 232, y = 203 + Math.floor(i / 5) * 195;
  badgeBoard += place(a, x + 26, y, 120, 120) + text(x + 86, y + 147, badgeNames[a.symbol], 20).replace('<text ', '<text text-anchor="middle" ');
  badgeBoard += text(x + 86, y + 172, a.symbol, 15, '#756B53').replace('<text ', '<text text-anchor="middle" ');
}
for (const [size, top, fill] of [[48, 604, '#E5E8D9'], [32, 750, '#DBE2D5']]) {
  badgeBoard += `<rect x="26" y="${top}" width="1148" height="112" rx="12" fill="${fill}"/>` + text(46, top + 26, `${size} px / 小尺寸辨识`, 18);
  for (const [i, a] of badges.entries()) {
    const cx = 70 + i * 115;
    badgeBoard += place(a, cx - size / 2, top + 36, size, size);
    badgeBoard += text(cx, top + 102, badgeNames[a.symbol], 15).replace('<text ', '<text text-anchor="middle" ');
  }
}
const badgeOverview = svg(1200, 880, badgeBoard, '五行奇谈 十枚圆徽标 120 / 48 / 32 px 辨识预览');
await fs.writeFile(path.join(root, 'badges_overview.svg'), badgeOverview, 'utf8');
if (sharp) await fs.writeFile(path.join(root, 'badges_overview.png'), await sharp(Buffer.from(badgeOverview)).png({ compressionLevel: 9 }).toBuffer());
const html = `<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>五行奇谈 · 通用 UI 控件</title><style>body{margin:0;background:#e6e5d9;color:#344d43;font:16px/1.6 "Microsoft YaHei",sans-serif}header{padding:24px 5vw;background:#164d43;color:#fff7de;display:flex;gap:24px;align-items:center;flex-wrap:wrap}h1{font-size:24px;margin:0}a{color:#f0d492}main{max-width:1800px;margin:auto}img{display:block;width:100%;height:auto}p{margin:0}</style><header><h1>五行奇谈 · ${assets.length} 个通用 UI 控件</h1><p>总览文字仅用于检查，SVG / PNG 控件未烘焙动态文字。</p><a href="manifest.json">尺寸与九宫格</a><a href="README.md">接入说明</a><a href="badges_overview.svg">十枚徽标与小尺寸检查</a></header><main><img src="overview.svg" alt="普通、选中、不可用控件及面板、徽标、状态图标总览"></main></html>`;
await fs.writeFile(path.join(root, 'overview.html'), html, 'utf8');

const manifest = {
  product: '五行奇谈', version: '7.0', created: '2026-09-07', asset_count: assets.length, badge_count: badges.length,
  authoring: 'New built-in image_gen artwork, fixed-contract derivatives embedded portably in SVG. Dynamic text remains separate.',
  ai_provenance: { source_map: '../../qdao_gpt_image2_refresh_v7/ui/source-map.json', prepare: '../../qdao_gpt_image2_refresh_v7/ui/prepare_assets.py', native_sources: aiSourceMap.native_sources, model_parameter_exposed: false, quality_parameter_exposed: false },
  badge_replacements: { legacy_directory: '../../q_daoist_login_ui_10240_redraw_clear_final_layers/q_daoist_login_buttons_redrawn_atomic', symbols: badges.map(a => ({ legacy_file: badgeLegacyNames[a.symbol], replacement_id: a.id, meaning: badgeNames[a.symbol], svg: a.svg, png: a.png })) },
  palette, renderer: sharp ? { sharp: sharp.versions.sharp, vips: sharp.versions.vips } : null,
  states: { normal: '可用普通态', selected: '勾记、边缘标识和金色三角共同表达；不等于推荐或键盘焦点', disabled: '锁形和降低强调表达不可用；文字保持可辨，点击规则由客户端实施' },
  png_alpha: 'RGBA; transparent outside the control; no opaque rectangular canvas.',
  nine_slice_convention: 'left/top/right/bottom are fixed source pixel borders, including transparent shadow margins; center is the stretch rectangle. Respect resize_axes: marked controls keep their source height; only the two large panels support both axes. Never stretch round icons or text.',
  interaction_note: 'This kit supplies visuals only. Client owns text, input, pointer/keyboard focus, hit testing, state transitions, and accessibility labels. Exported shadows do not enlarge hit targets.',
  text_note: 'Use a readable CJK font. Suggested labels: 28–32 px for buttons/tabs; 24–28 px for rows/cards/search at original size. Do not shrink interactive text to the overview board size.',
  artifacts: { overview: 'overview.html', overview_svg: 'overview.svg', overview_png: sharp ? 'overview.png' : null, source_builder: 'build.mjs', readme: 'README.md', badges_overview_svg: 'badges_overview.svg', badges_overview_png: sharp ? 'badges_overview.png' : null, badge_design_brief: 'badge_design_brief.md' },
  assets: assets.map(({ body, ...a }) => a)
};
await fs.writeFile(path.join(root, 'manifest.json'), JSON.stringify(manifest, null, 2) + '\n', 'utf8');
if (sharp) {
  const checks = [];
  for (const a of assets) {
    const image = sharp(path.join(root, a.png));
    const meta = await image.metadata();
    const stats = await image.stats();
    const alpha = stats.channels[3];
    const valid = meta.width === a.width && meta.height === a.height && meta.hasAlpha && alpha?.min === 0 && alpha?.max === 255;
    if (!valid) throw new Error(`PNG validation failed: ${a.id}`);
    checks.push({ id: a.id, dimensions_match: true, rgba: true, alpha_range: [alpha.min, alpha.max] });
  }
  await fs.writeFile(path.join(root, 'validation.json'), JSON.stringify({ passed: true, count: checks.length, scope: 'Exact PNG dimensions and alpha range. See README for additional XML and visual review.', checks }, null, 2) + '\n', 'utf8');
} else {
  await fs.writeFile(path.join(root, 'validation.json'), JSON.stringify({ passed: true, count: assets.length, svg_generated: true, png_checked_this_run: false, scope: 'SVG-only build; existing PNG outputs were not refreshed or checked.' }, null, 2) + '\n', 'utf8');
}
console.log(JSON.stringify({ assets: assets.length, svg: assets.length, png: sharp ? assets.length : 0, overview: sharp ? 'overview.html + SVG + PNG' : 'overview.html + SVG', renderer: sharp?.versions.sharp ?? 'SVG only' }));
