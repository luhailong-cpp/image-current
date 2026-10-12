"""Rebuild the adopted run timing preview without changing manifest or source PNGs.

Usage: python -X utf8 tools/render_timing_previews.py
Writes only review/timing-grounding/. Requires all eight run directions at 60 ms/frame.
"""
from pathlib import Path
import hashlib
import json
import re
import struct
import subprocess
import sys
import shutil
from datetime import datetime, timezone
from PIL import Image, features

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "review/timing-grounding"
MANIFEST = ROOT / "manifest.json"
DIRECTIONS = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")
FRAME_MS = 60
CYCLE_MS = 960
MODE_ID = "adopted-960"
SIZES = (240, 512)
PLAYBACK = ({"id": "normal", "label": "正常 1×", "rate": 1, "durationMultiplier": 1},
            {"id": "slow", "label": "慢放 0.25×", "rate": 0.25, "durationMultiplier": 4})
NOMINAL_GROUND_Y = 942

PLAYER_JS = r'''
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
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate_adopted_timing(manifest):
    """Fail before writing if an export rebuild would reintroduce obsolete run timing."""
    found = {direction: {} for direction in DIRECTIONS}
    for item in manifest["frames"]:
        match = re.fullmatch(r"frames/run/([A-Z]+)/([0-9]{2})\.png", item["file"].replace("\\", "/"))
        if not match:
            continue
        direction, number = match.group(1), int(match.group(2))
        if direction not in found or number in found[direction]:
            raise ValueError(f"Unexpected or duplicate run slot: {item['file']}")
        found[direction][number] = item.get("frameDurationMs")
    for direction, frames in found.items():
        if sorted(frames) != list(range(1, 17)) or list(frames.values()) != [FRAME_MS] * 16:
            raise ValueError(f"Manifest run/{direction} must contain 16 frames at {FRAME_MS}ms; update manifest first.")
    timing = manifest.get("runTiming", {})
    if timing.get("cycleDurationMs") != CYCLE_MS:
        raise ValueError("Manifest runTiming.cycleDurationMs must be 960; update manifest first.")
    durations = timing.get("durationsByDirection", {})
    if any(durations.get(direction) != [FRAME_MS] * 16 for direction in DIRECTIONS):
        raise ValueError("Manifest runTiming must use uniform 60ms for all eight directions.")
    return {"directions": list(DIRECTIONS), "frameCount": 128, "frameDurationMs": FRAME_MS,
            "cycleDurationMs": CYCLE_MS, "uniform": True, "passed": True}


def read_sources(manifest):
    by_number = {}
    for item in manifest["frames"]:
        match = re.fullmatch(r"frames/run/E/(\d{2})\.png", item["file"].replace("\\", "/"))
        if match:
            by_number[int(match.group(1))] = item
    sources, images = [], []
    for number in range(1, 17):
        item = by_number[number]; path = ROOT / item["file"]
        digest = sha(path)
        if digest != item["sha256"]:
            raise ValueError(f"Manifest SHA differs from current export: {path}. Update export+manifest first.")
        with Image.open(path) as im:
            if im.size != (1024, 1024) or im.mode != "RGBA":
                raise ValueError(f"Expected full 1024 RGBA export: {path}, {im.size}, {im.mode}")
            images.append(im.copy())
        sources.append({"frame": number, "file": item["file"], "sha256": digest,
                        "manifestSha256": item["sha256"], "manifestFrameDurationMs": item["frameDurationMs"],
                        "nativeSource": item.get("derivedFrom"), "exportOperation": item.get("operation"),
                        "browserPath": "../../" + item["file"].replace("\\", "/")})
    return sources, images


def animation_durations(path):
    """Read RIFF ANMF durations rather than relying on an FPS label."""
    data = path.read_bytes()
    if data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        raise ValueError(f"Not a WebP: {path}")
    pos, durations = 12, []
    while pos + 8 <= len(data):
        kind = data[pos:pos + 4]; size = struct.unpack("<I", data[pos + 4:pos + 8])[0]
        payload = data[pos + 8:pos + 8 + size]
        if kind == b"ANMF":
            durations.append(int.from_bytes(payload[12:15], "little"))
        pos += 8 + size + (size & 1)
    return durations


def verify_javascript():
    verifier = r'''
"use strict";
const fs = require("fs"), path = require("path"), assert = require("assert/strict");
const logic = require("./timing-player.js");
const data = JSON.parse(fs.readFileSync(path.join(__dirname,"review-data.json"),"utf8"));
let checks = 0;
assert.deepEqual(data.modes.map(mode => mode.id), ["adopted-960"]); checks++;
assert.equal(data.adoptedMode, "adopted-960"); checks++;
assert.deepEqual(data.playback.map(item => item.rate), [1, 0.25]); checks++;
const mode = data.modes[0];
assert.deepEqual(mode.durationsMs, Array(16).fill(60)); checks++;
assert.equal(mode.cycleMs, 960); checks++;
for (const playback of data.playback) {
  const durations = mode.durationsMs.map(ms => ms * playback.durationMultiplier);
  const cycle = mode.cycleMs * playback.durationMultiplier;
  assert.equal(logic.totalDuration(durations), cycle); checks++;
  let start = 0;
  for (let frame = 0; frame < 16; frame++) {
    assert.equal(logic.startForFrame(durations, frame), start);
    assert.equal(logic.frameAt(durations, start), frame);
    assert.equal(logic.frameAt(durations, start + durations[frame] - 0.001), frame);
    assert.equal(logic.frameAt(durations, start + cycle * 10), frame);
    assert.equal(logic.frameAt(mode.durationsMs, start * playback.rate), frame);
    start += durations[frame]; checks += 5;
  }
  assert.equal(logic.frameAt(durations, cycle), 0);
  assert.equal(logic.frameAt(durations, cycle - 0.001), 15);
  assert.equal(logic.frameAt(durations, -0.001), 15); checks += 3;
}
const html = fs.readFileSync(path.join(__dirname,"index.html"),"utf8");
const js = fs.readFileSync(path.join(__dirname,"timing-player.js"),"utf8");
const ids = [...html.matchAll(/\bid="([^"]+)"/g)].map(match => match[1]);
assert.equal(ids.length,new Set(ids).size); checks++;
for (const match of js.matchAll(/getElementById\("([^"]+)"\)/g)) {
  assert.ok(ids.includes(match[1]), "Missing control: " + match[1]); checks++;
}
const speed = html.match(/<select id="speed">([\s\S]*?)<\/select>/)[1];
assert.deepEqual([...speed.matchAll(/value="([^"]+)"/g)].map(match => Number(match[1])), [1, 0.25]); checks++;
for (const source of data.sources) {
  assert.ok(fs.existsSync(path.resolve(__dirname, source.browserPath)));
  assert.equal(source.manifestFrameDurationMs, 60); checks += 2;
}
assert.equal(data.products.length, 4); checks++;
for (const product of data.products) {
  const multiplier = product.playbackId === "normal" ? 1 : 4;
  assert.equal(product.modeId, "adopted-960");
  assert.deepEqual(product.durationsMs, Array(16).fill(60 * multiplier));
  assert.equal(product.cycleMs, 960 * multiplier);
  assert.ok(html.includes(product.file)); checks += 4;
}
process.stdout.write(JSON.stringify({status:"passed",checks,scope:"syntax separately; uniform normal/slow timing, loop boundaries, frame stepping, controls and local sources; no browser visual playback"}));
'''
    verifier_path = OUT / "verify-timing.cjs"
    verifier_path.write_text(verifier.strip() + "\n", encoding="utf-8")
    bundled = Path(sys.executable).resolve().parents[1] / "node/bin/node.exe"
    node = str(bundled) if bundled.exists() else shutil.which("node")
    if not node:
        return {"status": "not_run", "reason": "Node unavailable; verifier saved for later run"}
    subprocess.run([node, "--check", str(OUT / "timing-player.js")], check=True, capture_output=True, text=True)
    result = subprocess.run([node, str(verifier_path)], check=True, capture_output=True, text=True)
    return {"syntax": "passed", **json.loads(result.stdout)}


def html_page(data):
    payload = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
    links = " · ".join(f'<a href="{p["file"]}">{p["playbackLabel"]} {p["size"][0]}px WebP</a>' for p in data["products"])
    rows = "".join(f"<tr><th>{i:02d}</th><td>60</td><td>240</td></tr>" for i in range(1, 17))
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>00 E向跑步 · 960ms正常节奏</title>
<style>
:root{{--preview-size:240px;color-scheme:light;font-family:"Microsoft YaHei","Segoe UI",sans-serif;color:#183e35;background:#f4f3ee}}
*{{box-sizing:border-box}} body{{margin:0;padding:24px}} main{{max-width:1100px;margin:auto}}
h1{{font-size:25px;margin:0 0 10px}} p{{line-height:1.6}}
.notice{{padding:12px 16px;background:#fff1cf;border-left:4px solid #b68021;border-radius:6px}}
.controls{{display:flex;align-items:center;gap:12px;flex-wrap:wrap;padding:14px;background:#f4f3eefa;border:1px solid #d6dfd7;border-radius:10px;margin:16px 0}}
button,select{{font:inherit;color:#183e35;padding:8px 11px;border:1px solid #96b5a7;border-radius:6px;background:white;cursor:pointer}}
button:focus-visible,a:focus-visible,select:focus-visible,input:focus-visible{{outline:3px solid #b78322;outline-offset:2px}}
#play{{background:#206450;color:white}} label{{display:flex;align-items:center;gap:7px}} input[type=range]{{width:180px}}
.card{{overflow-x:auto;background:white;border:1px solid #d3ded6;border-radius:12px;padding:20px;text-align:center}}
.stage{{position:relative;width:var(--preview-size);height:var(--preview-size);margin:auto;overflow:hidden}}
body[data-background="dark"] .stage{{background:#27342f}} body[data-background="ivory"] .stage{{background:#f4eddb}}
body[data-background="checker"] .stage{{background-color:#e5e9ea;background-image:linear-gradient(45deg,#cdd5d6 25%,transparent 25%),linear-gradient(-45deg,#cdd5d6 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#cdd5d6 75%),linear-gradient(-45deg,transparent 75%,#cdd5d6 75%);background-size:20px 20px;background-position:0 0,0 10px,10px -10px,-10px 0}}
canvas{{display:block;width:100%;height:100%}} .ground-line{{display:none;position:absolute;left:0;right:0;top:{NOMINAL_GROUND_Y/1024*100:.8f}%;border-top:1px dashed #d84250;pointer-events:none}}
.show-ground .ground-line{{display:block}} .ground-line span{{position:absolute;right:2px;bottom:2px;font-size:10px;background:#fffc;color:#9a1927;padding:2px}}
.frame{{font-variant-numeric:tabular-nums}} a{{color:#24624e}} .details{{margin-top:20px;overflow-x:auto;background:white;padding:16px;border-radius:10px}}
table{{border-collapse:collapse;width:100%}} th,td{{padding:7px 12px;border-bottom:1px solid #e0e6e1;text-align:right}} th:first-child{{text-align:left}}
small{{color:#62756a}} @media(max-width:650px){{body{{padding:12px}}}}
</style></head><body data-background="checker"><main>
<h1>00 金发带道童 · E向跑步正常节奏</h1>
<p>正常1×统一960ms/圈，16帧各60ms。可慢放、暂停、逐帧查看；240×240与512×512均按完整画布等比显示。</p>
<div class="notice">八方向跑步已统一均匀时长，E向不再单独加权。此页读取当前正式E向帧；战斗动作时长不变。速度设定不等于姿态或客户端动态验收。</div>
<div class="controls">
<button id="play">暂停</button><button id="restart">从01重播</button><button id="previous">上一帧</button><button id="next">下一帧</button>
<label>逐帧 <input id="frame-slider" type="range" min="1" max="16" value="1"><output id="frame-choice">01</output></label>
<label>速度 <select id="speed"><option value="1">正常 1× · 960ms</option><option value="0.25">慢放 0.25× · 3840ms</option></select></label>
<label>显示 <select id="size"><option value="240">240×240</option><option value="512">512×512 放大检查</option></select></label>
<label><input id="ground" type="checkbox">名义地线 942/1024 · 未校准</label>
<label>背景 <select id="background"><option value="checker">棋盘格</option><option value="ivory">米白</option><option value="dark">深色</option></select></label>
</div><p id="playback-status" aria-live="polite">正在读取16张完整画布…</p>
<section class="card"><div class="stage"><canvas id="canvas-adopted-960" width="1024" height="1024" aria-label="E向跑步当前960ms节奏"></canvas><div class="ground-line"><span>名义地线 · 未校准</span></div></div>
<p class="frame" id="frame-adopted-960">读取帧…</p><p>{links}</p></section>
<details class="details"><summary>逐帧时长与来源</summary><p><a href="review-data.json">来源SHA及播放参数</a> · <a href="validation.json">编码与边界逻辑检查</a></p>
<table><thead><tr><th>帧</th><th>正常1×（ms）</th><th>慢放0.25×（ms）</th></tr></thead><tbody>{rows}</tbody><tfoot><tr><th>合计</th><td>960</td><td>3840</td></tr></tfoot></table></details>
<p><small>名义地线仅为诊断叠加线，不认定鞋底必须贴线。WebP逐帧编码时长已检查；连续视觉与客户端位移仍需实际验收。生成时间：{data["generatedAt"]}</small></p>
<script id="dataset" type="application/json">{payload}</script><script src="timing-player.js"></script></main></body></html>'''


def main():
    if not features.check("webp"):
        raise RuntimeError("Pillow runtime lacks WebP support.")
    before_manifest_sha = sha(MANIFEST)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
    timing_check = validate_adopted_timing(manifest)
    sources, images = read_sources(manifest)
    mode = {"id": MODE_ID, "label": "当前采用 960ms", "description": "正常1× · 16帧 × 60ms · 均匀时长",
            "durationsMs": [FRAME_MS] * 16, "cycleMs": CYCLE_MS}
    OUT.mkdir(parents=True, exist_ok=True)
    products, checks = [], []
    for size in SIZES:
        frames = [image.resize((size, size), Image.Resampling.LANCZOS) for image in images]
        for playback in PLAYBACK:
            durations = [FRAME_MS * playback["durationMultiplier"]] * 16
            path = OUT / f"run-E-{MODE_ID}-{playback['id']}-{size}.webp"
            frames[0].save(path, save_all=True, append_images=frames[1:], duration=durations,
                           loop=0, lossless=True, method=4, minimize_size=False, background=(0, 0, 0, 0))
            encoded = animation_durations(path)
            with Image.open(path) as check:
                count, dimensions = check.n_frames, list(check.size); all_rgba = True
                for number in range(count):
                    check.seek(number); all_rgba = all_rgba and check.mode == "RGBA"
            if count != 16 or dimensions != [size, size] or encoded != durations or not all_rgba:
                raise ValueError(f"Animation verification failed: {path}, {count}, {dimensions}, {encoded}")
            product = {"file": path.name, "sha256": sha(path), "direction": "E", "action": "run",
                       "modeId": MODE_ID, "playbackId": playback["id"], "playbackLabel": playback["label"],
                       "playbackRate": playback["rate"], "size": dimensions, "frameCount": 16,
                       "frameOrder": list(range(1, 17)), "durationsMs": encoded, "cycleMs": sum(encoded),
                       "loop": 0, "route": "derived", "alpha": "preserved",
                       "operation": "uniform full 1024 canvas downsample; no crop, translation, framewise fit, pose synthesis or interpolation",
                       "derivedFrom": sources, "artApproved": False, "dynamicReviewed": False,
                       "clientValidated": False, "timingAdopted": playback["id"] == "normal"}
            write_json(path.with_name(path.name + ".derivation.json"), product); products.append(product)
            checks.append({"file": path.name, "frameCount": count, "size": dimensions,
                           "encodedDurationsMs": encoded, "cycleMs": sum(encoded), "alpha": all_rgba, "passed": True})
    if sha(MANIFEST) != before_manifest_sha or any(sha(ROOT / s["file"]) != s["sha256"] for s in sources):
        raise RuntimeError("Manifest or exports changed during rendering; rerun after source update completes.")
    data = {"generatedAt": datetime.now(timezone.utc).isoformat(), "characterId": ROOT.name,
            "action": "run", "direction": "E", "frameOrder": list(range(1, 17)),
            "manifestFile": "manifest.json", "manifestSha256": before_manifest_sha,
            "manifestModified": False, "imagesModified": False, "combatModified": False,
            "timingAdopted": True, "adoptedMode": MODE_ID, "defaultComparison": MODE_ID,
            "status": "offline_timing_adopted_visual_review_pending", "displaySizes": list(SIZES),
            "groundReference": {"y": NOMINAL_GROUND_Y, "canvasHeight": 1024, "status": "nominal_uncalibrated", "movesArtwork": False},
            "sources": sources, "modes": [mode], "playback": list(PLAYBACK), "products": products,
            "allDirectionTimingCheck": timing_check, "dynamicReviewed": False, "clientValidated": False}
    write_json(OUT / "review-data.json", data)
    (OUT / "timing-player.js").write_text(PLAYER_JS.strip() + "\n", encoding="utf-8")
    (OUT / "index.html").write_text(html_page(data), encoding="utf-8")
    validation = {"generatedAt": data["generatedAt"], "sourceCount": len(sources), "frameOrder": data["frameOrder"],
                  "allSourceManifestHashesMatch": True, "allSources1024RGBA": True,
                  "manifestUnchanged": sha(MANIFEST) == before_manifest_sha,
                  "sourceExportsUnchanged": all(sha(ROOT / s["file"]) == s["sha256"] for s in sources),
                  "allDirectionTimingCheck": timing_check, "adoptedCycleMs": CYCLE_MS, "products": checks,
                  "javascript": verify_javascript(), "playbackVisualReview": False, "clientValidation": False}
    write_json(OUT / "validation.json", validation)
    (OUT / "README.md").write_text("""# E向跑步当前节奏预览

打开 [index.html](index.html)：正常1×为960ms/圈、16帧各60ms；慢放0.25×为3840ms/圈、各240ms。支持暂停、从01重播、上一帧、下一帧和滑块。240/512像素均显示完整画布，名义地线未校准且不移动人物。

当前输出只有 adopted-960 一个模式，normal/slow × 240/512 共4张透明动画WebP。页面及 review-data.json 只列当前产品；旧快档动画已按清理台账移除，派生文字记录作为历史证据保留；本工具不删除文件。

每张WebP配套来源及SHA记录；validation.json 核验16帧顺序、实际RIFF编码时长、透明度、画布、循环边界、逐帧控制和来源一致性。

修改导出与manifest后运行：python -X utf8 tools/render_timing_previews.py

脚本先要求manifest中八方向共128张run均为60ms且周期960ms，否则停止；再按当前E01–E16及SHA重建。脚本不改manifest、正式PNG、原生图片或战斗时长，不读取旧权重建议。此输出不代表已观看动态或完成客户端验收。
""", encoding="utf-8")
    print(json.dumps({"output": str(OUT), "animations": len(products), "sourceFrames": len(sources),
                      "modeId": MODE_ID, "normalCycleMs": CYCLE_MS, "slowCycleMs": CYCLE_MS * 4,
                      "allDirectionTimingCheck": timing_check, "manifestUnchanged": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
