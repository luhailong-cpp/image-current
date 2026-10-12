"use strict";
function totalDuration(durations) { return durations.reduce((a, b) => a + b, 0); }
function frameAt(durations, elapsedMs) {
  const total = totalDuration(durations);
  let within = ((elapsedMs % total) + total) % total;
  for (let i = 0; i < durations.length; i++) {
    if (within < durations[i]) return i;
    within -= durations[i];
  }
  return 0;
}
function startForFrame(durations, index) {
  return durations.slice(0, index).reduce((a, b) => a + b, 0);
}
if (typeof module !== "undefined") module.exports = {totalDuration, frameAt, startForFrame};
if (typeof document !== "undefined") {
  (async function boot() {
    const data = JSON.parse(document.getElementById("dataset").textContent);
    const mode = data.modes[0];
    const status = document.getElementById("playback-status");
    const images = await Promise.all(data.sources.map(source => new Promise((resolve, reject) => {
      const im = new Image();
      im.onload = () => resolve(im);
      im.onerror = () => reject(new Error("图片无法读取：" + source.file));
      im.src = source.browserPath;
    }))).catch(error => { status.textContent = error.message; throw error; });
    const canvas = document.getElementById("canvas-adopted-960");
    const context = canvas.getContext("2d");
    const frameLabel = document.getElementById("frame-adopted-960");
    const play = document.getElementById("play");
    const slider = document.getElementById("frame-slider");
    const sliderLabel = document.getElementById("frame-choice");
    let elapsed = 0, rate = 1, playing = true, lastTime = performance.now(), lastFrame = -1;
    function refreshStatus() {
      play.textContent = playing ? "暂停" : "继续";
      status.textContent = playing
        ? (rate === 1 ? "正常 1×：960ms/圈，每帧60ms。" : "慢放 0.25×：3840ms/圈，每帧240ms。")
        : "已暂停；可用上一帧、下一帧和滑块检查当前实图。";
    }
    function render(force = false) {
      const frame = frameAt(mode.durationsMs, elapsed);
      if (force || frame !== lastFrame) {
        context.clearRect(0, 0, 1024, 1024);
        context.drawImage(images[frame], 0, 0, 1024, 1024);
        frameLabel.textContent = "帧 " + String(frame + 1).padStart(2, "0")
          + " / 16 · 正式时长 " + mode.durationsMs[frame] + "ms";
        slider.value = String(frame + 1);
        sliderLabel.textContent = String(frame + 1).padStart(2, "0");
        lastFrame = frame;
      }
    }
    function alignToFrame(index) {
      const frame = ((index % 16) + 16) % 16;
      elapsed = startForFrame(mode.durationsMs, frame);
      playing = false;
      refreshStatus(); render(true);
    }
    play.addEventListener("click", () => {
      playing = !playing; lastTime = performance.now(); refreshStatus();
    });
    document.getElementById("restart").addEventListener("click", () => {
      elapsed = 0; playing = true; lastTime = performance.now(); refreshStatus(); render(true);
    });
    document.getElementById("previous").addEventListener("click", () => alignToFrame(frameAt(mode.durationsMs, elapsed) - 1));
    document.getElementById("next").addEventListener("click", () => alignToFrame(frameAt(mode.durationsMs, elapsed) + 1));
    slider.addEventListener("input", () => alignToFrame(Number(slider.value) - 1));
    document.getElementById("speed").addEventListener("change", event => {
      rate = Number(event.target.value); lastTime = performance.now(); refreshStatus();
    });
    document.getElementById("size").addEventListener("change", event => {
      document.documentElement.style.setProperty("--preview-size", event.target.value + "px");
    });
    document.getElementById("ground").addEventListener("change", event => {
      document.body.classList.toggle("show-ground", event.target.checked);
    });
    document.getElementById("background").addEventListener("change", event => {
      document.body.dataset.background = event.target.value;
    });
    document.addEventListener("visibilitychange", () => { lastTime = performance.now(); });
    function tick(now) {
      const delta = Math.max(0, now - lastTime); lastTime = now;
      if (playing && !document.hidden) elapsed += delta * rate;
      render(); requestAnimationFrame(tick);
    }
    refreshStatus(); render(true); requestAnimationFrame(tick);
    window.TIMING_PREVIEW_LOGIC = {frameAt, startForFrame, totalDuration};
  })();
}
