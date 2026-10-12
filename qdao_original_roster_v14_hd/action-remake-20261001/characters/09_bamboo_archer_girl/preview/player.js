"use strict";
(() => {
  const $ = id => document.getElementById(id);
  const data = window.BAMBOO_PREVIEW;
  if (!data?.sequences?.length) {
    $("inventoryNotice").textContent = "库存数据缺失。请运行 tools/verify_inventory.py --write-reports；尚未提供可验收的序列。";
    return;
  }
  const sequences = data.sequences;
  const names = {hit:"受击",attack:"普攻",cast:"施法",run:"跑步"};
  const contexts = [$("dark"), $("light")].map(canvas => canvas.getContext("2d"));
  const imageCache = new Map();
  let sequenceIndex = 0, frameIndex = 0, playing = false, all = false;
  let baseTime = 0, baseOffset = 0, fixedSequence = 0, lastPainted = "";
  const frameMs = sequence => sequence.action === "run" ? Number($("runCycle").value) / sequence.count : sequence.ms;
  const totalMs = () => sequences.reduce((sum, sequence) => sum + sequence.count * frameMs(sequence), 0);
  const label = sequence => `${names[sequence.action]} ${sequence.direction}`;
  const sequenceStart = index => sequences.slice(0, index).reduce((sum, sequence) => sum + sequence.count * frameMs(sequence), 0);
  const addText = (parent, tag, text) => {const element = document.createElement(tag); element.textContent = text; parent.append(element); return element;};
  const summaryValues = [["实际帧",data.counts.slotsWithActualPng,196],["已导出",data.counts.exportedRuntimeSlots,196],["视觉通过",data.counts.visualPassedSlots,196],["动态通过",data.counts.dynamicPassedSequences,14]];
  summaryValues.forEach(([text,count,total]) => addText($("summary"),"span",`${text} ${count}/${total}`));
  $("inventoryNotice").textContent = data.checkedAtUtc ? `库存核验：${data.checkedAtUtc}。仍缺 ${data.counts.missingSlots} 帧。所有缺槽在播放中保留原时长；没有使用占位角色图或现有帧补齐。` : "尚未运行实际库存核验。以下 196 槽为目标清单，全标为未核实空缺；请运行核验脚本刷新。";
  $("anchorInfo").textContent = data.anchor?.root ? `固定根参考点：${JSON.stringify(data.anchor.root)}（仅参考线，绘制不移动图片）。依据：${data.anchor.evidence || "未提供依据"}` : "固定根锚点尚未核验；参考线仅标示画布中心，不能当作已确认地面或脚点。";
  const tbody = $("groups").querySelector("tbody");
  sequences.forEach((sequence,index) => {
    const option = addText($("sequence"),"option",`${label(sequence)} · ${sequence.present}/${sequence.count} 张 · ${frameMs(sequence) * sequence.count}ms`);
    option.value = index;
    const row = document.createElement("tr");
    [label(sequence),`${sequence.present}/${sequence.count}`,`${sequence.exports}/${sequence.count}`,`${sequence.frames.filter(frame => frame.visualApproval === "passed").length}/${sequence.count}`,sequence.dynamicApproval === "passed" ? "通过" : "待验收"].forEach(text => addText(row,"td",text));
    tbody.append(row);
  });
  const missing = sequences.flatMap(sequence => sequence.frames.filter(frame => !frame.pngExists).map(frame => frame.slot));
  $("missingList").textContent = missing.length ? missing.join(" · ") : "没有缺槽；仍须分别核验来源、视觉、动态与客户端状态。";

  function drawMissing(ctx, text, color) {
    ctx.fillStyle = color;
    ctx.textAlign = "center";
    ctx.font = "bold 44px system-ui";
    ctx.fillText(text,512,470);
    ctx.font = "28px system-ui";
    ctx.fillText(sequences[sequenceIndex].frames[frameIndex].slot,512,530);
    ctx.font = "23px system-ui";
    ctx.fillText("本槽保留，不以其他帧填充",512,585);
  }
  function renderSlots() {
    $("slots").replaceChildren();
    sequences[sequenceIndex].frames.forEach((frame,index) => {
      const button = addText($("slots"),"button",String(index + 1).padStart(2,"0"));
      button.title = `${frame.slot} · ${frame.pngExists ? "实际文件存在" : "缺帧"}`;
      button.className = `${frame.previewable ? "present" : ""} ${frame.runtimeExportExists ? "export" : ""}`;
      button.onclick = () => {pause();frameIndex = index;show();};
    });
  }
  function show(force = false) {
    const sequence = sequences[sequenceIndex], frame = sequence.frames[frameIndex];
    const paintKey = `${sequenceIndex}/${frameIndex}/${$("guides").checked}/${$("groundY").value}/${imageCache.get(frame.previewUrl)?.state}`;
    if (!force && paintKey === lastPainted) return;
    const previousSequence = lastPainted.split("/")[0];
    lastPainted = paintKey;
    if (previousSequence !== String(sequenceIndex)) renderSlots();
    $("sequence").value = sequenceIndex;
    $("timeline").max = sequence.count - 1;
    $("timeline").value = frameIndex;
    $("position").textContent = `${label(sequence)} · ${frameIndex + 1}/${sequence.count} · ${frameMs(sequence) / Number($("speed").value)}ms/帧 · 本段实际 PNG ${sequence.present}/${sequence.count}`;
    [...$("slots").children].forEach((button,index) => button.classList.toggle("active", index === frameIndex));
    $("slotInfo").replaceChildren();
    if (frame.file) {
      const link = addText($("slotInfo"),"a",frame.file);
      link.href = frame.previewUrl || "../" + frame.file;link.target = "_blank";
      addText($("slotInfo"),"span",` · ${frame.runtimeExportExists ? "runtime 文件存在" : "选定在制稿"} · 视觉 ${frame.visualApproval === "passed" ? "通过" : "待验收"} · 动态 ${frame.dynamicApproval === "passed" ? "通过" : "待验收"}${frame.technicalErrors?.length ? " · 技术项：" + frame.technicalErrors.join(", ") : ""}`);
    } else $("slotInfo").textContent = "本槽未生成或未选定，未导出、未验收。";
    const cached = imageCache.get(frame.previewUrl);
    contexts.forEach((ctx,index) => {
      ctx.clearRect(0,0,1024,1024);
      if (cached?.state === "loaded") ctx.drawImage(cached.image,0,0);
      else drawMissing(ctx,!frame.pngExists ? "缺帧 · 尚未生成" : !frame.previewable ? "尺寸或文件未通过预览检查" : cached?.state === "error" ? "真实文件载入失败" : "载入真实 PNG…",index ? "#704b37" : "#f1bf9e");
      if ($("guides").checked) {
        ctx.strokeStyle = index ? "#23735a88" : "#b5eac088";ctx.lineWidth = 2;ctx.setLineDash([8,8]);ctx.beginPath();ctx.moveTo(512,0);ctx.lineTo(512,1024);ctx.moveTo(0,512);ctx.lineTo(1024,512);ctx.stroke();ctx.setLineDash([]);
        const ground = Number($("groundY").value); ctx.strokeStyle = "#e7a052bb"; ctx.beginPath();ctx.moveTo(0,ground);ctx.lineTo(1024,ground);ctx.stroke();
        const root = data.anchor?.root;
        if (Array.isArray(root) && root.length === 2 && root.every(Number.isFinite)) {
          ctx.strokeStyle = "#e29238";ctx.beginPath();ctx.moveTo(root[0]-20,root[1]);ctx.lineTo(root[0]+20,root[1]);ctx.moveTo(root[0],root[1]-20);ctx.lineTo(root[0],root[1]+20);ctx.stroke();
        }
      }
    });
  }
  function pause() {playing = false;$("playStatus").textContent = "已暂停。可拖动滑块或使用前后按钮逐帧核验。";}
  function start(playAll) {
    all = playAll;playing = true;fixedSequence = sequenceIndex;
    baseTime = performance.now();baseOffset = (all ? sequenceStart(sequenceIndex) : 0) + frameIndex * frameMs(sequences[sequenceIndex]);
    $("playStatus").textContent = `${all ? "全部 14 段顺序播放" : "当前段循环"} · ${$("speed").value}× · 缺槽按原时长显示空缺。`;
  }
  function tick(now) {
    if (playing) {
      const elapsed = baseOffset + (now-baseTime)*Number($("speed").value);
      if (all) {
        let position = elapsed % totalMs(), index = 0;
        while (index < sequences.length - 1 && position >= sequences[index].count * frameMs(sequences[index])) {
          position -= sequences[index].count * frameMs(sequences[index]);index++;
        }
        sequenceIndex = index;frameIndex = Math.min(sequences[index].count - 1,Math.floor(position / frameMs(sequences[index])));
      } else {
        sequenceIndex = fixedSequence;frameIndex = Math.floor(elapsed / frameMs(sequences[sequenceIndex])) % sequences[sequenceIndex].count;
      }
      show();
    }
    requestAnimationFrame(tick);
  }
  $("playOne").onclick = () => start(false);$("playAll").onclick = () => start(true);$("pause").onclick = pause;
  $("prev").onclick = () => {pause();frameIndex = (frameIndex + sequences[sequenceIndex].count - 1) % sequences[sequenceIndex].count;show();};
  $("next").onclick = () => {pause();frameIndex = (frameIndex + 1) % sequences[sequenceIndex].count;show();};
  $("timeline").oninput = () => {pause();frameIndex = Number($("timeline").value);show();};
  $("sequence").onchange = () => {pause();sequenceIndex = Number($("sequence").value);frameIndex = 0;show();};
  $("speed").onchange = () => {if(playing)start(all);show(true);};
  $("guides").onchange = () => show(true);
  $("groundY").oninput = () => show(true);
  $("runCycle").onchange = () => { if(playing)start(all); sequences.forEach((seq,i) => {$("sequence").options[i].textContent = `${label(seq)} · ${seq.present}/${seq.count} 张 · ${frameMs(seq)*seq.count}ms`;}); show(true); };
  $("displaySize").onchange = () => { document.querySelectorAll(".stage").forEach(stage => {stage.style.width = $("displaySize").value === "large" ? "" : $("displaySize").value + "px";}); };
  $("displaySize").onchange();
  const urls = [...new Set(sequences.flatMap(sequence => sequence.frames.map(frame => frame.previewUrl)).filter(Boolean))];
  let loaded = 0, failed = 0;
  urls.forEach(url => {
    const image = new Image(), entry = {image,state:"loading"};imageCache.set(url,entry);
    image.onload = () => {
      if (image.naturalWidth !== 1024 || image.naturalHeight !== 1024) {entry.state="error";failed++;}
      else {entry.state="loaded";loaded++;}
      if(!playing)$("playStatus").textContent=`真实帧预载：${loaded}/${urls.length} 成功，${failed} 失败；目标缺槽 ${missing.length}。`;
      show(true);
    };
    image.onerror = () => {entry.state="error";failed++;if(!playing)$("playStatus").textContent=`真实帧预载：${loaded}/${urls.length} 成功，${failed} 失败。载入失败的槽不会用其他帧替换。`;show(true);};
    image.src = url;
  });
  if (!urls.length) $("playStatus").textContent = "当前没有可载入的 1024 PNG；仍可检查完整槽位、时长与缺帧清单。";
  show(true);requestAnimationFrame(tick);
})();
