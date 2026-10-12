#!/usr/bin/env python3
"""Read-only frame inspection and local HTML preview for this character only."""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import sys
import time
from urllib.parse import quote
from zoneinfo import ZoneInfo

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "review"
SPECS = {
    "run": {"directions": ["N", "NE", "E", "SE", "S", "SW", "W", "NW"], "count": 16, "duration_ms": 960},
    "hit": {"directions": ["E", "W"], "count": 6, "duration_ms": 240},
    "attack": {"directions": ["E", "W"], "count": 12, "duration_ms": 360},
    "cast": {"directions": ["E", "W"], "count": 16, "duration_ms": 720},
}


def write_report(path: Path, contents: str) -> None:
    temporary = path.with_name(path.name + ".write-tmp")
    temporary.write_text(contents, encoding="utf-8")
    for attempt in range(5):
        try:
            temporary.replace(path)
            return
        except OSError:
            if attempt == 4:
                raise
            time.sleep(0.2 * (attempt + 1))


def digest(path: Path) -> str:
    value = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def resolve_path(value: str) -> Path:
    path = Path(value)
    return path.resolve() if path.is_absolute() else (ROOT / path).resolve()


def load_sources(path: Path | None) -> dict:
    if path is None:
        return {}
    raw = json.loads(path.read_text(encoding="utf-8-sig"))
    records = raw.get("frames", raw)
    if not isinstance(records, dict):
        raise ValueError("来源索引必须为对象，或包含 frames 对象。")
    return {key.replace("\\", "/").removeprefix("frames/"): value for key, value in records.items()}


def inspect_source(record: dict | None) -> dict:
    result = {"status": "unconfirmed", "native_frame_size": None, "issues": []}
    if not record:
        result["issues"].append("缺少逐帧来源记录")
        return result
    if not isinstance(record, dict):
        result["issues"].append("来源记录不是对象")
        return result
    result["record"] = record
    source = resolve_path(record["source_path"]) if record.get("source_path") else None
    if source and source.is_file():
        try:
            with Image.open(source) as image:
                image.load()
                size = list(image.size)
            result["source_size"] = size
            result["source_sha256"] = digest(source)
            if record.get("source_sha256") and record["source_sha256"].lower() != result["source_sha256"]:
                result["issues"].append("来源 SHA-256 与记录不一致")
            if record.get("source_kind") == "single_frame":
                native = size
            elif record.get("source_kind") == "sheet":
                rect = record.get("native_frame_rect")
                if not (isinstance(rect, list) and len(rect) == 4 and all(isinstance(v, int) for v in rect)):
                    result["issues"].append("来源为图集，缺少真实单帧裁切区域 native_frame_rect")
                    return result
                x, y, width, height = rect
                if min(x, y) < 0 or min(width, height) <= 0 or x + width > size[0] or y + height > size[1]:
                    result["issues"].append("原生单帧裁切区域超出源图")
                    return result
                native = [width, height]
            else:
                result["issues"].append("未声明来源是单帧还是图集，不能将整张图集尺寸当单帧尺寸")
                return result
            result["native_frame_size"] = native
            if record.get("native_frame_size") and record["native_frame_size"] != native:
                result["issues"].append("记录的原生单帧尺寸与源图/区域不一致")
            if min(native) < 1024:
                result["issues"].append("原生单帧输入不足 1024×1024")
            result["status"] = "measured_pass" if not result["issues"] else "failed"
        except Exception as error:
            result["status"] = "failed"
            result["issues"].append(f"源图读取失败：{error}")
    else:
        # Retention policy permits removal of superseded source PNGs. Report text
        # evidence separately: it cannot be silently promoted to a measurement.
        native = record.get("native_frame_size")
        evidence = resolve_path(record["evidence_path"]) if record.get("evidence_path") else None
        source_hash = record.get("source_sha256", "")
        valid_size = isinstance(native, list) and len(native) == 2 and all(isinstance(v, int) and v > 0 for v in native)
        valid_hash = isinstance(source_hash, str) and len(source_hash) == 64 and all(c in "0123456789abcdefABCDEF" for c in source_hash)
        if valid_size:
            result["native_frame_size"] = native
        if valid_size and min(native) < 1024:
            result["status"] = "failed"
            result["issues"].append("文字来源记录中的原生单帧尺寸不足 1024×1024")
        elif valid_size and valid_hash and evidence and evidence.is_file():
            result["status"] = "documented_only"
            result["issues"].append("源图未保留；尺寸与 SHA 仅来自文字证据，本次未实测")
        else:
            result["issues"].append("源图不可读取，文字来源尺寸/SHA/证据文件也不完整")
    return result


def inspect(sources: dict) -> dict:
    frames, file_hashes, pixel_hashes = [], defaultdict(list), defaultdict(list)
    notes_path = REVIEW / "visual-notes.json"
    notes = json.loads(notes_path.read_text(encoding="utf-8-sig")) if notes_path.is_file() else {"frames": {}, "actions": {}}
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8-sig"))
    timing = {f["file"].removeprefix("frames/"): f["frameDurationMs"] for f in manifest["frames"]}
    expected = set()
    for action, spec in SPECS.items():
        for direction in spec["directions"]:
            for index in range(1, spec["count"] + 1):
                key = f"{action}/{direction}/{index:02}.png"
                expected.add(key)
                path = ROOT / "frames" / key
                item = {"key": key, "action": action, "direction": direction, "index": index, "exists": path.is_file(), "issues": []}
                if not item["exists"]:
                    item["status"] = "missing"
                    frames.append(item)
                    continue
                item["frame_duration_ms"] = timing[key]
                item["url"] = "../frames/" + quote(key, safe="/")
                item["sha256"] = digest(path)
                file_hashes[item["sha256"]].append(key)
                try:
                    with Image.open(path) as image:
                        image.load()
                        item.update({"size": list(image.size), "mode": image.mode, "format": image.format})
                        if image.size != (1024, 1024):
                            item["issues"].append("正式帧尺寸不是 1024×1024")
                        if image.mode != "RGBA":
                            item["issues"].append("正式帧模式不是 RGBA")
                        if image.format != "PNG":
                            item["issues"].append("扩展名为 PNG，但文件实际格式不是 PNG")
                        pixels = image.convert("RGBA")
                        item["pixel_sha256"] = sha256(str(pixels.size).encode() + pixels.tobytes()).hexdigest()
                        pixel_hashes[item["pixel_sha256"]].append(key)
                        alpha = pixels.getchannel("A")
                        item["alpha_range"] = list(alpha.getextrema())
                        if item["alpha_range"][1] == 0:
                            item["issues"].append("整帧全透明，不能作为有效动作帧")
                        elif item["alpha_range"][0] == 255:
                            item["issues"].append("整帧完全不透明，需核实背景透明度")
                except Exception as error:
                    item["issues"].append(f"图像读取失败：{error}")
                item["source"] = inspect_source(sources.get(key))
                record = sources.get(key) or {}
                if record.get("export_sha256") and record["export_sha256"] != item["sha256"]:
                    item["issues"].append("导出 PNG 的 SHA-256 与来源索引不一致")
                item["visual_status"] = record.get("visual_status", "unreviewed_candidate")
                item["art_approved"] = False
                item["dynamic_approved"] = False
                item["runtime_approved"] = False
                item["visual_notes"] = list(notes.get("actions", {}).get(action, []))
                note = notes.get("frames", {}).get(key)
                if note:
                    note = dict(note)
                    note["source_matches_review"] = note.get("source_sha256") == item["source"].get("source_sha256")
                    if not note["source_matches_review"]:
                        note["message"] = "来源已变更，旧问题待重新审核：" + note["message"]
                    item["visual_notes"].append(note)
                item["status"] = "failed" if item["issues"] or item["source"]["status"] == "failed" else "file_pass"
                frames.append(item)
    duplicate_files = [keys for keys in file_hashes.values() if len(keys) > 1]
    duplicate_pixels = [keys for keys in pixel_hashes.values() if len(keys) > 1]
    duplicate_keys = {key for keys in duplicate_pixels for key in keys}
    for item in frames:
        if item["key"] in duplicate_keys:
            item["issues"].append("与其他槽位的 RGBA 像素完全重复")
            item["status"] = "failed"
    present = sum(item["exists"] for item in frames)
    file_pass = sum(item["status"] == "file_pass" for item in frames)
    measured = sum(item.get("source", {}).get("status") == "measured_pass" for item in frames)
    documented = sum(item.get("source", {}).get("status") == "documented_only" for item in frames)
    actual = {p.relative_to(ROOT / "frames").as_posix() for p in (ROOT / "frames").rglob("*.png")} if (ROOT / "frames").exists() else set()
    return {
        "character": ROOT.name,
        "generated_at": datetime.now(ZoneInfo("America/New_York")).isoformat(),
        "timezone": "America/New_York",
        "scope": "仅技术检查；不判断真实独立姿态、锚点、首尾衔接、手脚或道具是否符合美术要求；未运行客户端。",
        "specs": SPECS,
        "summary": {"expected": len(frames), "present": present, "missing": len(frames) - present, "file_pass": file_pass, "failed": present - file_pass, "source_measured_pass": measured, "source_documented_only": documented, "source_unconfirmed_or_failed": present - measured - documented, "fully_measured_technical_pass": file_pass == len(frames) and measured == len(frames)},
        "duplicate_file_groups": duplicate_files,
        "duplicate_pixel_groups": duplicate_pixels,
        "unexpected_pngs": sorted(actual - expected),
        "art_review": {"fully_approved_sequences": 0, "runtime_approved": False, "notes_path": "visual-notes.json", "scope": "已载入当前选帧的静态复核记录；整段动态观感、世界地面和客户端位移尚未实测。"},
        "sequence_summary": [{"action": action, "direction": direction, "expected": spec["count"], "present": sum(f["exists"] for f in frames if f["action"] == action and f["direction"] == direction), "missing_indices": [f["index"] for f in frames if f["action"] == action and f["direction"] == direction and not f["exists"]]} for action, spec in SPECS.items() for direction in spec["directions"]],
        "frames": frames,
    }


HTML = r'''<!doctype html>
<html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>00 金发带道童 · 候选动作审核</title>
<style>
:root{font-family:system-ui,"Microsoft YaHei",sans-serif;color-scheme:dark;color:#f0eee7;background:#161918}*{box-sizing:border-box}body{margin:0;padding:24px;max-width:1500px;margin:auto}h1{font-size:24px;margin:0 0 8px}p{line-height:1.6;color:#bfc9c1}button,select,input{font:inherit}button,select{background:#2b3630;border:1px solid #66746b;border-radius:6px;color:inherit;padding:8px 12px}button{cursor:pointer}button.active{background:#445e4d;border-color:#a7d5ae}.controls{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:12px 0}.layout{display:grid;grid-template-columns:minmax(360px,700px) minmax(280px,1fr);gap:24px}.stage{width:var(--display-size,240px);max-width:100%;margin:auto;aspect-ratio:1;position:relative;background-color:#ddd;background-image:linear-gradient(45deg,#c6c6c6 25%,transparent 25%),linear-gradient(-45deg,#c6c6c6 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#c6c6c6 75%),linear-gradient(-45deg,transparent 75%,#c6c6c6 75%);background-size:32px 32px;background-position:0 0,0 16px,16px -16px,-16px 0;overflow:hidden;border:1px solid #69716c}.stage img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain}.empty{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:#6d2723;background:#f5e8dc;white-space:pre-line;text-align:center;font-size:22px}.stage .label{position:absolute;left:12px;top:12px;background:#111b;color:white;padding:6px 10px;border-radius:4px;font-size:13px}.thumbs{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}.thumb{padding:0;overflow:hidden;font-size:12px}.thumb img{width:100%;display:block;background:#ddd;aspect-ratio:1;object-fit:contain}.thumb .absent{aspect-ratio:1;display:grid;place-content:center;color:#e3b4ac;background:#3b2b29}.thumb span{display:block;padding:5px}.thumb.selected{outline:2px solid #d7ce75}.small{font-size:13px;color:#b9c6bc;overflow-wrap:anywhere}.summary{border-left:4px solid #cfb971;background:#242d26;padding:12px;margin:16px 0}pre{white-space:pre-wrap;overflow-wrap:anywhere;max-height:320px;overflow:auto;font-size:12px;background:#101411;padding:12px}.slider{width:100%}a{color:#bee1b3}.bad{color:#ffb0a3}@media(max-width:850px){.layout{grid-template-columns:1fr}body{padding:12px}}
</style>
<h1>00 金发带道童 · 候选动作审核</h1><p>当前八方向跑步每圈960ms，16帧统一60ms。<a href="timing-grounding/index.html">960ms 正常与慢放检查</a>。此页按清单逐帧时长播放，默认240px；受击/普攻/施法保持40/30/45ms。</p><p id="scope"></p><div class="summary" id="summary"></div><div class="summary bad" id="artSummary"></div>
<div class="controls"><label>动作 <select id="action"><option value="run">跑步</option><option value="hit">受击</option><option value="attack">普攻</option><option value="cast">施法</option></select></label><label>方向 <select id="direction"></select></label><label>显示 <select id="display-size"><option value="160">160px</option><option value="240" selected>240px</option><option value="512">512px</option></select></label><button id="normal">正常速度（跑步960ms）</button><button id="slow">慢速 ¼</button><button id="pause">暂停</button><button id="previous">上一帧</button><button id="next">下一帧</button><label><input id="loop" type="checkbox" checked>循环检查</label></div>
<div class="layout"><main><div class="stage" id="stage"><img id="frame" alt="实际动作帧"><div class="empty" id="empty"></div><div class="label" id="label"></div></div><input class="slider" id="slider" type="range" aria-label="逐帧滑块" min="1" value="1"><div class="small" id="timing"></div><div class="summary bad" id="visualNotes"></div><p class="small">所有帧使用同一完整画布显示；缺帧保留时间槽并显示文字，不跳过、不补图。页面不进行裁切、镜像、逐帧缩放或脚底对齐。图像浏览器显示缩放不修改源文件。</p><div class="small" id="detail"></div><details><summary>当前帧技术记录</summary><pre id="record"></pre></details></main><aside><div class="thumbs" id="thumbs"></div><p class="small">逐帧点击缩略图检查。独立动作、手脚与道具、整体比例、根锚点、腾空及首尾衔接仍需人工动态验收。</p><a href="technical_report.json">完整技术报告 JSON</a></aside></div>
<script id="data" type="application/json">__REPORT__</script>
<script>
const data=JSON.parse(document.getElementById('data').textContent),$=id=>document.getElementById(id);
let sequence=[],index=0,playing=false,speed=1,last=0,elapsed=0;
$('scope').textContent=data.scope;
const s=data.summary;
$('artSummary').textContent=data.art_review.scope+' 逐帧问题及修正以当前来源SHA绑定的下方记录为准；run仍需检查全局比例、手脚相位与根锚。整段动态通过 0，客户端未运行。';
$('summary').textContent=`实际文件 ${s.present}/${s.expected} · 缺帧 ${s.missing} · 文件检查通过 ${s.file_pass} · 文件检查失败 ${s.failed} · 原生单帧尺寸实测通过 ${s.source_measured_pass} · 仅文字证据 ${s.source_documented_only} · 来源未确认/不合格 ${s.source_unconfirmed_or_failed}。以上不代表美术通过。报告：${data.generated_at}`;
function spec(){return data.specs[$('action').value]}
function stop(){playing=false;elapsed=0;refreshButtons()}
function refreshButtons(){$('normal').classList.toggle('active',playing&&speed===1);$('slow').classList.toggle('active',playing&&speed===.25);$('pause').classList.toggle('active',!playing)}
function render(){const f=sequence[index];if(!f)return;$('slider').value=index+1;$('frame').style.display=f.exists?'block':'none';$('empty').style.display=f.exists?'none':'flex';if(f.exists){$('frame').src=f.url;$('frame').alt=f.key}else{$('frame').removeAttribute('src');$('empty').textContent=`缺帧\n${f.key}\n该时间槽尚无图片`}$('label').textContent=f.key;const ms=f.frame_duration_ms;const pair=f.action==='run'?` · ${index<8?'右':'左'}脚支撑 · ${['相邻位置1','相邻位置2','相邻位置3','相邻位置4'][Math.floor((index%8)/2)]}第 ${index%2+1}/2 帧`:'';$('timing').textContent=`第 ${index+1}/${sequence.length} 帧 · 正常 ${ms} ms/帧 · ${spec().duration_ms} ms/段 · 当前${playing?(speed===1?'正常播放':'¼ 速度播放'):'暂停/逐帧'}${pair}`;$('detail').textContent=f.exists?`技术文件状态：${f.status}；美术状态：${f.visual_status??'未验收'}；源图证据：${f.source?.status??'unconfirmed'}。${[...f.issues,...(f.source?.issues??[])].join('；')}`:'未导出；无占位图片。';$('detail').classList.toggle('bad',!f.exists||f.status==='failed');$('record').textContent=JSON.stringify(f,null,2);document.querySelectorAll('.thumb').forEach((el,i)=>el.classList.toggle('selected',i===index));$('visualNotes').textContent=f.exists?'当前帧静态记录（整段动态待实播）：'+(f.visual_notes??[]).map(n=>n.message).join('；'):'此槽缺失；完整动作尚不能验收。'}
function sequenceChanged(){stop();index=0;sequence=data.frames.filter(f=>f.action===$('action').value&&f.direction===$('direction').value);$('slider').max=sequence.length;$('thumbs').replaceChildren();sequence.forEach((f,i)=>{const button=document.createElement('button');button.className='thumb';button.title=f.key;if(f.exists){const image=document.createElement('img');image.src=f.url;image.alt=f.key;image.loading='lazy';button.append(image)}else{const absent=document.createElement('div');absent.className='absent';absent.textContent='缺帧';button.append(absent)}const caption=document.createElement('span');caption.textContent=String(f.index).padStart(2,'0')+(f.status==='failed'?' · 技术失败':(f.visual_notes?.length?' · 待复核':(f.exists?' · 候选':'')));button.append(caption);button.onclick=()=>{stop();index=i;render()};$('thumbs').append(button)});render()}
function actionChanged(){const old=$('direction').value;$('direction').replaceChildren();spec().directions.forEach(value=>{const option=document.createElement('option');option.value=value;option.textContent=value;$('direction').append(option)});if(spec().directions.includes(old))$('direction').value=old;sequenceChanged()}
function play(value){if(!$('loop').checked)index=0;speed=value;playing=true;elapsed=0;last=performance.now();refreshButtons();render()}
$('display-size').onchange=()=>{$('stage').style.setProperty('--display-size',$('display-size').value+'px')};$('action').onchange=actionChanged;$('direction').onchange=sequenceChanged;$('normal').onclick=()=>play(1);$('slow').onclick=()=>play(.25);$('pause').onclick=()=>{stop();render()};$('previous').onclick=()=>{stop();index=(index-1+sequence.length)%sequence.length;render()};$('next').onclick=()=>{stop();index=(index+1)%sequence.length;render()};$('slider').oninput=()=>{stop();index=Number($('slider').value)-1;render()};$('frame').onerror=()=>{$('frame').style.display='none';$('empty').style.display='flex';$('empty').textContent=`图片读取失败\n${sequence[index]?.key??''}\n文件可能在报告生成后更改，请重新运行工具。`};
function tick(now){if(playing){elapsed+=(now-last)*speed;let changed=false;while(playing&&elapsed>=sequence[index].frame_duration_ms){elapsed-=sequence[index].frame_duration_ms;if(index===sequence.length-1){if($('loop').checked)index=0;else{stop();changed=true;break}}else index++;changed=true}if(changed)render()}last=now;requestAnimationFrame(tick)}
document.addEventListener('visibilitychange',()=>{last=performance.now();elapsed=0});actionChanged();requestAnimationFrame(tick);
</script></html>'''


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["verify", "preview", "all"], nargs="?", default="all")
    parser.add_argument("--sources", type=Path, help="来源 JSON 路径；相对路径从当前工作目录解释")
    parser.add_argument("--allow-incomplete", action="store_true", help="报告仍保留全部问题，仅不以非零退出码表示尚未齐全")
    args = parser.parse_args()
    report = inspect(load_sources(args.sources))
    REVIEW.mkdir(parents=True, exist_ok=True)
    write_report(REVIEW / "technical_report.json", json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    if args.command in ("preview", "all"):
        embedded = json.dumps(report, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
        write_report(REVIEW / "index.html", HTML.replace("__REPORT__", embedded))
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    print(f"报告: {REVIEW / 'technical_report.json'}")
    if args.command in ("preview", "all"):
        print(f"预览: {REVIEW / 'index.html'}")
    return 0 if args.allow_incomplete or report["summary"]["fully_measured_technical_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
