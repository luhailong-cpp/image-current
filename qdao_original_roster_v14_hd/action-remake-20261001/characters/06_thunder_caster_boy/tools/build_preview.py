#!/usr/bin/env python3
"""Read actual character frames; write only preview/index.html and manifest.json.

Run with Pillow-enabled Python. No image creation, conversion, interpolation,
rescaling, alignment, or runtime-file writes occur. Frame numbering defaults to 00.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image
from current_review_state import current_review
from current_run_pairs import current_run_pairs


ROOT = Path(__file__).resolve().parents[1]
SPECS = {
    "run": {"label": "跑步（960ms / 圈）", "directions": ["N", "NE", "E", "SE", "S", "SW", "W", "NW"], "count": 16, "duration_ms": 60},
    "hit": {"label": "受击", "directions": ["E", "W"], "count": 6, "duration_ms": 40},
    "attack": {"label": "普攻", "directions": ["E", "W"], "count": 12, "duration_ms": 30},
    "cast": {"label": "施法", "directions": ["E", "W"], "count": 16, "duration_ms": 45},
}


def inspect_frame(path: Path) -> dict:
    record = {"path": path.relative_to(ROOT).as_posix(), "url": "../" + path.relative_to(ROOT).as_posix(), "sha256": None, "width": None, "height": None, "mode": None, "alpha_extrema": None, "issues": []}
    if not path.is_file():
        raise FileNotFoundError(path)
    try:
        record["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        with Image.open(path) as frame:
            frame.load()
            record.update(width=frame.width, height=frame.height, mode=frame.mode)
            if frame.format != "PNG":
                record["issues"].append("文件格式不是 PNG")
            if frame.size != (1024, 1024):
                record["issues"].append(f"尺寸 {frame.width}×{frame.height}，要求 1024×1024")
            if frame.mode != "RGBA":
                record["issues"].append(f"模式 {frame.mode}，要求 RGBA")
            else:
                extrema = frame.getchannel("A").getextrema()
                record["alpha_extrema"] = list(extrema)
                if extrema[0] == 255:
                    record["issues"].append("Alpha 全不透明，需检查背景")
                if extrema[1] == 0:
                    record["issues"].append("Alpha 全透明，没有可见像素")
    except Exception as error:
        record["issues"].append(f"无法解码：{type(error).__name__}: {error}")
    record["technical_ok"] = not record["issues"]
    return record


def build_manifest(first_frame: int) -> dict:
    sequences = []
    pairs=current_run_pairs()
    for action, spec in SPECS.items():
        for direction in spec["directions"]:
            folder = ROOT / "runtime" / action / direction
            expected = list(range(first_frame, first_frame + spec["count"]))
            frames = []
            missing = []
            for number in expected:
                path = folder / f"{number:02d}.png"
                if path.is_file():
                    frame={"number": number, **inspect_frame(path)}
                    if frame['path'] in pairs:frame['contactPosition']=pairs[frame['path']]
                    frames.append(frame)
                else:
                    missing.append(number)
            expected_names = {f"{number:02d}.png" for number in expected}
            unexpected = sorted(path.name for path in folder.glob("*.png") if path.name not in expected_names) if folder.is_dir() else []
            sequences.append({
                "id": f"{action}/{direction}", "action": action,
                "label": spec["label"], "direction": direction,
                "expected_count": spec["count"], "first_frame": first_frame,
                "duration_ms": spec["duration_ms"],
                "cycle_ms": spec["duration_ms"] * spec["count"],
                "frames": frames, "missing": missing, "unexpected_files": unexpected,
                "present_count": len(frames),
                "technical_ok_count": sum(frame["technical_ok"] for frame in frames),
                "visual_approval": "unreviewed", "client_status": "not_integrated",
            })
    review=current_review()
    if review:
        for sequence in sequences:
            sequence['visual_approval']='current_frames_reviewed_offline'
    return {
        "schema_version": 1, "character_id": ROOT.name, "title": "06 雷法少年 · 动作预览",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_root": "..", "frame_naming": f"{{action}}/{{direction}}/{{number:02d}}.png, first={first_frame}",
        "expected_total": sum(sequence["expected_count"] for sequence in sequences),
        "present_total": sum(sequence["present_count"] for sequence in sequences),
        "technical_ok_total": sum(sequence["technical_ok_count"] for sequence in sequences),
        "visual_approval": "current_frames_reviewed_offline" if review else "unreviewed", "client_status": "not_integrated",
        "review_label": "手脚：当前帧已复核；离线播放已验证" if review else "手脚：复核中",
        "notes": ["只引用已存在的 runtime 帧；缺帧为空，不补帧、不复制、不镜像、不插值。", "技术检查通过不代表美术通过，原生输入分辨率与逐图来源需另行核实。", "预览保留整张画布，不按各帧包围盒缩放或贴地。", "当前未接入客户端。"],
        "sequences": sequences,
    }


HTML = r'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>06 雷法少年 · 动作预览</title>
<style>
:root{color-scheme:dark;font-family:system-ui,"Microsoft YaHei",sans-serif;background:#141b27;color:#e8eef4}*{box-sizing:border-box}body{margin:0;padding:24px}main{max-width:1280px;margin:auto}h1{font-size:25px;margin:0 0 8px}p{line-height:1.6;color:#b9c7d5}.status{display:flex;gap:12px;flex-wrap:wrap;margin:18px 0}.badge{border:1px solid #455367;padding:9px 13px;border-radius:8px}.layout{display:grid;grid-template-columns:minmax(300px,680px) minmax(270px,1fr);gap:24px}.controls{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px}select,button{font:inherit;background:#263347;color:inherit;border:1px solid #53647b;border-radius:6px;padding:8px 12px;cursor:pointer}button:hover{background:#35465e}button:disabled{opacity:.4;cursor:default}.stage{position:relative;aspect-ratio:1;width:100%;background:repeating-conic-gradient(#344054 0 25%,#293344 0 50%) 50%/32px 32px;border:1px solid #58697e;overflow:hidden}.stage.light{background:repeating-conic-gradient(#f8f5eb 0 25%,#d2cfc4 0 50%) 50%/32px 32px}.stage img{position:absolute;width:100%;height:100%;object-fit:contain;inset:0}.stage img[hidden]{display:none}.empty{position:absolute;inset:0;display:grid;place-content:center;text-align:center;padding:25px;white-space:pre-line;background:#141b2788;color:white;font-size:20px}.empty[hidden]{display:none}.meta{white-space:pre-line;overflow-wrap:anywhere;line-height:1.6;font-size:14px;background:#1b2534;padding:14px;border-radius:8px}.frames{display:flex;flex-wrap:wrap;gap:5px;margin:12px 0}.frames button{font-size:13px;min-width:43px;padding:7px}.frames button.missing{color:#ffabb0;border-style:dashed}.frames button.issue{color:#ffd28c}.frames button.current{outline:3px solid #65d7d0;outline-offset:1px}table{border-collapse:collapse;width:100%;font-size:14px;margin-top:20px}td,th{border-bottom:1px solid #3e4b60;padding:10px 6px;text-align:left}tr{cursor:pointer}tr:hover{background:#263347}.warning{color:#ffd28c}.fine{color:#73dbc2}small{font-size:12px;color:#b9c7d5}.range{width:100%;margin-top:14px}a{color:#84dfd5}details{margin-top:20px}summary{cursor:pointer}footer{font-size:13px;color:#95a6b9;margin-top:25px}@media(max-width:850px){body{padding:14px}.layout{grid-template-columns:1fr}}
</style></head><body><main>
<h1>06 雷法少年 · 动作预览</h1>
<p>固定整张画布展示。缺帧保持空缺；文件齐全与技术检查不代表美术验收通过。跑步正常1×统一960ms/圈，16帧各60ms；客户端速度未接入；可查看 <a href="timing-grounding-20261003/index.html">960ms正常与慢放接地复核</a>。</p>
<div class="status" id="totals"></div>
<div class="layout"><section>
<div class="controls"><label>动作 <select id="action"></select></label><label>方向 <select id="direction"></select></label></div>
<div class="stage" id="stage"><img id="sprite" alt="当前动作帧" hidden><div class="empty" id="empty"></div></div>
<input class="range" id="timeline" type="range" min="0" step="1" value="0" aria-label="逐帧位置">
<div class="frames" id="frames"></div>
<div class="controls"><button id="play">播放</button><button id="previous">上一帧</button><button id="next">下一帧</button><label>速度 <select id="speed"><option value="1">正常速度</option><option value="4">慢速（¼ 速度）</option></select></label><button id="background">切换底色</button></div>
<small>空格：播放 / 暂停；← →：逐帧。缺帧按原时间槽留空显示，不跳帧、不拿相邻图片代替。</small>
</section><aside><h2 id="sequence-title" style="margin-top:0;font-size:21px"></h2><p id="sequence-summary"></p><div class="meta" id="frame-meta"></div><table><thead><tr><th>序列</th><th>现有 / 目标</th><th>技术通过</th></tr></thead><tbody id="sequence-table"></tbody></table></aside></div>
<details><summary>检查范围与已知限制</summary><ul id="notes"></ul><p>SHA、PNG 解码、尺寸、RGBA 和透明范围由脚本检查。姿态连续性、持物正确性、原生分辨率、根锚点与美术质量必须结合逐图记录人工验收。序列切换和浏览器调度可能产生显示延迟，预览不代替客户端帧时序测试。</p><p><a href="manifest.json">查看 manifest.json</a></p></details>
<footer id="generated"></footer></main>
<script id="manifest" type="application/json">__MANIFEST__</script>
<script>
"use strict";
const data=JSON.parse(document.getElementById('manifest').textContent);
const $=id=>document.getElementById(id);
let sequence,slot=0,playing=false,lastTime=0,elapsed=0;
const imageCache=new Map();
function node(tag,text,cls){const n=document.createElement(tag);n.textContent=text;if(cls)n.className=cls;return n;}
for(const text of [`已落盘 ${data.present_total} / ${data.expected_total}`,`技术通过 ${data.technical_ok_total} / ${data.expected_total}`,data.review_label,'客户端：未接入']) $('totals').append(node('span',text,'badge'));
const actionNames=new Map(data.sequences.map(s=>[s.action,s.label]));
for(const [id,label] of actionNames){const option=node('option',label);option.value=id;$('action').append(option);}
for(const note of data.notes)$('notes').append(node('li',note));
$('generated').textContent=`清单生成时间（UTC）：${data.generated_at_utc}。新增或替换帧后重新运行 tools/build_preview.py 并刷新。`;
for(const item of data.sequences){const row=document.createElement('tr');row.tabIndex=0;row.append(node('td',`${item.label} ${item.direction}`),node('td',`${item.present_count} / ${item.expected_count}`,item.present_count===item.expected_count?'fine':'warning'),node('td',`${item.technical_ok_count}`));const select=()=>{$('action').value=item.action;setDirections(item.direction);};row.addEventListener('click',select);row.addEventListener('keydown',e=>{if(e.key==='Enter')select();});$('sequence-table').append(row);}
function setDirections(preferred){$('direction').replaceChildren();for(const s of data.sequences.filter(s=>s.action===$('action').value)){const o=node('option',s.direction);o.value=s.direction;$('direction').append(o);}if([...$('direction').options].some(o=>o.value===preferred))$('direction').value=preferred;selectSequence();}
function selectSequence(){sequence=data.sequences.find(s=>s.action===$('action').value&&s.direction===$('direction').value);slot=0;elapsed=0;$('timeline').max=sequence.expected_count-1;$('sequence-title').textContent=`${sequence.label} · ${sequence.direction}`;$('sequence-summary').textContent=`${sequence.duration_ms} ms / 帧 · ${sequence.cycle_ms} ms / 段；现有 ${sequence.present_count}/${sequence.expected_count}，技术通过 ${sequence.technical_ok_count}。缺帧：${sequence.missing.length?sequence.missing.map(n=>String(n).padStart(2,'0')).join('、'):'无'}${sequence.unexpected_files.length?'；规格外文件未播放：'+sequence.unexpected_files.join('、'):''}`;$('frames').replaceChildren();for(let i=0;i<sequence.expected_count;i++){const number=sequence.first_frame+i;const record=sequence.frames.find(f=>f.number===number);const b=node('button',String(number).padStart(2,'0'),!record?'missing':record.technical_ok?'':'issue');b.title=!record?'缺帧':record.issues.length?record.issues.join('；'):'技术检查通过；复核范围见页面状态';b.addEventListener('click',()=>{pause();slot=i;draw();});$('frames').append(b);}for(const frame of sequence.frames){if(!imageCache.has(frame.url)){const img=new Image();img.src=frame.url;imageCache.set(frame.url,img);}}if(!sequence.present_count)pause();$('play').disabled=!sequence.present_count;draw();}
function draw(){const number=sequence.first_frame+slot;const frame=sequence.frames.find(f=>f.number===number);$('timeline').value=slot;[...$('frames').children].forEach((b,i)=>b.classList.toggle('current',i===slot));if(!frame){$('sprite').hidden=true;$('sprite').removeAttribute('src');$('empty').hidden=false;$('empty').textContent=`${sequence.label} ${sequence.direction} · ${String(number).padStart(2,'0')}\n缺帧 · 尚未导出`;$('frame-meta').textContent=`帧 ${slot+1} / ${sequence.expected_count}\n路径：runtime/${sequence.action}/${sequence.direction}/${String(number).padStart(2,'0')}.png\n此槽位为空，未生成替代图片。`;return;}$('sprite').src=frame.url;$('sprite').hidden=false;$('empty').hidden=true;const cp=frame.contactPosition;const contact=cp?('支撑：'+cp.supportLeg+' · '+cp.positionPhase+' · 配对 '+(cp.pairFrames??[]).map(n=>String(n).padStart(2,'0')).join('/')+'（120ms）\n'):'';$('frame-meta').textContent=contact+`帧 ${slot+1} / ${sequence.expected_count} · 编号 ${String(number).padStart(2,'0')}\n${frame.width??'?'} × ${frame.height??'?'} · ${frame.mode??'无法识别'}\nAlpha 范围：${frame.alpha_extrema?.join('–')??'不可用'}\n${frame.technical_ok?(data.visual_approval==='current_frames_reviewed_offline'?'当前手脚已复核；客户端未接入':'技术检查通过；美术待验收'):'需处理：'+frame.issues.join('；')}\n路径：${frame.path}\nSHA-256：${frame.sha256??'不可用'}`;}
$('sprite').addEventListener('error',()=>{$('sprite').hidden=true;$('empty').hidden=false;$('empty').textContent='图片加载失败\n请重新生成清单，检查文件路径。';});
function pause(){playing=false;$('play').textContent='播放';elapsed=0;}
function step(delta){pause();slot=(slot+delta+sequence.expected_count)%sequence.expected_count;draw();}
$('play').onclick=()=>{playing=!playing;elapsed=0;lastTime=performance.now();$('play').textContent=playing?'暂停':'播放';};
$('previous').onclick=()=>step(-1);$('next').onclick=()=>step(1);
$('action').onchange=()=>setDirections($('direction').value);$('direction').onchange=selectSequence;
$('timeline').oninput=()=>{pause();slot=Number($('timeline').value);draw();};
$('speed').onchange=()=>{elapsed=0;};$('background').onclick=()=>$('stage').classList.toggle('light');
document.addEventListener('keydown',event=>{if(['INPUT','SELECT','BUTTON'].includes(event.target.tagName))return;if(event.code==='Space'){event.preventDefault();if(!$('play').disabled)$('play').click();}if(event.key==='ArrowLeft'){event.preventDefault();step(-1);}if(event.key==='ArrowRight'){event.preventDefault();step(1);}});
document.addEventListener('visibilitychange',()=>{lastTime=performance.now();elapsed=0;});
function animate(now){if(playing&&!document.hidden){elapsed+=Math.min(now-lastTime,250);const duration=sequence.duration_ms*Number($('speed').value);if(elapsed>=duration){const steps=Math.floor(elapsed/duration);slot=(slot+steps)%sequence.expected_count;elapsed%=duration;draw();}}lastTime=now;requestAnimationFrame(animate);}
setDirections('E');requestAnimationFrame(animate);
</script></body></html>'''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--first-frame", type=int, choices=(0, 1), default=0, help="首帧编号，默认 0（00.png）")
    parser.add_argument("--strict", action="store_true", help="存在缺帧、规格外文件或技术错误时以状态 1 退出；仍输出清单和预览")
    args = parser.parse_args()
    manifest = build_manifest(args.first_frame)
    output = ROOT / "preview"
    output.mkdir(exist_ok=True)
    serialized = json.dumps(manifest, ensure_ascii=False, indent=2)
    (output / "manifest.json").write_text(serialized + "\n", encoding="utf-8")
    embedded = serialized.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    (output / "index.html").write_text(HTML.replace("__MANIFEST__", embedded), encoding="utf-8")
    print(json.dumps({"index": str(output / "index.html"), "manifest": str(output / "manifest.json"), "present": manifest["present_total"], "expected": manifest["expected_total"], "technical_ok": manifest["technical_ok_total"], "visual_approval": manifest["visual_approval"], "client_status": "not_integrated"}, ensure_ascii=False))
    incomplete = manifest["technical_ok_total"] != manifest["expected_total"] or any(s["unexpected_files"] for s in manifest["sequences"])
    return int(args.strict and incomplete)


if __name__ == "__main__":
    raise SystemExit(main())
