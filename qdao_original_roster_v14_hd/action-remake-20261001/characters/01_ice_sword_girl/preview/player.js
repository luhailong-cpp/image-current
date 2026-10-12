'use strict';
const data = window.PREVIEW_DATA;
const $ = (id) => document.getElementById(id);
const esc = (value) => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const label = i => 'E' + String(i + 1).padStart(2, '0');
let selection = data.selection, playing = true, speed = 1, size = 256, debug = false;
let lastTime = null, manualFrame = 0, lastNativeFrame = -1;
const images = new Map(), lanes = [];

function durationsFor(s) { return Array(16).fill(75); }

function frameAt(time, durations) {
  const total = durations.reduce((a,b) => a+b, 0);
  let remain = ((time % total) + total) % total;
  for (let i = 0; i < 16; i++) { if (remain < durations[i]) return i; remain -= durations[i]; }
  return 15;
}
function frameStart(frame, durations) { return durations.slice(0, frame).reduce((a,b) => a+b, 0); }
function sourceUrl(frame, native) {
  if (!frame?.path || frame.previewFileError) return null;
  const path = frame.path.replace(/\\/g, '/');
  if (/^(?:[a-z]+:|\/)/i.test(path)) return null;
  return new URL((native ? '../' : '') + path, window.location.href).href;
}
function getImage(frame, native) {
  const url = sourceUrl(frame, native);
  if (!url) return null;
  if (!images.has(url)) {
    const image = new Image();
    const entry = {image, ready:false, error:false};
    image.onload = () => { entry.ready = true; renderAll(); };
    image.onerror = () => { entry.error = true; renderAll(); };
    image.src = url;
    images.set(url, entry);
  }
  return images.get(url);
}
function createLane(parent, title, subtitle, durations, native=false) {
  const el = document.createElement('section'); el.className='lane';
  el.innerHTML = `<h3>${esc(title)}</h3><div class="sub muted">${esc(subtitle)}</div><div class="canvas-wrap"><canvas></canvas></div><div class="info"></div>`;
  $(parent).appendChild(el);
  const lane = {el,canvas:el.querySelector('canvas'),info:el.querySelector('.info'),durations,native,time:0,frame:0};
  lanes.push(lane); return lane;
}
const nativeLane = createLane('native-lane','正常跑步 · 1200 ms / 圈','16帧 · 每帧75 ms · 当前修稿',durationsFor(selection),true);
function resize() {
  document.documentElement.style.setProperty('--size',size+'px');
  const scale = Math.min(window.devicePixelRatio || 1, 2);
  for (const lane of lanes) { lane.canvas.width=size*scale;lane.canvas.height=size*scale; }
  renderAll();
}
function contactText(contact) {
  if (!contact) return '未知 / 尚未逐帧标定';
  if (typeof contact === 'string') return contact;
  return `左脚 ${contact.left??'unknown'}；右脚 ${contact.right??'unknown'}${contact.confidence?'；可信度 '+contact.confidence:''}${contact.evidence?'。'+contact.evidence:''}`;
}
function draw(lane) {
  const s = lane.native ? selection : data.baseline;
  const i = lane.frame = frameAt(lane.time,lane.durations), frame=s.frames[i];
  const context=lane.canvas.getContext('2d'), width=lane.canvas.width;
  context.clearRect(0,0,width,width);
  const entry=getImage(frame,lane.native);
  if (entry?.ready) {
    const image=entry.image;
    const scale=width/Math.max(image.naturalWidth,image.naturalHeight);
    // Only fit the full source canvas; never inspect alpha, crop or align the feet.
    context.drawImage(image,0,0,image.naturalWidth*scale,image.naturalHeight*scale);
  } else {
    context.fillStyle='#eac79b';context.font=`${Math.max(10,width/26)}px system-ui`;context.textAlign='center';
    context.fillText(`${label(i)} ${!frame?'空槽':entry?.error?'图片未加载':frame.previewFileError?'文件核验失败':'载入中'}`,width/2,width/2);
  }
  if(debug && Array.isArray(s.root?.point) && Array.isArray(s.canvasSize)) {
    const [rx,ry]=s.root.point, [cw,ch]=s.canvasSize;
    const x=rx/cw*width,y=ry/ch*width;
    context.save();context.strokeStyle=lane.native?'#f8bf65':'#f19494';context.lineWidth=Math.max(1,width/256);context.setLineDash([width/40,width/70]);
    context.beginPath();context.moveTo(0,y);context.lineTo(width,y);context.stroke();context.setLineDash([]);
    context.beginPath();context.moveTo(x-6,y);context.lineTo(x+6,y);context.moveTo(x,y-6);context.lineTo(x,y+6);context.stroke();context.restore();
    if(lane.native && Number.isFinite(s.root.farFootGroundY)) {
      const farY=s.root.farFootGroundY/ch*width;
      context.save();context.strokeStyle='#8bcddb';context.lineWidth=Math.max(.75,width/512);context.setLineDash([width/80,width/40]);
      context.beginPath();context.moveTo(0,farY);context.lineTo(width,farY);context.stroke();context.restore();
    }
  }
  const total=lane.durations.reduce((a,b)=>a+b,0);
  lane.info.textContent=`${label(i)} / 16 · ${lane.durations[i].toFixed(2)} ms\n${total.toFixed(2)} ms / 圈 × ${speed}（实播 ${(total/speed).toFixed(0)} ms）${lane.native?' · '+(frame?.status??'missing'):''}`;
  if(lane===nativeLane && (lastNativeFrame!==i || !playing)) {
    lastNativeFrame=i;
    $('frame-label').textContent=label(i);$('scrub').value=i+1;
    $('selected-detail').textContent=`${label(i)}：${frame?.path??'空槽'}。实际：${contactText(frame?.actualContact)}${frame?.notes?'。'+frame.notes:''}`;
    document.querySelectorAll('#frame-table tr').forEach((tr,j)=>tr.classList.toggle('current',j===i));
  }
}
function renderAll() { for(const lane of lanes) draw(lane); }
function setPlaying(value) { if(!value && playing)manualFrame=nativeLane.frame;playing=value;lastTime=null;$('play').textContent=playing?'暂停':'播放'; }
function seek(frame) { setPlaying(false);manualFrame=(frame+16)%16;for(const lane of lanes)lane.time=frameStart(manualFrame,lane.durations);renderAll(); }
function validateSelection(s) {
  if(s.characterId!=='01_ice_sword_girl'||s.direction!=='E'||!Array.isArray(s.frames)||s.frames.length!==16)throw Error('角色、方向或16槽清单不符合约定');
  s.frames.forEach((f,i)=>{if(f!==null && (f.frame!==i+1 || typeof f.path!=='string'))throw Error(`E${i+1}槽不合法`);});
  const d=s.timing?.frameDurationsMs;
  if(!Array.isArray(d)||d.length!==16||d.some(n=>n!==75))throw Error('当前跑步统一16帧 × 75ms = 1200ms，请先更新选择清单');
  return s;
}
function updateSelection(s, state) {
  selection=validateSelection(s);nativeLane.durations=durationsFor(selection);lastNativeFrame=-1;
  const count=selection.frames.filter(Boolean).length,total=nativeLane.durations.reduce((a,b)=>a+b,0);
  $('native-summary').textContent=`${count} / 16 槽有选图。正常1倍：1200 ms / 圈，16帧每帧75 ms；完整16帧连续回环，首尾不额外停顿。客户端速度尚未接入确认。`;
  $('root-summary').textContent=selection.root?`根点：${JSON.stringify(selection.root.point)}，状态 ${selection.root.status??'unknown'}。${selection.root.definition??''}`:'尚无根点定义；诊断开关不绘制臆测地面线。';
  $('load-state').textContent=state;
  $('frame-table').innerHTML=selection.frames.map((frame,i)=>`<tr><td><button class="slot" data-frame="${i}">${label(i)}</button></td><td class="${frame?'':'missing'}">${esc(frame?.path??'空槽')}<br><small>${esc(frame?.status??'missing')}</small></td><td>${esc(frame?.plannedPhase??'未标记')}</td><td>${esc(contactText(frame?.actualContact))}</td><td>${nativeLane.durations[i].toFixed(2)}</td><td>${esc(frame?.notes??'')}</td></tr>`).join('');
  $('snapshot').textContent=JSON.stringify(selection,null,2);
  renderAll();
}
$('play').onclick=()=>setPlaying(!playing);
$('prev').onclick=()=>seek((playing?nativeLane.frame:manualFrame)-1);
$('next').onclick=()=>seek((playing?nativeLane.frame:manualFrame)+1);
$('reset').onclick=()=>{for(const lane of lanes)lane.time=0;manualFrame=0;lastTime=null;renderAll();};
$('speed').onchange=e=>{speed=Number(e.target.value);lastTime=null;renderAll();};
$('size').onchange=e=>{size=Number(e.target.value);resize();};
$('debug').onchange=e=>{debug=e.target.checked;renderAll();};
$('scrub').oninput=e=>seek(Number(e.target.value)-1);
$('frame-table').onclick=e=>{const button=e.target.closest('[data-frame]');if(button)seek(Number(button.dataset.frame));};
$('reload').onclick=async()=>{try{const r=await fetch('../review/run-E-selection.json',{cache:'no-store'});if(!r.ok)throw Error('HTTP '+r.status);updateSelection(await r.json(),'已直接读取选择清单；动态读取未重新校验文件SHA，请构建脚本复核。');}catch(e){$('load-state').textContent='无法直接读取：'+e.message+'。保持已有快照；可运行构建脚本或手动载入JSON。';}};
$('selection-file').onchange=async e=>{try{if(e.target.files[0])updateSelection(JSON.parse(await e.target.files[0].text()),'已手动载入；路径仍按角色目录解析。文件SHA需由构建脚本复核。');}catch(error){$('load-state').textContent='未载入：'+error.message;}};
$('source-table').innerHTML='<table><tr><th>帧</th><th>输出 SHA256 / 与旧记录相符</th><th>历史源图 SHA256</th><th>历史源图</th></tr>'+data.baseline.frames.map(f=>`<tr><td>E${String(f.frame).padStart(2,'0')}</td><td><code>${esc(f.sha256)}</code><br>${f.hashesMatch?'相符':'不符'}</td><td><code>${esc(f.historicalSource?.sha256)}</code></td><td>${esc(f.historicalSource?.path)}<br>旧输出 ${f.nativeSize.join('×')}</td></tr>`).join('')+'</table>';
updateSelection(selection,'当前为构建时快照；'+(selection.snapshotSourceSha256?'选择清单 SHA256 '+selection.snapshotSourceSha256:'尚无选择清单'));
resize();
function animate(time) {
  if(playing && lastTime!==null){const delta=time-lastTime;for(const lane of lanes)lane.time+=delta*speed;}
  lastTime=time;renderAll();requestAnimationFrame(animate);
}
document.addEventListener('visibilitychange',()=>{lastTime=null;});
requestAnimationFrame(animate);
// Exposed pure helpers allow timing/boundary checks without asserting visual quality.
window.GROUNDING_PREVIEW={frameAt,frameStart,durationsFor,validateSelection,getState:()=>({playing,speed,size,frames:lanes.map(l=>l.frame),times:lanes.map(l=>l.time),laneKinds:lanes.map(l=>l===nativeLane?'native-phase':l.native?'native-uniform':'old-uniform'),cycleDurations:lanes.map(l=>l.durations.reduce((a,b)=>a+b,0)),selectedSlots:selection.frames.filter(Boolean).length,loadedImageCount:[...images.values()].filter(e=>e.ready).length,failedImageCount:[...images.values()].filter(e=>e.error).length})};
