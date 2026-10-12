"use strict";

(() => {
  const $ = (id) => document.getElementById(id);
  const delivery = JSON.parse($("delivery-data").textContent);
  const actions = [["hit", "受击", 6, 40], ["attack", "普攻", 12, 30], ["cast", "施法", 16, 45]];
  const fallbackGroups = actions.flatMap(([action, label, count, duration]) => ["E", "W"].map((direction) => ({
    id: `${action}-${direction}`, action, label, direction, expected: count, present: 0, durationMs: duration,
    totalDurationMs: count * duration,
    frames: Array.from({length: count}, (_, index) => ({action, direction, frame: index + 1,
      path: `runtime/${action}/${direction}/${String(index + 1).padStart(2, "0")}.png`, exists: false,
      durationMs: duration, event: null, technicalStatus: "missing", errors: ["missing-frame"]}))
  })));
  const groups = delivery.groups.length ? delivery.groups : fallbackGroups;
  let selected = 0, elapsed = 0, playing = true, speed = 1, previousTime = null, mainSignature = "", ready = false;
  const failures = new Set();
  const cards = [];
  const directionLabel = (direction) => direction === "E" ? "E · 斜前 / 右下" : "W · 斜后 / 左上";
  const frameIndex = (group) => Math.floor(elapsed / group.durationMs) % group.frames.length;
  const pathUrl = (path) => "../" + path.split("/").map(encodeURIComponent).join("/");
  const translatedStatus = {pass: "文件检查通过", invalid: "文件检查有问题", missing: "缺帧"};
  const counts = delivery.counts;
  $("summary").textContent = `已有 ${counts.present} / ${counts.expected} 帧 · 缺 ${counts.missing} 帧 · 技术通过 ${counts.technicalPass} 帧 · 待修 ${counts.invalid} 帧`;
  $("summary").classList.toggle("complete", delivery.status === "complete");
  $("built-at").textContent = delivery.builtAt ? `清单构建：${delivery.builtAt}` : "尚未运行交付构建器";

  function showImage(image, placeholder, frame) {
    const unavailable = !frame.exists || failures.has(frame.path);
    image.hidden = unavailable;
    placeholder.hidden = !unavailable;
    placeholder.textContent = !frame.exists ? `缺帧 ${String(frame.frame).padStart(2, "0")}` : "图像读取失败";
    if (unavailable || image.dataset.path === frame.path) return;
    image.dataset.path = frame.path;
    image.alt = `${frame.action} ${frame.direction} 第 ${frame.frame} 帧`;
    image.onerror = () => {
      failures.add(frame.path);
      image.hidden = true;
      placeholder.hidden = false;
      placeholder.textContent = "图像读取失败";
      mainSignature = "";
    };
    image.src = pathUrl(frame.path);
  }

  groups.forEach((group, index) => {
    const option = document.createElement("option");
    option.value = String(index);
    option.textContent = `${group.label} · ${directionLabel(group.direction)}`;
    $("group-select").append(option);
    const button = document.createElement("button");
    button.type = "button";
    button.className = "group-card";
    const stage = document.createElement("span");
    stage.className = "mini-stage stage";
    const image = document.createElement("img");
    image.draggable = false;
    const missing = document.createElement("span");
    missing.className = "missing";
    stage.append(image, missing);
    const title = document.createElement("strong");
    title.textContent = `${group.label} · ${group.direction}`;
    const meta = document.createElement("span");
    meta.className = "card-meta";
    meta.textContent = `${group.present}/${group.expected} 帧 · ${group.durationMs}ms/帧`;
    const current = document.createElement("span");
    current.className = "card-current";
    button.append(stage, title, meta, current);
    button.addEventListener("click", () => selectGroup(index));
    $("groups").append(button);
    cards.push({button, image, missing, current, lastIndex: -1});
  });

  function selectGroup(index) {
    selected = index;
    $("group-select").value = String(index);
    $("scrubber").max = String(groups[index].frames.length);
    mainSignature = "";
    render();
  }

  function detail(term, value) {
    const dt = document.createElement("dt"), dd = document.createElement("dd");
    dt.textContent = term;
    dd.textContent = value;
    $("frame-details").append(dt, dd);
  }

  function render() {
    groups.forEach((group, index) => {
      const number = frameIndex(group), card = cards[index];
      card.button.classList.toggle("selected", selected === index);
      card.button.setAttribute("aria-pressed", String(selected === index));
      if (card.lastIndex !== number || failures.has(group.frames[number].path)) {
        showImage(card.image, card.missing, group.frames[number]);
        card.current.textContent = `${String(number + 1).padStart(2, "0")} / ${group.frames.length}`;
        card.lastIndex = number;
      }
    });
    const group = groups[selected], index = frameIndex(group), frame = group.frames[index];
    const signature = `${selected}-${index}-${failures.has(frame.path)}`;
    if (signature === mainSignature) return;
    mainSignature = signature;
    $("group-title").textContent = `${group.label} · ${directionLabel(group.direction)}`;
    $("stage-label").textContent = `${group.label} ${group.direction} / ${String(frame.frame).padStart(2, "0")} / ${group.frames.length}`;
    $("scrubber").value = String(index + 1);
    $("frame-label").textContent = `第 ${index + 1} / ${group.frames.length} 帧 · 原时长 ${frame.durationMs}ms · 单轮 ${group.totalDurationMs}ms`;
    showImage($("main-image"), $("missing"), frame);
    $("frame-details").replaceChildren();
    detail("事件", frame.event || "—");
    detail("文件", translatedStatus[frame.technicalStatus] || "未检查");
    detail("尺寸", frame.width ? `${frame.width} × ${frame.height}` : "缺失");
    detail("实际模型", frame.provenance?.actualModel ?? "未披露 / 未确认");
    detail("实际质量", frame.provenance?.actualQuality ?? "未披露 / 未确认");
    detail("视觉审核", "以人工审核记录为准");
    detail("客户端", "未接入 / 未验");
    $("frame-errors").textContent = [...(frame.errors || []), ...(frame.warnings || [])].join(" · ");
    $("frame-link").hidden = !frame.exists;
    if (frame.exists) $("frame-link").href = pathUrl(frame.path);
    $("record-link").hidden = !frame.sourceRecord;
    if (frame.sourceRecord) $("record-link").href = pathUrl(frame.sourceRecord);
  }

  function setPlaying(value) {
    playing = value;
    previousTime = null;
    $("play").textContent = playing ? "暂停" : "播放";
  }

  function goToFrame(index) {
    setPlaying(false);
    const group = groups[selected];
    elapsed = ((index + group.frames.length) % group.frames.length) * group.durationMs;
    mainSignature = "";
    render();
  }

  $("play").addEventListener("click", () => setPlaying(!playing));
  $("speed").addEventListener("change", (event) => { speed = Number(event.target.value); previousTime = null; });
  $("group-select").addEventListener("change", (event) => selectGroup(Number(event.target.value)));
  $("previous").addEventListener("click", () => goToFrame(frameIndex(groups[selected]) - 1));
  $("next").addEventListener("click", () => goToFrame(frameIndex(groups[selected]) + 1));
  $("scrubber").addEventListener("input", (event) => goToFrame(Number(event.target.value) - 1));
  $("show-anchor").addEventListener("change", (event) => { $("anchor").hidden = !event.target.checked; });
  $("background").addEventListener("change", (event) => { document.body.dataset.background = event.target.value; });
  document.addEventListener("keydown", (event) => {
    if (/^(INPUT|SELECT|TEXTAREA|BUTTON)$/.test(event.target.tagName)) return;
    if (event.code === "Space") { event.preventDefault(); setPlaying(!playing); }
    if (event.code === "ArrowLeft") { event.preventDefault(); goToFrame(frameIndex(groups[selected]) - 1); }
    if (event.code === "ArrowRight") { event.preventDefault(); goToFrame(frameIndex(groups[selected]) + 1); }
  });
  document.addEventListener("visibilitychange", () => { previousTime = null; });

  function tick(now) {
    if (ready && playing && previousTime !== null && !document.hidden) elapsed += (now - previousTime) * speed;
    previousTime = now;
    render();
    requestAnimationFrame(tick);
  }
  selectGroup(0);
  // Decode existing files before advancing the clock so the first cycle is
  // inspectable at 30–45 ms per frame, even with a cold local file cache.
  const imageCache = groups.flatMap((group) => group.frames).filter((frame) => frame.exists).map((frame) => {
    const image = new Image();
    image.src = pathUrl(frame.path);
    return {image, frame};
  });
  Promise.allSettled(imageCache.map(({image, frame}) => image.decode().catch(() => {
    failures.add(frame.path);
  }))).then(() => { ready = true; previousTime = null; mainSignature = ""; });
  requestAnimationFrame(tick);
})();
