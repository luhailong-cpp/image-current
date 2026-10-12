'use strict';

// Executes the actual inline player in a local VM with deterministic DOM/RAF.
// Writes audit reports only; never modifies product HTML, frame records or images.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');

const root = path.resolve(__dirname, '..');
assert.equal(path.basename(root), '04_mountain_guardian_boy');
const htmlPath = path.join(root, 'preview', 'index.html');
const html = fs.readFileSync(htmlPath, 'utf8');
const digest = value => crypto.createHash('sha256').update(value).digest('hex');
const htmlSha = digest(html);
const scripts = [...html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script\s*>/gi)];
const dataScripts = scripts.filter(s => /\bid\s*=\s*["']manifest-data["']/i.test(s[1]));
const playerScripts = scripts.filter(s => !/\btype\s*=\s*["']application\/json["']/i.test(s[1]));
assert.equal(dataScripts.length, 1, 'Expected one embedded manifest');
assert.equal(playerScripts.length, 1, 'Expected one inline player');
assert.ok(!/\bsrc\s*=/i.test(playerScripts[0][1]), 'External player is outside this harness');
const manifestText = dataScripts[0][2];
const manifest = JSON.parse(manifestText);
const player = playerScripts[0][2];
const markup = html.slice(0, scripts[0].index);

class Element {
  constructor(tagName) {
    this.tagName = tagName.toUpperCase();
    this.children = [];
    this.dataset = {};
    this.style = {};
    this.classList = {toggle() {}};
    this.listeners = new Map();
    this._value = '';
    this.textContent = '';
    this.hidden = false;
    this.checked = false;
  }
  get value() { return this._value; }
  set value(value) { this._value = String(value); }
  get options() { return this.children.filter(x => x.tagName === 'OPTION'); }
  append(child) {
    this.children.push(child);
    if (this.tagName === 'SELECT' && this.options.length === 1) this.value = child.value;
  }
  replaceChildren(...children) {
    this.children = [];
    this.value = '';
    for (const child of children) this.append(child);
  }
  addEventListener(type, callback) {
    if (!this.listeners.has(type)) this.listeners.set(type, []);
    this.listeners.get(type).push(callback);
  }
  dispatch(type, event = {}) {
    for (const callback of this.listeners.get(type) || []) callback(event);
    if (typeof this['on' + type] === 'function') this['on' + type](event);
  }
  removeAttribute(name) { delete this[name]; }
}

function harness() {
  const elements = new Map();
  for (const match of markup.matchAll(/<([a-z][\w-]*)\b([^>]*)>/gi)) {
    const id = /\bid\s*=\s*["']([^"']+)["']/i.exec(match[2]);
    if (!id) continue;
    const element = new Element(match[1]);
    const value = /\bvalue\s*=\s*["']([^"']*)["']/i.exec(match[2]);
    if (value) element.value = value[1];
    element.hidden = /\bhidden\b/i.test(match[2]);
    element.checked = /\bchecked\b/i.test(match[2]);
    elements.set(id[1], element);
  }
  for (const select of markup.matchAll(/<select\b([^>]*)>([\s\S]*?)<\/select>/gi)) {
    const id = /\bid\s*=\s*["']([^"']+)["']/i.exec(select[1]);
    if (!id) continue;
    for (const option of select[2].matchAll(/<option\b([^>]*)>([\s\S]*?)<\/option>/gi)) {
      const element = new Element('option');
      const value = /\bvalue\s*=\s*["']([^"']*)["']/i.exec(option[1]);
      element.value = value ? value[1] : option[2];
      element.textContent = option[2];
      elements.get(id[1]).append(element);
      if (/\bselected\b/i.test(option[1])) elements.get(id[1]).value = element.value;
    }
  }
  const dataElement = new Element('script');
  dataElement.textContent = manifestText;
  elements.set('manifest-data', dataElement);
  const document = new Element('document');
  document.getElementById = id => {
    assert.ok(elements.has(id), `Actual script requested unmodelled element ${id}`);
    return elements.get(id);
  };
  document.createElement = tag => new Element(tag);
  document.activeElement = new Element('body');
  let callbacks = [];
  let lastTime = -Infinity;
  class LoadedImage {
    constructor() { this.complete = false; this.naturalWidth = 0; }
    set src(value) {
      this._src = value;
      this.complete = true;
      this.naturalWidth = 1024;
      if (this.onload) this.onload();
    }
    get src() { return this._src; }
  }
  const context = vm.createContext({document, Image: LoadedImage,
    requestAnimationFrame(callback) { callbacks.push(callback); return callbacks.length; }});
  new vm.Script(player, {filename: htmlPath + '#actual-inline-player'}).runInContext(context);
  const element = id => elements.get(id);
  return {
    element,
    choose(action, direction, speed = 1) {
      element('action').value = action;
      element('action').dispatch('change');
      assert.ok(element('direction').options.some(x => x.value === direction));
      element('direction').value = direction;
      element('direction').dispatch('change');
      element('speed').value = speed;
      element('speed').dispatch('change');
    },
    click(id) { element(id).dispatch('click'); },
    frame() { return Number(element('scrub').value); },
    advance(timestamp) {
      assert.ok(timestamp >= lastTime, 'Clock must be monotonic');
      lastTime = timestamp;
      const batch = callbacks;
      callbacks = [];
      assert.equal(batch.length, 1, 'Exactly one RAF loop should be scheduled');
      for (const callback of batch) callback(timestamp);
    },
  };
}

const results = [];
function test(name, run) {
  try { results.push({name, status: 'passed', ...run()}); }
  catch (error) { results.push({name, status: 'failed', error: error.stack}); }
}

function cycleTest(action, direction, count, baseFrameMs, speed) {
  const h = harness();
  h.choose(action, direction, speed);
  const sequence = manifest.sequences.find(s => s.action === action && s.direction === direction);
  assert.equal(sequence.target_count, count);
  assert.equal(sequence.frames.length, count);
  assert.ok(sequence.frames.every(f => f.exists), 'Player must use all real frame slots');
  assert.equal(sequence.frame_ms, baseFrameMs);
  assert.equal(sequence.duration_ms, count * baseFrameMs);
  h.click('play');
  h.advance(0);
  const stepMs = baseFrameMs / speed;
  const cycleMs = count * stepMs;
  const boundaries = [{timeMs: 0, observedFrame: h.frame()}];
  const beforeBoundaries = [];
  assert.equal(h.frame(), 0);
  for (let index = 1; index <= count; index++) {
    const before = index * stepMs - 1;
    h.advance(before);
    assert.equal(h.frame(), index - 1, `Frame before boundary ${index}`);
    beforeBoundaries.push({timeMs: before, observedFrame: h.frame()});
    h.advance(index * stepMs);
    assert.equal(h.frame(), index % count, `Frame at boundary ${index}`);
    boundaries.push({timeMs: index * stepMs, observedFrame: h.frame()});
  }
  // A second cycle checks repeated wrapping and the catch-up loop.
  h.advance(cycleMs * 2 - 1);
  assert.equal(h.frame(), count - 1);
  h.advance(cycleMs * 2);
  assert.equal(h.frame(), 0);
  assert.ok(h.element('status').textContent.includes(`${stepMs}ms / 帧`));
  assert.ok(h.element('status').textContent.includes(`${cycleMs}ms / 段`));
  return {action, direction, speed, frameMs: stepMs, cycleMs, boundaries, beforeBoundaries,
    finalFrameAtCycleMinusOne: beforeBoundaries.at(-1).observedFrame,
    firstFrameAtCycle: boundaries.at(-1).observedFrame,
    extraFirstOrLastFrameWait: false, secondCycleWrapped: true};
}

const directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
test('实际页面无旧run-cycle选择器，速度选项仅1/0.5/0.25', () => {
  const h = harness();
  assert.ok(!/\brun-cycle\b/i.test(markup));
  assert.ok(!/\brun-cycle\b/i.test(player));
  assert.deepEqual(h.element('speed').options.map(x => x.value), ['1', '0.5', '0.25']);
  assert.equal(h.element('speed').value, '1');
  assert.deepEqual(manifest.sequences.filter(s => s.action === 'run').map(s => s.direction), directions);
  return {oldRunCycleSelectorPresent: false, speeds: ['1', '0.5', '0.25'], defaultSpeed: 1};
});
for (const direction of directions) {
  for (const speed of [1, 0.5, 0.25]) {
    test(`run/${direction}/${speed}x完整循环`, () => cycleTest('run', direction, 16, 75, speed));
  }
  test(`run/${direction}/暂停与恢复`, () => {
    const h = harness();
    h.choose('run', direction);
    h.click('play'); h.advance(0); h.advance(150);
    assert.equal(h.frame(), 2);
    h.click('play');
    assert.equal(h.element('play').textContent, '播放');
    h.advance(10000);
    assert.equal(h.frame(), 2);
    h.click('play'); h.advance(10100); h.advance(10174);
    assert.equal(h.frame(), 2);
    h.advance(10175);
    assert.equal(h.frame(), 3);
    return {pausedFrame: 2, stayedPausedThroughMs: 10000,
      resumeClockOriginMs: 10100, resumedFrameAfter75Ms: 3, backlogCatchup: false};
  });
  test(`run/${direction}/逐帧双向循环并暂停播放`, () => {
    const h = harness();
    h.choose('run', direction);
    h.click('previous'); assert.equal(h.frame(), 15);
    h.click('next'); assert.equal(h.frame(), 0);
    const steps = [0];
    for (let n = 1; n <= 16; n++) {
      h.click('next'); assert.equal(h.frame(), n % 16); steps.push(h.frame());
    }
    h.click('play'); h.advance(0); h.click('next');
    assert.equal(h.frame(), 1);
    assert.equal(h.element('play').textContent, '播放');
    h.advance(10000); assert.equal(h.frame(), 1);
    h.element('scrub').value = 15; h.element('scrub').dispatch('input');
    h.click('next'); assert.equal(h.frame(), 0);
    return {previousFromZero: 15, nextFromFifteen: 0, steps, stepPausesPlayback: true,
      scrubThenNextWraps: true};
  });
}
for (const [action, count, ms] of [['hit', 6, 40], ['attack', 12, 30], ['cast', 16, 45]]) {
  for (const direction of ['E', 'W']) {
    test(`${action}/${direction}/原时长保持`, () => cycleTest(action, direction, count, ms, 1));
  }
}
test('读取到报告写入前HTML未变化', () => {
  assert.equal(digest(fs.readFileSync(htmlPath)), htmlSha);
  return {sha256: htmlSha};
});

const failed = results.filter(x => x.status !== 'passed');
const report = {
  schema: 'qdao-player-timing-validation-v1', character: path.basename(root),
  validatedAtUtc: new Date().toISOString(), status: failed.length ? 'failed' : 'passed',
  engine: {name: 'Node.js vm', nodeVersion: process.version, executable: process.execPath,
    source: 'Bundled runtime; no dependencies downloaded'},
  sources: {html: {file: 'preview/index.html', sha256: htmlSha},
    inlinePlayerSha256: digest(player), embeddedManifestSha256: digest(manifestText),
    test: {file: 'tools/' + path.basename(__filename), sha256: digest(fs.readFileSync(__filename))}},
  method: 'Execute actual unmodified inline player using local VM, minimal DOM, immediate image-load stub and deterministic RAF timestamps; assert observable scrub/status/button values.',
  productFilesModified: false, browserEvaluationInjectionUsed: false,
  expected: {run: {directions, frames: 16, frameMs: 75, normalCycleMs: 1200,
      halfSpeedCycleMs: 2400, quarterSpeedCycleMs: 4800},
    combatCycleMs: {hit: 240, attack: 360, cast: 720}},
  summary: {tests: results.length, passed: results.length - failed.length, failed: failed.length},
  limits: ['测试从播放后的首个RAF时间戳t=0开始计时；真实点击至首个RAF有显示调度延迟。',
    'Node VM不渲染像素，也不测浏览器实际刷新率、图像解码或掉帧。',
    '本轮只验证播放器逻辑和嵌入时长；不构成美术、脚底接地或客户端位移验收。'],
  results,
};
const audit = path.join(root, 'provenance', 'audit');
fs.mkdirSync(audit, {recursive: true});
const reportName = 'timing_1200_player_validation';
fs.writeFileSync(path.join(audit, reportName + '.json'), JSON.stringify(report, null, 2) + '\n');
const markdown = [
  '# 04 山岳守卫：1200ms 播放器验证', '',
  `结果：**${failed.length ? '未全部通过' : '全部通过'}**，${report.summary.passed}/${results.length} 项。`, '',
  '使用本机 bundled Node.js VM 执行当前 `preview/index.html` 实际内嵌播放器，模拟 DOM 和 requestAnimationFrame；没有修改产品页面、元数据或图片，没有向浏览器注入测试。', '',
  '| 检查 | 执行证据 |', '|---|---|',
  '| 八向正常播放 | 各自走完 0→1→…→15→0；每帧75ms，t=1199仍为15，t=1200回到0；第二圈也正确回接，无额外首尾等待。 |',
  '| 八向0.5× / 0.25× | 分别每帧150ms / 300ms，一圈2400ms / 4800ms；逐边界和回接检查。 |',
  '| 八向暂停 / 恢复 | 暂停保留当前帧；恢复从新的RAF时间基准计时，不补播暂停期间帧。 |',
  '| 八向逐帧 | 上一帧0→15、下一帧15→0；完整16次步进循环；步进自动暂停，滑块之后仍能循环。 |',
  '| 战斗动作 | E/W受击6×40=240ms、普攻12×30=360ms、施法16×45=720ms，逐边界与循环检查。 |',
  '| 控件 | 旧run-cycle选择器及脚本引用消失；速度仅正常1×、慢速0.5×、慢速0.25×，默认1×。 |', '',
  `当前页面 SHA256：\`${htmlSha}\`。逐项观测时间、帧序列、脚本与测试工具 SHA 见同名 JSON。`, '',
  '测试从播放后的首个RAF时间戳 t=0 开始。真实浏览器调度、图像解码、掉帧和像素显示未在VM中测试；该证据不代替美术、接地或客户端移动验收。', '',
];
if (failed.length) {
  markdown.push('执行失败项（以上表格是目标检查项，具体以失败记录为准）：', '');
  for (const row of failed) markdown.push(`- ${row.name}: ${row.error}`, '');
}
fs.writeFileSync(path.join(audit, reportName + '.md'), markdown.join('\n') + '\n');
console.log(JSON.stringify({status: report.status, ...report.summary, htmlSha256: htmlSha,
  reports: [reportName + '.json', reportName + '.md']}, null, 2));
process.exitCode = failed.length ? 1 : 0;
