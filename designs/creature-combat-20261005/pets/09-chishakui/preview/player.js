/* Local preview only. Rendering/playback visual acceptance is recorded separately. */
(() => {
  'use strict';
  const manifest = JSON.parse(document.getElementById('manifest').textContent);
  const states = [];
  let allPaused = false;
  let hidden = document.hidden;
  let lastTime = performance.now();
  const cards = document.getElementById('cards');
  const toggle = document.getElementById('toggle');
  const status = document.getElementById('status');

  function tick(now) {
    const delta = Math.max(0, now - lastTime);
    lastTime = now;
    for (const s of states) s.timeline.advance(delta, allPaused || hidden || !s.ready);
  }
  function render() {
    for (const s of states) {
      const frames = s.timeline.frames;
      s.canvases.forEach((canvas, i) => {
        const ctx = canvas.getContext('2d');
        const im = s.images[frames[i]];
        ctx.clearRect(0, 0, 1024, 1024);
        if (s.ready && im.complete && im.naturalWidth) ctx.drawImage(im, 0, 0);
        s.readouts[i].textContent = s.error ? '图片加载失败，请检查文件路径' : !s.ready ? '正在加载本组图片…' :
          `${i ? '0.25×' : '1×'} · ${String(frames[i] + 1).padStart(2, '0')} / ${s.g.count}`;
      });
      s.slider.value = frames[0];
      s.pause.textContent = s.timeline.paused ? '播放本组' : '暂停本组';
    }
    toggle.textContent = allPaused ? '全部播放' : '全部暂停';
    const failed = states.filter(s => s.error).length;
    const ready = states.filter(s => s.ready).length;
    status.textContent = `${manifest.actualFrames} / 68 帧 · ${ready}/6 组已加载 · 1024×1024 RGBA · pivot (0.5, 0.08)` +
      (failed ? ` · ${failed}组加载失败` : '') + (allPaused ? ' · 全局暂停' : '');
  }
  function act(fn) {
    tick(performance.now());
    fn();
    render();
  }
  for (const g of manifest.groups) {
    const el = document.createElement('section');
    el.className = 'card';
    el.id = `${g.action}-${g.direction}`;
    el.tabIndex = 0;
    el.innerHTML = `<h2>${g.action} · ${g.direction}<small>${g.count} 帧 × ${g.durationMs} ms = ${g.totalMs} ms</small></h2><div class="pair"><div class="view"><canvas width="1024" height="1024"></canvas><small class="readout normal"></small></div><div class="view"><canvas width="1024" height="1024"></canvas><small class="readout slow"></small></div></div><button class="pause">暂停本组</button> <button class="prev">上一帧</button> <button class="next">下一帧</button><input aria-label="逐帧 ${g.action} ${g.direction}" type="range" min="0" max="${g.count - 1}" value="0">`;
    cards.append(el);
    const s = {g, el, timeline: new CombatTimeline(g.count, g.durationMs), images: [], ready: false, error: false,
      canvases: [...el.querySelectorAll('canvas')], readouts: [...el.querySelectorAll('.readout')],
      pause: el.querySelector('.pause'), slider: el.querySelector('input')};
    states.push(s);
    const seek = frame => act(() => s.timeline.seek(frame));
    s.pause.onclick = () => act(() => { s.timeline.paused = !s.timeline.paused; });
    el.querySelector('.prev').onclick = () => act(() => s.timeline.step(-1));
    el.querySelector('.next').onclick = () => act(() => s.timeline.step(1));
    s.slider.oninput = event => seek(Number(event.target.value));
    el.onkeydown = event => {
      if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
        event.preventDefault();
        act(() => s.timeline.step(event.key === 'ArrowLeft' ? -1 : 1));
      }
    };
    Promise.all(g.files.map(file => new Promise((resolve, reject) => {
      const im = new Image();
      s.images.push(im);
      im.onload = resolve;
      im.onerror = () => reject(new Error(file));
      im.src = '../' + file;
    }))).then(() => act(() => { s.ready = true; })).catch(() => act(() => { s.error = true; }));
  }
  toggle.onclick = () => act(() => { allPaused = !allPaused; });
  document.getElementById('reset').onclick = () => act(() => {
    allPaused = false;
    for (const s of states) s.timeline.reset();
  });
  document.getElementById('bg').onchange = event => document.querySelectorAll('canvas').forEach(canvas => {
    canvas.style.backgroundImage = event.target.value === 'check' ? '' : 'none';
    canvas.style.backgroundColor = event.target.value === 'check' ? '#52605b' : event.target.value;
  });
  document.addEventListener('visibilitychange', () => act(() => { hidden = document.hidden; }));
  function draw(now) { tick(now); render(); requestAnimationFrame(draw); }
  render();
  requestAnimationFrame(draw);
})();
