#!/usr/bin/env python3
"""Read explicit frame inventory; audit without modifying art; build honest previews."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

sys.dont_write_bytecode = True
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "previews"
SPECS = {
    "run": (16, 60, ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]),
    "hit": (6, 40, ["E", "W"]),
    "attack": (12, 30, ["E", "W"]),
    "cast": (16, 45, ["E", "W"]),
}
SIZE = (1024, 1024)


def inside(path: Path, parent: Path = ROOT) -> Path:
    resolved = path.resolve()
    if not resolved.is_relative_to(parent.resolve()):
        raise ValueError(f"路径越过本角色目录: {resolved}")
    return resolved


def local_path(value: str, base: Path = ROOT) -> Path:
    path = Path(value)
    return inside(path if path.is_absolute() else base / path)


def gif_durations(durations: list[int]) -> list[int]:
    """GIF resolution is 10 ms; diffuse rounding while preserving total duration."""
    previous = 0
    total = 0
    result = []
    for duration in durations:
        total += duration
        boundary = int(math.floor(total / 10 + 0.5)) * 10
        result.append(max(10, boundary - previous))
        previous = boundary
    return result


def native_size(entry: dict) -> tuple[int, int] | None:
    value = entry.get("native_size", entry.get("native_dimensions"))
    if isinstance(value, dict):
        return int(value["width"]), int(value["height"])
    if isinstance(value, (list, tuple)) and len(value) == 2:
        return int(value[0]), int(value[1])
    if entry.get("native_width") is not None and entry.get("native_height") is not None:
        return int(entry["native_width"]), int(entry["native_height"])
    return None


def inspect_frame(entry: dict, index: int) -> dict:
    action = str(entry.get("action", "")).lower()
    direction = str(entry.get("direction", "")).upper()
    number = int(entry.get("frame", entry.get("frame_index", 0)))
    if action not in SPECS or direction not in SPECS[action][2]:
        raise ValueError(f"条目 {index}: 非法动作/方向 {action}/{direction}")
    if not 1 <= number <= SPECS[action][0]:
        raise ValueError(f"条目 {index}: 帧编号必须从 1 开始且不超过 {SPECS[action][0]}")
    item = {
        "action": action, "direction": direction, "frame": number,
        "path": None, "loadable": False, "technical_pass": False,
        "visual_status": entry.get("visual_status", "not_reviewed"),
        "errors": [], "warnings": [],
    }
    value = entry.get("path", entry.get("file", entry.get("png")))
    if not value:
        item["errors"].append("槽位为空：未生成，不创建占位图")
        return item
    path = local_path(str(value))
    required_path = inside(ROOT / "frames" / action / direction / f"{number:02d}.png")
    if path != required_path:
        raise ValueError(f"条目 {index}: 正式帧只接受 frames/{action}/{direction}/{number:02d}.png")
    item["path"] = path.relative_to(ROOT).as_posix()
    if path.suffix.lower() != ".png" or not path.is_file():
        item["errors"].append("未找到指定 PNG")
        return item
    item["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    supplied_hash = entry.get("sha256")
    if supplied_hash and str(supplied_hash).lower() != item["sha256"]:
        item["errors"].append("SHA256 与 inventory 不匹配")
    try:
        with Image.open(path) as image:
            image.load()
            item.update(mode=image.mode, size=list(image.size), loadable=True)
            if image.size != SIZE:
                item["errors"].append("正式帧必须是 1024×1024；此工具不会补像素或缩放导出")
                item["loadable"] = False
            if image.mode != "RGBA":
                item["errors"].append("正式帧必须是 RGBA")
            alpha = image.convert("RGBA").getchannel("A")
            histogram = alpha.histogram()
            item["alpha"] = {
                "extrema": list(alpha.getextrema()),
                "fully_transparent_pixels": histogram[0],
                "partial_alpha_pixels": sum(histogram[1:255]),
                "fully_opaque_pixels": histogram[255],
                "bbox_diagnostic_only": alpha.getbbox(),
            }
            if not histogram[0]:
                item["errors"].append("没有完全透明像素，需确认背景与透明通道")
            if alpha.getbbox() is None:
                item["errors"].append("整张为空白透明图")
                item["loadable"] = False
            w, h = image.size
            edges = [alpha.crop(box).getextrema()[1] for box in
                     [(0, 0, w, 1), (0, h-1, w, h), (0, 0, 1, h), (w-1, 0, w, h)]]
            if max(edges) > 8:
                item["warnings"].append("画布边缘含非透明像素，请视觉检查裁切；不自动移动或缩放")
    except (OSError, ValueError) as exc:
        item["errors"].append(f"PNG 读取失败: {exc}")
        item["loadable"] = False
    source_size = native_size(entry)
    item["native_size_claim"] = list(source_size) if source_size else None
    item["native_evidence"] = entry.get("native_evidence", entry.get("source_record"))
    if source_size is None:
        item["errors"].append("原生尺寸未确认：当前 PNG 尺寸不能证明原生输入尺寸")
    elif min(source_size) < 1024:
        item["errors"].append("原生单帧输入低于 1024；小格或放大图不能算正式高清帧")
    if source_size and not item["native_evidence"]:
        item["warnings"].append("原生尺寸为清单声明，未提供 native_evidence/source_record 来源引用")
    item["technical_pass"] = not item["errors"]
    return item


def font(size: int):
    candidate = Path("C:/Windows/Fonts/arial.ttf")
    return ImageFont.truetype(str(candidate), size) if candidate.exists() else ImageFont.load_default()


def make_card(item: dict, sequence: dict, anchor: list[float] | None) -> Image.Image:
    """Fixed whole-canvas 0.5 display scale. No bbox normalization, pose warp or reanchoring."""
    image = Image.new("RGB", (512, 566), "#162331")
    draw = ImageDraw.Draw(image)
    for y in range(0, 512, 32):
        for x in range(0, 512, 32):
            draw.rectangle((x, y, x+31, y+31), fill="#d9dde2" if (x//32+y//32)%2 else "#f1f3f5")
    with Image.open(ROOT / item["path"]) as source:
        # Same full-canvas preview transform is applied to every frame.
        rgba = source.convert("RGBA").resize((512, 512), Image.Resampling.LANCZOS)
        image.paste(rgba, (0, 0), rgba)
    if anchor is not None:
        x, y = anchor[0]/2, anchor[1]/2
        draw.line((x-7, y, x+7, y), fill="#1179cc", width=1)
        draw.line((x, y-7, x, y+7), fill="#1179cc", width=1)
    label = "OFFLINE REVIEW COMPLETE / CLIENT PENDING" if sequence.get("offline_review_complete") else ("COMPLETE INVENTORY / VISUAL REVIEW REQUIRED" if sequence["complete"] else "PARTIAL PREVIEW / MISSING SLOTS")
    draw.text((10, 518), f"{item['action']} {item['direction']}  frame {item['frame']:02d}  ({len(sequence['available'])}/{sequence['expected']})", font=font(16), fill="white")
    draw.text((10, 543), label, font=font(12), fill="#ffdc87")
    return image


def make_animations(sequence: dict, anchor: list[float] | None) -> dict:
    available = sequence["available"]
    # Incomplete sets remain inspectable in HTML, where every missing slot is
    # retained in the timeline. Never compress an incomplete set into a GIF.
    if not sequence["complete"]:
        for speed in ["normal", "slow"]:
            stale = inside(OUTPUT / f"{sequence['action']}-{sequence['direction']}-{speed}.gif", OUTPUT)
            if stale.is_file():
                stale.unlink()
        return {}
    cards = [make_card(item, sequence, anchor) for item in available]
    base = OUTPUT / f"{sequence['action']}-{sequence['direction']}"
    outputs = {}
    for speed, factor in [("normal", 1), ("slow", 4)]:
        exact = [sequence["frame_ms"] * factor for _ in cards]
        rounded = gif_durations(exact)
        # Frame label differs even for identical pixels; GIF does not conceal duplicates.
        path = inside(base.with_name(base.name + f"-{speed}.gif"), OUTPUT)
        cards[0].save(path, save_all=True, append_images=cards[1:], duration=rounded,
                      loop=0, disposal=2, optimize=False)
        with Image.open(path) as reopened:
            observed = []
            for index in range(reopened.n_frames):
                reopened.seek(index)
                observed.append(reopened.info.get("duration", 0))
        outputs[speed] = {"file": path.name, "requested_durations_ms": exact,
                          "gif_durations_ms": observed, "frame_count": len(cards),
                          "gif_timing_note": "GIF 按 10ms 精度量化；HTML 播放使用规格时长。"}
    return outputs


HTML = r'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>02 火符少年 · 逐帧动作验收</title><style>
body{margin:0;background:#10202d;color:#eef3f7;font:15px system-ui,"Microsoft YaHei",sans-serif}main{max-width:1250px;margin:auto;padding:24px}h1{font-size:24px}button,select{font:inherit;background:#263d50;color:white;border:1px solid #657d8e;border-radius:6px;padding:8px;margin:3px;cursor:pointer}button.active{background:#ad541a}small,.note{color:#c8d4db}.layout{display:grid;grid-template-columns:minmax(300px,680px) minmax(260px,1fr);gap:24px}.stage{position:relative;aspect-ratio:1;background:repeating-conic-gradient(#d7dce2 0% 25%,#f0f3f5 0% 50%) 50%/32px 32px;overflow:hidden}.stage img{width:100%;height:100%;object-fit:contain;image-rendering:auto}.stage .empty{display:none;color:#562315;position:absolute;inset:0;place-items:center;font-weight:bold}.cross{position:absolute;color:#0077ba;pointer-events:none;transform:translate(-50%,-50%);font:22px monospace}.badge{padding:12px;background:#5e3617;border-radius:7px;margin:12px 0}.slots{display:flex;flex-wrap:wrap}.slots button{min-width:40px}.slots .missing{opacity:.5;border-style:dashed}.slots .pass{border-color:#5cac91}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#1c3040;padding:12px;font-size:12px}.timeline{width:100%}a{color:#8bceff}.summary{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:8px}.summary button{text-align:left}@media(max-width:760px){.layout{grid-template-columns:1fr}main{padding:12px}}
</style><main><h1>02 火符少年 · 动作验收</h1><p class="note">只展示清单中实际存在的图。缺帧显示文字空槽；不插值、不镜像、不重复补帧。固定全画布显示，根锚点仅作参考标记，不自动贴地。跑步正常1×为960ms（每帧60ms）；慢放为3840ms。</p>
<p><a href="run-grounding.html">八方向跑步 · 960ms正常 / 慢放 / 逐帧</a></p><div id="total" class="badge"></div><div class="summary" id="summary"></div><div class="layout"><section><h2 id="title"></h2><div id="stage" class="stage"><img id="frame" alt="当前实际动作帧"><div id="empty" class="empty"></div><div id="cross" class="cross">＋</div></div><div><button id="bg-checker">棋盘格</button><button id="bg-light">浅底</button><button id="bg-dark">深底</button></div><div id="state" class="badge"></div><button id="normal">正常速度</button><button id="slow">慢速 ×4</button><button id="stop">暂停</button><button id="previous">上一槽</button><button id="next">下一槽</button><input id="slider" class="timeline" type="range" min="1" step="1"><div id="slots" class="slots"></div></section><aside><h2>来源与技术检查</h2><p class="note">技术通过不代表美术或动态验收通过。正常/慢速均保留全部规格槽位与时长；缺帧时播放文字空槽，不跳帧、不复制上一帧。只有槽位齐全时生成 GIF；美术与动态验收另记。</p><p id="links"></p><pre id="detail"></pre><p><a href="technical-report.json">完整技术审计 JSON</a></p></aside></div></main><script>
const report=__REPORT__;const preloadAll=report.sequences.flatMap(s=>s.available).map(f=>new Promise(resolve=>{const img=new Image();img.onload=()=>resolve(true);img.onerror=()=>resolve(false);img.src='../'+f.path.split('/').map(encodeURIComponent).join('/')+'?sha='+f.sha256}));let current=0,slot=1,timer=null,factor=1;const byId=x=>document.getElementById(x);const seq=()=>report.sequences[current];
byId('total').textContent=`目标 ${report.target_frames} 帧；实际可预览 ${report.loadable_frames} 帧；技术通过 ${report.technical_pass_frames} 帧。${report.loadable_frames<report.target_frames?'本页为部分成果预览。':(report.offline_materials_complete?'素材及离线手脚复核完成；客户端未接入。':'库存已齐，仍需视觉及动态验收。')}`;
report.sequences.forEach((s,i)=>{const b=document.createElement('button');b.textContent=`${s.action} ${s.direction}：${s.available.length}/${s.expected}`;b.onclick=()=>select(i);byId('summary').append(b)});
let playbackStart=0,playbackSlot=1;function stop(){cancelAnimationFrame(timer);timer=null}
function show(n){slot=n;const s=seq(),f=s.available.find(x=>x.frame===slot);byId('slider').value=slot;byId('state').textContent=`${s.complete?'库存齐全':'部分预览'} · 槽位 ${slot}/${s.expected} · 单帧 ${s.frame_ms}ms / 整段 ${s.duration_ms}ms · 缺帧：${s.missing.join(', ')||'无'}`;byId('frame').style.visibility=f?'visible':'hidden';byId('empty').style.display=f?'none':'grid';byId('empty').textContent='此槽位未生成或 PNG 无法读取';if(f){byId('frame').src='../'+f.path.split('/').map(encodeURIComponent).join('/')+'?sha='+f.sha256;byId('detail').textContent=JSON.stringify(f,null,2)}else{byId('frame').removeAttribute('src');byId('detail').textContent=JSON.stringify(s.entries.find(x=>x.frame===slot)||{action:s.action,direction:s.direction,frame:slot,status:'未生成；无占位图'},null,2)}Array.from(byId('slots').children).forEach((b,i)=>b.classList.toggle('active',i+1===slot))}
function select(i){stop();current=i;const s=seq();byId('normal').textContent=s.action==='run'?'正常 1× · 960ms':'正常速度';byId('title').textContent=`${s.action} / ${s.direction}`;byId('slider').max=s.expected;byId('slots').replaceChildren();for(let n=1;n<=s.expected;n++){const f=s.available.find(x=>x.frame===n),b=document.createElement('button');b.textContent=String(n).padStart(2,'0');b.className=f?(f.technical_pass?'pass':''):'missing';b.onclick=()=>{stop();show(n)};byId('slots').append(b)}byId('links').replaceChildren();for(const [key,value] of Object.entries(s.animations)){const a=document.createElement('a');a.href=value.file;a.textContent=key==='normal'?'正常速度 GIF':'慢速 GIF';a.style.marginRight='12px';byId('links').append(a)}const a=report.root_anchor;byId('cross').style.display=a?'block':'none';if(a){byId('cross').style.left=(a[0]/1024*100)+'%';byId('cross').style.top=(a[1]/1024*100)+'%'}show(s.available[0]?.frame||1)}
function nextSlot(n,expected){return n%expected+1}function tick(){const elapsed=Math.max(0,performance.now()-playbackStart);const n=(playbackSlot-1+Math.floor(elapsed/(seq().frame_ms*factor)))%seq().expected+1;if(n!==slot)show(n);timer=requestAnimationFrame(tick)}async function play(f){stop();factor=f;const selected=current;await Promise.all(preloadAll);if(current===selected){playbackSlot=slot;playbackStart=performance.now();timer=requestAnimationFrame(tick)}}byId('bg-checker').onclick=()=>byId('stage').style.background='';byId('bg-light').onclick=()=>byId('stage').style.background='#f6f0e5';byId('bg-dark').onclick=()=>byId('stage').style.background='#182331';byId('normal').onclick=()=>play(1);byId('slow').onclick=()=>play(4);byId('stop').onclick=stop;byId('previous').onclick=()=>{stop();show((slot+seq().expected-2)%seq().expected+1)};byId('next').onclick=()=>{stop();show(slot%seq().expected+1)};byId('slider').oninput=e=>{stop();show(+e.target.value)};select(Math.max(0,report.sequences.findIndex(s=>s.available.length)));
</script></html>'''


def build(manifest_path: Path, anchor_override: list[float] | None) -> dict:
    manifest_path = inside(manifest_path)
    data = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    entries = data if isinstance(data, list) else data.get("frames", data.get("images", data.get("entries", [])))
    if not isinstance(entries, list):
        raise ValueError("manifest.frames 必须是数组")
    anchor = anchor_override if anchor_override is not None else (data.get("root_anchor") if isinstance(data, dict) else None)
    if anchor is not None and (len(anchor) != 2 or any(not 0 <= float(x) <= 1024 for x in anchor)):
        raise ValueError("root_anchor 必须是 1024 画布内的 [x,y]；不知道时请省略，不伪造已对齐结论")
    inspected = [inspect_frame(entry, index+1) for index, entry in enumerate(entries)]
    seen = set()
    hashes: dict[str, list[str]] = {}
    for item in inspected:
        key = (item["action"], item["direction"], item["frame"])
        if key in seen:
            raise ValueError(f"同一槽位重复列入：{key}")
        seen.add(key)
        if "sha256" in item:
            hashes.setdefault(item["sha256"], []).append(f"{key[0]}/{key[1]}/{key[2]:02d}")
    for item in inspected:
        if len(hashes.get(item.get("sha256", ""), [])) > 1:
            item["errors"].append("多个槽位 SHA256 完全相同，不得以复制帧充数")
            item["technical_pass"] = False
    inside(OUTPUT).mkdir(parents=True, exist_ok=True)
    sequences = []
    for action, (expected, ms, directions) in SPECS.items():
        for direction in directions:
            subset = sorted([x for x in inspected if x["action"] == action and x["direction"] == direction], key=lambda x:x["frame"])
            available = [x for x in subset if x["loadable"]]
            missing = [n for n in range(1, expected+1) if not any(x["frame"] == n for x in available)]
            sequence = {"action": action, "direction": direction, "expected": expected,
                        "frame_ms": ms, "duration_ms": expected * ms,
                        "complete": not missing, "missing": missing,
                        "entries": subset, "available": available,
                        "offline_review_complete": bool(data.get("offline_materials_complete",False))}
            sequence["animations"] = make_animations(sequence, anchor)
            sequences.append(sequence)
    report = {"character": "02_fire_talisman_boy", "generated_at_utc": datetime.now(timezone.utc).isoformat(),
              "manifest": manifest_path.relative_to(ROOT).as_posix(), "target_frames": 196,
              "offline_materials_complete": bool(data.get("offline_materials_complete",False)),
              "client_integrated": False,
              "canvas": [1024, 1024], "root_anchor": anchor,
              "root_anchor_note": "仅绘制统一参考标记；不证明图片已对齐；不读取 bbox 进行归一化",
              "loadable_frames": sum(x["loadable"] for x in inspected),
              "listed_frames": len(inspected),
              "technical_pass_frames": sum(x["technical_pass"] for x in inspected),
              "technical_failure_frames": sum(bool(x["errors"]) for x in inspected),
              "duplicate_sha256": {h:slots for h,slots in hashes.items() if len(slots)>1},
              "visual_review_note": "文件齐全、原生尺寸声明或 SHA 不同均不代表美术及动态通过；工具不自动判定视觉通过。",
              "sequences": sequences}
    inside(OUTPUT / "technical-report.json", OUTPUT).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    inside(OUTPUT / "index.html", OUTPUT).write_text(HTML.replace("__REPORT__", json.dumps(report, ensure_ascii=False).replace("<", "\\u003c")), encoding="utf-8")
    template = ROOT / "tools" / "run-grounding-template.html"
    if template.is_file():
        (OUTPUT / "run-grounding.html").write_text(template.read_text(encoding="utf-8"), encoding="utf-8")
    return report


def self_test() -> None:
    assert sum(spec[0] * len(spec[2]) for spec in SPECS.values()) == 196
    assert gif_durations([45]*16) == [50, 40]*8
    assert sum(gif_durations([45]*16)) == 720
    assert gif_durations([30]*16) == [30]*16
    assert gif_durations([40]*6) == [40]*6
    assert gif_durations([180]*16) == [180]*16
    assert native_size({"native_size": [1024, 1536]}) == (1024, 1536)
    assert native_size({"native_width": 2048, "native_height": 2048}) == (2048, 2048)
    assert native_size({}) is None
    assert inside(ROOT / "previews" / "example.png").parent == OUTPUT
    try:
        inside(ROOT.parent / "other_character.png")
    except ValueError:
        pass
    else:
        raise AssertionError("越界路径必须被拒绝")
    assert "bbox" not in make_card.__code__.co_names
    print("PASS: 196-slot spec, exact timing totals, native-size parsing, path boundary; no image fixtures created.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, help="角色目录内的 JSON 清单；图片路径相对于角色目录")
    parser.add_argument("--anchor", type=float, nargs=2, metavar=("X", "Y"), help="已确定的统一根锚点；省略时读取 manifest.root_anchor")
    parser.add_argument("--self-test", action="store_true", help="纯逻辑自检，不创建假帧或测试图片")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if not args.manifest:
        parser.error("必须提供 --manifest；工具不扫描或推测输入图")
    try:
        report = build(args.manifest, args.anchor)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"preview": str(OUTPUT / "index.html"), "loadable": report["loadable_frames"],
                      "technical_pass": report["technical_pass_frames"], "target": 196}, ensure_ascii=False))
    return 0 if report["technical_failure_frames"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())

