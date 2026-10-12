// Execute the actual preview player with a minimal DOM; checks timing, not appearance.
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const crypto = require('crypto');
const root = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'review/index.html'), 'utf8');
const data = JSON.parse(html.match(/<script id="data" type="application\/json">([\s\S]*?)<\/script>/)[1]);
const script = html.match(/<script>\s*([\s\S]*?)<\/script>/)[1];
const nodes = new Map();
function element() {
  return {value: '', textContent: '', checked: false, children: [], style: {setProperty() {}}, classList: {toggle() {}},
    append(child) { this.children.push(child); if (!this.value && child.value) this.value = child.value; },
    replaceChildren() { this.children = []; this.value = ''; }, removeAttribute() {}};
}
function node(id) { if (!nodes.has(id)) nodes.set(id, element()); return nodes.get(id); }
node('data').textContent = JSON.stringify(data);
node('action').value = 'run'; node('direction').value = 'N'; node('loop').checked = true;
const context = { document: {getElementById: node, createElement: element, querySelectorAll: () => [], addEventListener() {}},
  performance: {now: () => 0}, requestAnimationFrame() {}};
vm.createContext(context);
vm.runInContext(script, context);
const run = code => vm.runInContext(code, context);
const assert = (condition, message) => { if (!condition) throw Error(message); };
let assertions = 0;
const sequences = [];
for (const [action, spec] of Object.entries(data.specs)) {
  for (const direction of spec.directions) {
    node('action').value = action; node('direction').value = direction;
    run('sequenceChanged()');
    const rows = data.frames.filter(f => f.action === action && f.direction === direction);
    const ms = action === 'run' ? 60 : {hit: 40, attack: 30, cast: 45}[action];
    assert(rows.length === spec.count && rows.every(f => f.frame_duration_ms === ms), `${action}/${direction}: frame contract`);
    assert(spec.duration_ms === rows.length * ms, `${action}/${direction}: total`);
    for (const speed of [1, 0.25]) {
      node('loop').checked = false;
      // Single-play must restart and show every slot even when previously paused mid-cycle.
      run(`index=7;play(${speed})`);
      assert(run('index') === 0, 'single-play start');
      for (let count = 1; count <= rows.length; count++) {
        context.now = (count * ms - 0.01) / speed; run('tick(now)');
        assert(run('index') === count - 1 && run('playing'), 'full dwell before boundary'); assertions++;
        context.now = count * ms / speed; run('tick(now)');
        assert(run('index') === (count < rows.length ? count : rows.length - 1), 'exact boundary index');
        assert(run('playing') === (count < rows.length), 'single-play stop at total'); assertions += 2;
      }
      node('loop').checked = true;
      run(`sequenceChanged();play(${speed})`);
      for (let count = 1; count <= rows.length * 2; count++) {
        context.now = count * ms / speed; run('tick(now)');
        assert(run('index') === count % rows.length && run('playing'), 'loop continuous boundary'); assertions++;
      }
      assert(Math.abs(run('elapsed')) < 0.001, 'no extra first/last hold');
      run('stop()'); const paused = run('index'); context.now += 1000; run('tick(now)');
      assert(run('index') === paused, 'pause'); assertions++;
    }
    sequences.push({action, direction, frames: rows.length, frameMs: ms, cycleMs: rows.length * ms, passed: true});
  }
}
const result = {passed: true, htmlSha256: crypto.createHash('sha256').update(html).digest('hex'), sequences, assertions, speeds: [1, 0.25],
  method: 'Actual generated player executed in Node VM: all frame boundaries, complete single-play, two full loops and pause. Not browser visual playback.',
  dynamicVisualPlaybackVerified: false};
fs.writeFileSync(path.join(root, 'review/player-validation.json'), JSON.stringify(result, null, 2) + '\n');
console.log(JSON.stringify({passed: true, sequences: sequences.length, assertions}));
