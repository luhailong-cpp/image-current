/**
 * Read-only PNG inventory and offline animation review. No image manipulation.
 * Run: node tools/build-preview.mjs [--candidates]
 * Candidate input: character-root candidate-selection.json (an array; missing means []).
 * Writes only this character's preview/ HTML and manifest; source PNGs remain read-only.
 */
import { readFile, writeFile, mkdir, stat } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const characterRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const previewRoot = path.join(characterRoot, 'preview');
const registeredMode = process.argv.includes('--registered');
const candidateMode = process.argv.includes('--candidates') || registeredMode;
const outputHtml = registeredMode ? 'registered.html' : candidateMode ? 'candidates.html' : 'index.html';
const outputManifest = registeredMode ? 'registered-manifest.json' : candidateMode ? 'candidate-manifest.json' : 'manifest.json';
const selectionFile = path.join(characterRoot, registeredMode ? 'registered-selection.json' : 'candidate-selection.json');
const timing = JSON.parse(await readFile(path.join(characterRoot, 'animation-timing.json'), 'utf8'));
const specifications = [
  { id: 'run', label: '跑步', directions: ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'], frames: 16, frameMs: timing.run.frameMs },
  { id: 'hit', label: '受击', directions: ['E', 'W'], frames: 6, frameMs: timing.hit.frameMs },
  { id: 'attack', label: '普攻', directions: ['E', 'W'], frames: 12, frameMs: timing.attack.frameMs },
  { id: 'cast', label: '施法', directions: ['E', 'W'], frames: 16, frameMs: timing.cast.frameMs },
];
const relative = file => path.relative(characterRoot, file).split(path.sep).join('/');
const sha256 = bytes => createHash('sha256').update(bytes).digest('hex');

async function readOptional(file) {
  try { return await readFile(file); }
  catch (error) { if (error.code === 'ENOENT') return null; throw error; }
}

async function loadCandidateSelection() {
  const selections = new Map();
  if (!candidateMode) return selections;
  const raw = await readOptional(selectionFile);
  if (!raw) return selections;
  const entries = JSON.parse(raw.toString('utf8').replace(/^\uFEFF/, ''));
  if (!Array.isArray(entries)) throw new Error('candidate-selection.json 必须是条目数组；无候选时使用 []。');
  for (const [index, entry] of entries.entries()) {
    const action = specifications.find(item => item.id === entry?.action);
    if (!action || !action.directions.includes(entry.direction) || !Number.isInteger(entry.frame)
      || entry.frame < 1 || entry.frame > action.frames || typeof entry.file !== 'string' || !entry.file.trim()) {
      throw new Error(`candidate-selection.json 第 ${index + 1} 条的动作、方向、帧号或 file 无效。`);
    }
    if (entry.generationRecord != null && (typeof entry.generationRecord !== 'string' || !entry.generationRecord.trim())) {
      throw new Error(`candidate-selection.json 第 ${index + 1} 条 generationRecord 必须是文件路径。`);
    }
    if (entry.visualStatus != null && typeof entry.visualStatus !== 'string') {
      throw new Error(`candidate-selection.json 第 ${index + 1} 条 visualStatus 必须是文本。`);
    }
    const key = `${entry.action}/${entry.direction}/${entry.frame}`;
    if (selections.has(key)) throw new Error(`candidate-selection.json 重复选择槽位 ${key}。`);
    selections.set(key, entry);
  }
  return selections;
}

const candidateSelection = await loadCandidateSelection();

function candidateUrl(file) {
  const fromPreview = path.relative(previewRoot, file);
  if (path.isAbsolute(fromPreview)) return pathToFileURL(file).href;
  return fromPreview.split(path.sep).map(segment => encodeURIComponent(segment)).join('/');
}

function pngHeader(bytes) {
  const signature = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
  if (bytes.length < 33 || !bytes.subarray(0, 8).equals(signature) || bytes.toString('ascii', 12, 16) !== 'IHDR') {
    return { validHeader: false, error: '不是可识别的 PNG 文件头' };
  }
  const width = bytes.readUInt32BE(16), height = bytes.readUInt32BE(20);
  const bitDepth = bytes[24], colorType = bytes[25];
  return { validHeader: true, width, height, bitDepth, colorType, rgba: colorType === 6,
    meetsCanvasFormat: width === 1024 && height === 1024 && colorType === 6 };
}

async function inventoryFrame(action, direction, frameNumber) {
  const number = String(frameNumber).padStart(2, '0');
  const selected = candidateSelection.get(`${action.id}/${direction}/${frameNumber}`);
  const file = candidateMode
    ? (selected ? path.resolve(characterRoot, selected.file) : null)
    : path.join(characterRoot, 'final', action.id, direction, `${number}.png`);
  const bytes = file ? await readOptional(file) : null;
  const sidecars = file ? (candidateMode && selected.generationRecord
    ? [path.resolve(characterRoot, selected.generationRecord)]
    : [`${file.slice(0, -4)}.generation.json`, `${file}.generation.json`]) : [];
  const provenance = [];
  for (const sidecar of sidecars) {
    const raw = await readOptional(sidecar);
    if (!raw) continue;
    try { provenance.push({ path: relative(sidecar), data: JSON.parse(raw.toString('utf8').replace(/^\uFEFF/, '')) }); }
    catch (error) { provenance.push({ path: relative(sidecar), error: error.message, raw: raw.toString('utf8') }); }
  }
  return {
    action: action.id, direction, frame: frameNumber, file: file ? relative(file) : null, present: bytes !== null,
    url: bytes ? (candidateMode ? candidateUrl(file) : `../${relative(file)}`) + `?v=${sha256(bytes).slice(0, 12)}` : null,
    bytes: bytes?.length ?? null, sha256: bytes ? sha256(bytes) : null,
    modifiedAt: bytes ? (await stat(file)).mtime.toISOString() : null,
    png: bytes ? pngHeader(bytes) : null, provenance,
    generationRecordPresent: provenance.some(record => record.data !== undefined),
    visualAcceptance: provenance.some(record => record.data?.finalVisualPassed === true) ? '离线复核通过（逐图验收记录）' : '未由本工具判定',
    finalVisualPassed: provenance.some(record => record.data?.finalVisualPassed === true), clientAcceptance: '未接入实测', duplicateFiles: [],
    ...(candidateMode ? { selected: Boolean(selected), visualStatus: selected?.visualStatus ?? '未填写',
      generationRecord: selected?.generationRecord ?? null, formalExportInferred: false } : {}),
  };
}

const sequences = [];
for (const action of specifications) {
  for (const direction of action.directions) {
    const frames = [];
    for (let number = 1; number <= action.frames; number++) frames.push(await inventoryFrame(action, direction, number));
    sequences.push({ id: `${action.id}/${direction}`, action: action.id, label: action.label, direction,
      frameMs: action.frameMs, durationMs: action.frameMs * action.frames, frames });
  }
}
const allFrames = sequences.flatMap(sequence => sequence.frames);
const shaGroups = new Map();
for (const frame of allFrames.filter(frame => frame.present)) {
  if (!shaGroups.has(frame.sha256)) shaGroups.set(frame.sha256, []);
  shaGroups.get(frame.sha256).push(frame);
}
for (const group of shaGroups.values()) {
  if (group.length > 1) for (const frame of group) frame.duplicateFiles = group.filter(other => other !== frame).map(other => other.file);
}
const manifest = {
  schemaVersion: 1, character: '05_celestial_musician_girl', label: '05 天音少女',
  builtAtUtc: new Date().toISOString(), specifications, sequences,
  ...(candidateMode ? { mode: 'candidates', registeredReview: registeredMode, title: registeredMode ? '1024固定配准复核' : '候选预览，非正式交付',
    selectionFile: relative(selectionFile), sourceFilesModified: false, formalExportInferred: false } : {}),
  summary: {
    expected: allFrames.length, present: allFrames.filter(frame => frame.present).length,
    missing: allFrames.filter(frame => !frame.present).length,
    format1024RGBA: allFrames.filter(frame => frame.png?.meetsCanvasFormat).length,
    withGenerationRecord: allFrames.filter(frame => frame.present && frame.generationRecordPresent).length,
    duplicateFileSlots: allFrames.filter(frame => frame.duplicateFiles.length).length,
    ...(candidateMode ? { selected: candidateSelection.size,
      unselected: allFrames.filter(frame => !frame.selected).length,
      selectedMissing: allFrames.filter(frame => frame.selected && !frame.present).length } : {}),
  },
  notes: [
    ...(candidateMode ? ['候选预览，非正式交付。visualStatus 原样展示选帧记录；本工具不将任何候选自动判为通过。',
      '原生/来源尺寸以逐图记录为准；源 PNG 尺寸仅作显示，不代表已导出正式 1024×1024，生成预览不修改 PNG。'] : []),
    '这是文件库存与人工预览工具；存在、尺寸及 SHA 不代表姿态、美术、原生输入或客户端验收通过。',
    '缺失帧保留原槽位并清空显示；不镜像、不复制、不插值、不逐帧缩放或贴地。',
    '正常速度按各动作规格播放；实际显示节奏受浏览器刷新率与图像读取速度限制。',
    'PNG 检查只读取文件头；真实解码是否成功以浏览器显示与人工核验为准。',
  ],
};

const pageTitle = registeredMode ? '05 天音少女 · 1024固定配准复核' : candidateMode ? '05 天音少女 · 候选预览，非正式交付' : '05 天音少女 · 正式动作素材';
const runTimingLabel = `${timing.run.frames}帧/${timing.run.cycleMs}ms，${timing.run.frameMs}ms/帧`;
const subtitle = registeredMode ? `1024 RGBA复核导出 · 全角色统一比例与每段固定根 · 跑步${runTimingLabel} · 战斗时长保持原要求` : candidateMode
  ? `按源 PNG 整画布等比显示 · 跑步${runTimingLabel} · 未选帧保留空槽 · 未正式导出`
  : `196张1024透明素材 · 腿脚与持琴逐帧复核 · 跑步每个接地位置两张姿态，${runTimingLabel} · 客户端尚未接入实测`;
const inputInstructions = registeredMode
  ? '此页读取 registered-selection.json 的1024复核图。整段共用固定根、全角色共用统一比例；registration.json与逐图export记录保存变换。未作每帧贴地。'
  : candidateMode
  ? '根目录 candidate-selection.json 使用条目数组：{action, direction, frame, file, generationRecord?, visualStatus}。file 和 generationRecord 可用相对角色目录的路径引用本机旧素材。未选择槽位保持空白；修改选帧后执行 tools/build-preview.mjs --candidates。'
  : '正式 PNG 放入 final/动作/方向/01.png 等路径后，重新执行 tools/build-preview.mjs，并刷新此页。逐图记录支持同目录 01.generation.json 或 01.png.generation.json。';

// Escaping '<' prevents any sidecar text from ending the JSON script element.
const embeddedManifest = JSON.stringify(manifest).replace(/</g, '\\u003c').replace(/\u2028/g, '\\u2028').replace(/\u2029/g, '\\u2029');
const html = `<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>${pageTitle}</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#f5f2e9;color:#253d39;font:15px/1.6 system-ui,"Microsoft YaHei",sans-serif}header,main{max-width:1380px;margin:auto;padding:20px 28px}header{padding-bottom:8px}h1{margin:0;font-size:25px}p{margin:8px 0}.muted{color:#61716c;font-size:13px}.summary{display:flex;gap:10px;flex-wrap:wrap}.pill{padding:3px 11px;border:1px solid #d4c5a6;border-radius:30px;background:#fffdf7}main{display:grid;grid-template-columns:minmax(320px,1.2fr) minmax(280px,1fr);gap:22px}.panel{padding:18px;background:#fffdf6;border:1px solid #d9c9a7;border-radius:16px;box-shadow:0 3px 18px #254d3910}.controls{display:flex;gap:9px;align-items:center;flex-wrap:wrap;margin-bottom:12px}button,select,input{font:inherit}button,select{padding:7px 11px;background:#fffdf6;border:1px solid #b8c5b8;border-radius:8px;color:#253d39}button{cursor:pointer}button.primary,button.active{background:#285c51;color:#fff9e9;border-color:#285c51}button:focus-visible,select:focus-visible,input:focus-visible{outline:3px solid #d4a75c;outline-offset:2px}.stage{position:relative;width:100%;aspect-ratio:1;overflow:hidden;border:1px solid #b9c4ba;border-radius:10px;background-color:#e3e7e1;background-image:linear-gradient(45deg,#cdd4cc 25%,transparent 25%),linear-gradient(-45deg,#cdd4cc 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#cdd4cc 75%),linear-gradient(-45deg,transparent 75%,#cdd4cc 75%);background-size:32px 32px;background-position:0 0,0 16px,16px -16px,-16px 0}.stage.white{background:#fff}.stage.dark{background:#233536}.stage img{display:block;position:absolute;inset:0;width:100%;height:100%;object-fit:contain}.stage img[hidden]{display:none}.empty{position:absolute;inset:0;display:grid;place-content:center;gap:8px;text-align:center;background:#faf8efdb;color:#705c40;padding:20px}.empty[hidden]{display:none}.guide{display:none;position:absolute;inset:0;pointer-events:none}.guide:before{content:"";position:absolute;left:50%;height:100%;border-left:1px dashed #d14769}.guide:after{content:"";position:absolute;top:${registeredMode || !candidateMode ? 91.9921875 : 50}%;width:100%;border-top:1px dashed #d14769}.stage.guides .guide{display:block}.timeline{display:grid;grid-template-columns:repeat(8,1fr);gap:5px;margin:12px 0}.slot{padding:6px 0;min-width:0}.slot.missing{border-style:dashed;color:#886841;background:#f5eee3}.slot.active{color:#fff9e9;background:#285c51;border-color:#285c51}.slider{width:100%;accent-color:#285c51}.status{padding:9px 12px;background:#f5efe1;border-radius:8px;overflow-wrap:anywhere}h2{font-size:17px;margin:0 0 10px}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f3f1e8;padding:12px;border-radius:8px;font-size:12px;max-height:380px;overflow:auto}table{width:100%;border-collapse:collapse;font-size:13px}th,td{padding:6px;border-bottom:1px solid #e8dfcb;text-align:left}tbody tr{cursor:pointer}tbody tr.selected{background:#eef3e9}.sequence-table{max-height:345px;overflow:auto}code{overflow-wrap:anywhere}details{margin-top:14px}summary{cursor:pointer}label{display:inline-flex;gap:6px;align-items:center}#frameInfo{white-space:pre-wrap;overflow-wrap:anywhere}#currentFile{color:#265d53}.notice{border-left:3px solid #b99353;padding-left:12px}@media(max-width:850px){main{grid-template-columns:1fr;padding:15px}header{padding:18px 15px}.timeline{grid-template-columns:repeat(8,1fr)}}
</style></head><body>
<header><h1>${pageTitle}</h1><p class="muted">${subtitle}</p><div class="summary" id="summary"></div><p class="muted" id="buildTime"></p></header>
<main><section class="panel">
<div class="controls"><label>动作<select id="action"></select></label><label>方向<select id="direction"></select></label><label>背景<select id="background"><option value="checker">透明棋盘</option><option value="white">白色</option><option value="dark">深色</option></select></label></div>
<div class="stage" id="stage"><img id="sprite" alt="当前动作帧" hidden><div id="empty" class="empty"></div><div class="guide"></div></div>
<div class="timeline" id="timeline"></div><input id="scrub" class="slider" type="range" min="1" max="16" value="1" aria-label="逐帧拖动">
<div class="controls"><button id="previous" title="左方向键">上一帧</button><button id="play" class="primary">播放</button><button id="playOnce">播放一圈</button><button id="next" title="右方向键">下一帧</button><button id="first">回到首帧</button><label>速度<select id="speed"><option value="1">正常 1×</option><option value="0.25">慢速 ¼×</option><option value="0.5">慢速 ½×</option></select></label><label><input id="loop" type="checkbox" checked>循环</label></div>
<div class="controls"><label><input id="guides" type="checkbox">${registeredMode || !candidateMode ? "固定根参考线" : "画布中心参考线"}</label><span class="muted">${registeredMode || !candidateMode ? "输出根(512,942)，整段固定；透视远近脚不强行同高" : "参考线不是已确认的角色根锚点"}</span></div>
<div class="status" id="status" aria-live="polite"></div><p class="muted">空格播放／暂停，左右键逐帧。播放遇到缺图或读取失败会清空人物，不保留上一张。</p>
</section><section class="panel">
<h2>${candidateMode ? '候选库存' : '库存'}</h2><div class="sequence-table"><table><thead><tr><th>动作／方向</th><th>实际 PNG</th><th>${candidateMode ? '源图画布' : '格式符合'}</th><th>来源记录</th></tr></thead><tbody id="inventory"></tbody></table></div>
<p class="muted notice">${candidateMode ? '库存只证明文件存在；本页不自动判定美术验收。' : '接地位置依次为：落脚、承重经过、髋下向后、后侧蹬地；每个位置两张独立姿态，再换另一只脚。膝、踝与鞋掌沿运动方向连续过渡，保留正常屈膝与透视。最新复核见 provenance/foot-axis-20261004/acceptance.json。'}</p>
<h2>当前帧</h2><p><a id="currentFile" target="_blank" rel="noopener"></a></p><div id="frameInfo"></div>
<details><summary>逐图生成记录（原字段）</summary><pre id="record"></pre></details>
<details><summary>检查范围与使用说明</summary><p>方向由独立文件读取，不镜像。所有帧共用整个画布的显示比例；不裁切包围盒、不归一化人物大小、不调整脚底。1× 时长由动作规格定义，显示节奏受浏览器限制。</p><p>${inputInstructions}</p><p>人物帧所含光效、解剖左右手、连续姿态是否正确，均不能通过文件数量或 SHA 判断。重复 SHA 只作为人工检查提示。</p></details>
</section></main>
<script id="manifest-data" type="application/json">${embeddedManifest}</script>
<script>
'use strict';
const data=JSON.parse(document.getElementById('manifest-data').textContent);
const isCandidate=data.mode==='candidates';
const isRegistered=Boolean(data.registeredReview);
const el=id=>document.getElementById(id);
let sequence,frameIndex=0,playing=false,timer=null,frameToken=0,nextDeadline=0;
const cache=new Map();
const actionSelect=el('action'),directionSelect=el('direction');
for(const spec of data.specifications){const option=document.createElement('option');option.value=spec.id;option.textContent=spec.label;actionSelect.append(option)}
const summaryLabels=isCandidate?{expected:'目标槽位',selected:'已选槽位',present:'已有源 PNG',unselected:'未选择',selectedMissing:'选择但缺文件',withGenerationRecord:'有来源记录',duplicateFileSlots:'重复 SHA 槽位'}:{expected:'目标槽位',present:'已有 PNG',missing:'缺图',format1024RGBA:'1024 RGBA',withGenerationRecord:'有来源记录',duplicateFileSlots:'重复 SHA 槽位'};
for(const [key,label] of Object.entries(summaryLabels)){const item=document.createElement('span');item.className='pill';item.textContent=label+' '+data.summary[key];el('summary').append(item)}
el('buildTime').textContent='库存扫描时间（UTC）：'+data.builtAtUtc+'。新增或修改素材后请重新生成本页。';
const inventoryRows=new Map();
for(const item of data.sequences){const row=document.createElement('tr');row.tabIndex=0;const present=item.frames.filter(f=>f.present).length;const sourceSizes=[...new Set(item.frames.filter(f=>f.png?.validHeader).map(f=>f.png.width+'×'+f.png.height))].join('、')||'—';const values=[item.label+' / '+item.direction,present+'/'+item.frames.length,isCandidate?sourceSizes:item.frames.filter(f=>f.png?.meetsCanvasFormat).length,item.frames.filter(f=>f.present&&f.generationRecordPresent).length];for(const value of values){const td=document.createElement('td');td.textContent=String(value);row.append(td)}const choose=()=>{actionSelect.value=item.action;setDirections(item.direction)};row.addEventListener('click',choose);row.addEventListener('keydown',event=>{if(event.key==='Enter'){event.preventDefault();choose()}});el('inventory').append(row);inventoryRows.set(item.id,row)}
function pause(){playing=false;clearTimeout(timer);timer=null;el('play').textContent='播放'}
function setDirections(preferred){pause();directionSelect.replaceChildren();const spec=data.specifications.find(s=>s.id===actionSelect.value);for(const dir of spec.directions){const option=document.createElement('option');option.value=dir;option.textContent=dir;directionSelect.append(option)}if(spec.directions.includes(preferred))directionSelect.value=preferred;selectSequence()}
function preload(frame){if(!frame.present)return;if(cache.has(frame.url))return;const image=new Image();const entry={image,status:'loading'};cache.set(frame.url,entry);image.onload=()=>{entry.status='ready'};image.onerror=()=>{entry.status='error'};image.src=frame.url}
function selectSequence(){pause();sequence=data.sequences.find(s=>s.action===actionSelect.value&&s.direction===directionSelect.value);frameIndex=0;el('scrub').max=sequence.frames.length;el('timeline').replaceChildren();for(const frame of sequence.frames){const button=document.createElement('button');button.className='slot'+(frame.present?'':' missing');button.textContent=String(frame.frame).padStart(2,'0');button.title=frame.present?(frame.finalVisualPassed?'离线复核通过；客户端未实测':'存在文件，待人工检查'):'缺图：空槽';button.addEventListener('click',()=>{pause();frameIndex=frame.frame-1;render()});el('timeline').append(button);preload(frame)}for(const [id,row] of inventoryRows)row.classList.toggle('selected',id===sequence.id);render()}
function showEmpty(title,description){el('sprite').hidden=true;el('sprite').removeAttribute('src');el('empty').hidden=false;el('empty').replaceChildren();const strong=document.createElement('strong');strong.textContent=title;const detail=document.createElement('span');detail.textContent=description;el('empty').append(strong,detail)}
function render(){
  const frame=sequence.frames[frameIndex],token=++frameToken;
  const displayFile=frame.file||('未选择 · '+sequence.id+'/'+String(frame.frame).padStart(2,'0'));
  el('scrub').value=frame.frame;
  Array.from(el('timeline').children).forEach((button,index)=>button.classList.toggle('active',index===frameIndex));
  el('status').textContent=sequence.label+' / '+sequence.direction+' · 第 '+frame.frame+' / '+sequence.frames.length+' 帧 · '+sequence.frameMs+' ms/帧，'+sequence.durationMs+' ms/段（正常速度）';
  const stance=frame.provenance.find(record=>record.data?.stancePosition)?.data;
  if(stance)el('status').textContent+=' · '+(stance.supportLeg==='RIGHT'?'右脚':'左脚')+'支撑：'+['落脚','承重经过','髋下向后','后侧蹬地'][stance.stancePosition.positionSegment-1]+'（第'+stance.stancePosition.pairOrdinal+'/2张）';
  el('currentFile').textContent=displayFile;
  if(frame.present)el('currentFile').href=frame.url;else el('currentFile').removeAttribute('href');
  const header=frame.png;
  const availability=isCandidate
    ?(frame.present?'源文件：已存在（候选，非正式交付）':frame.selected?'源文件：已选择但缺失，画面留空':'候选：未选择，画面留空')
    :(frame.present?'文件：正式素材已存在':'文件：缺失，画面留空');
  const format=frame.present?(isCandidate
    ?(isRegistered?'格式说明：1024 × 1024 RGBA固定配准复核图；原生来源、统一比例和整段根见逐图记录。导出不自动判定美术通过。':'格式说明：以上为源 PNG 画布；原生尺寸见逐图记录。本工具未导出正式 1024 × 1024，也不判定候选通过。')
    :'规格：'+(header?.meetsCanvasFormat?'文件头符合 1024 × 1024 RGBA':'文件头不符合正式格式')):'';
  const info=[availability,
    header?.validHeader?(isCandidate?'源 PNG 画布：':'画布：')+header.width+' × '+header.height+'；PNG 色彩类型 '+header.colorType+(header.rgba?'（RGBA）':'（非 RGBA）'):'画布：'+(header?.error||'无文件'),
    format,isCandidate&&frame.selected?'选帧状态（原样记录，非自动验收）：'+frame.visualStatus:'',
    frame.present?'来源记录：'+(frame.generationRecordPresent?'已读取，详情见下方':'缺失或解析失败'):'',
    frame.sha256?'SHA-256：'+frame.sha256:'',frame.duplicateFiles.length?'相同 SHA 文件：'+frame.duplicateFiles.join('、'):'',
    isCandidate?'美术／客户端验收：本工具不判定':'美术：'+frame.visualAcceptance+'；客户端：'+frame.clientAcceptance];
  el('frameInfo').textContent=info.filter(Boolean).join('\\n');
  el('record').textContent=frame.provenance.length?JSON.stringify(frame.provenance,null,2):'没有可读取的逐图记录。';
  if(!frame.present){showEmpty((isCandidate&&!frame.selected?'未选择':'缺图')+' · '+String(frame.frame).padStart(2,'0'),displayFile);return}
  showEmpty('读取中',displayFile);
  const image=el('sprite');
  image.onload=()=>{if(token!==frameToken)return;image.hidden=false;el('empty').hidden=true};
  image.onerror=()=>{if(token!==frameToken)return;showEmpty('文件读取或解码失败',displayFile)};
  image.src=frame.url;
  if(image.complete&&image.naturalWidth>0){image.hidden=false;el('empty').hidden=true}
}
function frameDelay(){return sequence.frameMs/Number(el('speed').value)}
function schedule(){if(!playing)return;timer=setTimeout(tick,Math.max(0,nextDeadline-performance.now()))}
function tick(){if(!playing)return;if(frameIndex===sequence.frames.length-1&&!el('loop').checked){pause();return}frameIndex=(frameIndex+1)%sequence.frames.length;render();nextDeadline+=frameDelay();if(nextDeadline<performance.now()-frameDelay())nextDeadline=performance.now()+frameDelay();schedule()}
function togglePlayback(){if(playing){pause();return}playing=true;el('play').textContent='暂停';nextDeadline=performance.now()+frameDelay();schedule()}
function playOnce(){pause();frameIndex=0;el('loop').checked=false;render();togglePlayback()}
function step(amount){pause();frameIndex=(frameIndex+amount+sequence.frames.length)%sequence.frames.length;render()}
actionSelect.addEventListener('change',()=>setDirections(directionSelect.value));directionSelect.addEventListener('change',selectSequence);el('play').addEventListener('click',togglePlayback);el('playOnce').addEventListener('click',playOnce);el('previous').addEventListener('click',()=>step(-1));el('next').addEventListener('click',()=>step(1));el('first').addEventListener('click',()=>{pause();frameIndex=0;render()});el('scrub').addEventListener('input',()=>{pause();frameIndex=Number(el('scrub').value)-1;render()});el('speed').addEventListener('change',()=>{if(playing){clearTimeout(timer);nextDeadline=performance.now()+frameDelay();schedule()}});el('background').addEventListener('change',()=>{el('stage').classList.toggle('white',el('background').value==='white');el('stage').classList.toggle('dark',el('background').value==='dark')});el('guides').addEventListener('change',()=>el('stage').classList.toggle('guides',el('guides').checked));document.addEventListener('keydown',event=>{if(['INPUT','SELECT','TEXTAREA','BUTTON','A','SUMMARY'].includes(document.activeElement.tagName))return;if(event.code==='Space'){event.preventDefault();togglePlayback()}else if(event.key==='ArrowLeft'){event.preventDefault();step(-1)}else if(event.key==='ArrowRight'){event.preventDefault();step(1)}});document.addEventListener('visibilitychange',()=>{if(document.hidden)pause()});
actionSelect.value='run';setDirections('E');
</script></body></html>`;

await mkdir(previewRoot, { recursive: true });
await writeFile(path.join(previewRoot, outputManifest), `${JSON.stringify(manifest, null, 2)}\n`, 'utf8');
await writeFile(path.join(previewRoot, outputHtml), html, 'utf8');
console.log(JSON.stringify({ output: relative(path.join(previewRoot, outputHtml)), ...manifest.summary }, null, 2));
