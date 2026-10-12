"""Character-local full-canvas export and honest incomplete-sequence preview."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import quote
from zoneinfo import ZoneInfo

from PIL import Image
from timing import RUN_TIMING

ROOT = Path(__file__).resolve().parents[1]
SPECS = {
    "run": {"directions": ["N", "NE", "E", "SE", "S", "SW", "W", "NW"], "count": 16, "durationMs": 60},
    "hit": {"directions": ["E", "W"], "count": 6, "durationMs": 40},
    "attack": {"directions": ["E", "W"], "count": 12, "durationMs": 30},
    "cast": {"directions": ["E", "W"], "count": 16, "durationMs": 45},
}
DEFAULT_TRANSFORM = {"canvasSize": [1024, 1024], "imageSize": [922, 922], "offset": [51, 40], "pivot": [512, 922]}


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def inside_root(path):
    path = path.resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError(f"输出越过角色目录: {path}")
    return path


def source_path(value):
    path = Path(value)
    return (ROOT / path).resolve() if not path.is_absolute() else path.resolve()


def relative(path):
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path, value):
    inside_root(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def dict_nodes(value):
    if isinstance(value, dict):
        yield value
        for item in value.values():
            yield from dict_nodes(item)
    elif isinstance(value, list):
        for item in value:
            yield from dict_nodes(item)


def check_record(record, source, source_sha, dimensions):
    """Match the exact digest; inspect native metadata without inventing model data."""
    nodes = [node for node in dict_nodes(record) if str(node.get("sha256", "")).lower() == source_sha]
    if not nodes:
        raise ValueError("generationRecord 中未找到与源 PNG 一致的 sha256")
    selected = nodes[0]
    for node in nodes:
        name = node.get("file") or node.get("path") or node.get("outputFile")
        if name and Path(str(name)).name.lower() == source.name.lower():
            selected = node
            break
    metadata = selected.get("native", selected.get("nativeImage", selected.get("metadata", selected)))
    verified = {"sha256": "matched", "width": "not_recorded", "height": "not_recorded", "format": "not_recorded"}
    for index, key in enumerate(("width", "height")):
        value = metadata.get(key) if isinstance(metadata, dict) else None
        if value is not None:
            if int(value) != dimensions[index]:
                raise ValueError(f"生成记录 {key}={value} 与 PNG {dimensions[index]} 不一致")
            verified[key] = "matched"
    fmt = metadata.get("format") if isinstance(metadata, dict) else None
    if fmt is not None:
        if str(fmt).lower() not in {"png", "image/png"}:
            raise ValueError(f"生成记录 format={fmt} 与 PNG 不一致")
        verified["format"] = "matched"
    return verified


def validate_transform(value):
    value = dict(value)
    if "size" in value:
        if "imageSize" in value and value["imageSize"] != value["size"]:
            raise ValueError("exportTransform.size 与 imageSize 不一致")
        value["imageSize"] = value.pop("size")
    transform = {**DEFAULT_TRANSFORM, **value}
    for key in DEFAULT_TRANSFORM:
        pair = transform[key]
        if not isinstance(pair, list) or len(pair) != 2 or any(type(x) is not int for x in pair):
            raise ValueError(f"exportTransform.{key} 必须是两个整数")
    if transform["canvasSize"] != [1024, 1024] or transform["pivot"] != [512, 922]:
        raise ValueError("本批固定 canvasSize=[1024,1024]、pivot=[512,922]")
    if transform["imageSize"][0] != transform["imageSize"][1]:
        raise ValueError("imageSize 必须是正方形，避免比例变形")
    for dim, off, canvas in zip(transform["imageSize"], transform["offset"], transform["canvasSize"]):
        if dim <= 0 or off < 0 or dim + off > canvas:
            raise ValueError("统一整幅画布变换必须完整位于1024画布内")
    return transform


def export_frame(entry, transform, dry_run):
    action, direction, number = entry["action"], entry["direction"], entry["frame"]
    source, record_path = source_path(entry["source"]), source_path(entry["generationRecord"])
    if source.suffix.lower() != ".png" or not source.is_file():
        raise ValueError(f"源 PNG 不存在: {source}")
    record = read_json(record_path)
    digest = sha256(source)
    expected = entry.get("sourceSha256", entry.get("sha256"))
    if expected and expected.lower() != digest:
        raise ValueError("selection 中的源 sha256 与实际 PNG 不一致")
    with Image.open(source) as image:
        if image.format != "PNG" or getattr(image, "n_frames", 1) != 1:
            raise ValueError("输入必须是单帧 PNG")
        if min(image.size) < 1024:
            raise ValueError(f"原生单帧至少1024，实际为{image.size}")
        if image.width != image.height:
            raise ValueError("源画布必须为正方形；不会自动裁切或拉伸")
        if "A" not in image.getbands():
            raise ValueError("源 PNG 缺少 alpha 通道；不会自动抠图")
        image.load()
        source_size, source_mode = list(image.size), image.mode
        record_check = check_record(record, source, digest, source_size)
        alpha_extrema = image.getchannel("A").getextrema()
        if alpha_extrema[0] == 255:
            raise ValueError("源 PNG 完全不透明；不会自动抠图")
        destination = inside_root(ROOT / "candidate" / action / direction / f"{number:02d}.png")
        operation = {
            "type": "full_canvas_resize_and_fixed_offset",
            "sourceCanvas": source_size,
            **transform,
            "resizeCount": 0 if source_size == transform["imageSize"] else 1,
            "resample": "LANCZOS",
            "usesBoundingBox": False,
            "alignsLowestPixel": False,
            "alphaKeying": False,
        }
        result = {**entry, "source": relative(source), "sourceSha256": digest,
                  "generationRecord": relative(record_path), "recordSha256": sha256(record_path),
                  "nativeSize": source_size, "nativeMode": source_mode,
                  "sourceAlphaExtrema": list(alpha_extrema), "recordValidation": record_check,
                  "candidate": relative(destination), "pivot": transform["pivot"],
                  "operation": operation, "exported": not dry_run,
                  "visualReview": entry.get("visualReview", "not_verified"),
                  "dynamicReview": "not_verified"}
        if not dry_run:
            destination.parent.mkdir(parents=True, exist_ok=True)
            rgba = image.convert("RGBA")
            if list(rgba.size) != transform["imageSize"]:
                rgba = rgba.resize(tuple(transform["imageSize"]), Image.Resampling.LANCZOS)
            canvas = Image.new("RGBA", tuple(transform["canvasSize"]), (0, 0, 0, 0))
            canvas.paste(rgba, tuple(transform["offset"]))
            canvas.save(destination, format="PNG")
            with Image.open(destination) as verify:
                verify.load()
                if verify.mode != "RGBA" or verify.size != (1024, 1024):
                    raise ValueError("导出 PNG 元数据验证失败")
            result["sha256"] = sha256(destination)
            sidecar = {
                "file": relative(destination), "sha256": result["sha256"],
                "width": 1024, "height": 1024, "format": "PNG", "mode": "RGBA",
                "exportedAt": datetime.now(ZoneInfo("America/New_York")).isoformat(),
                "derivedFrom": {"file": relative(source), "sha256": digest,
                                "generationRecord": relative(record_path), "generationRecordSha256": result["recordSha256"],
                                "nativeWidth": source_size[0], "nativeHeight": source_size[1]},
                "operation": operation, "pivot": transform["pivot"],
                "isNewAIGeneration": False, "modelAndQuality": "沿 derivedFrom 追溯，不继承当前默认配置",
                "status": entry.get("status", "candidate"), "visualReview": result["visualReview"],
                "dynamicReview": "not_verified", "clientIntegration": "not_integrated",
                "recordValidation": record_check,
            }
            sidecar_path = destination.with_name(destination.name + ".generation.json")
            write_json(sidecar_path, sidecar)
            result["derivedRecord"] = relative(sidecar_path)
    return result


PAGE = '''<!doctype html>
<html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>星阵少女 · 候选动作检查</title><style>
body{margin:0;background:#152132;color:#edf2f7;font:15px system-ui,sans-serif}main{max-width:1440px;margin:auto;padding:24px}h1{font-size:24px}p{line-height:1.65}a{color:#afd6ff}.notice{padding:14px;border:1px solid #b88533;background:#3d3224;border-radius:8px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:18px}article{padding:16px;background:#24334a;border-radius:12px}.stage{aspect-ratio:1;position:relative;background-color:#d2d5dc;background-image:linear-gradient(45deg,#e3e6ec 25%,transparent 25%),linear-gradient(-45deg,#e3e6ec 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#e3e6ec 75%),linear-gradient(-45deg,transparent 75%,#e3e6ec 75%);background-size:24px 24px;background-position:0 0,0 12px,12px -12px,-12px 0;border:1px solid #78899e}.stage img{width:100%;height:100%;object-fit:contain}.blank{position:absolute;inset:0;display:grid;place-content:center;color:#35465b;text-align:center;background:#e7ebf3}.ground{position:absolute;left:0;right:0;top:90.0390625%;border-top:1px dashed #487893;pointer-events:none}.pivot{position:absolute;left:50%;top:90.0390625%;transform:translate(-50%,-50%);color:#e22945;font-size:18px;pointer-events:none}.controls{display:flex;gap:6px;flex-wrap:wrap;margin:10px 0}button,select{border:1px solid #7890ac;border-radius:5px;background:#334866;color:inherit;padding:7px;cursor:pointer}input{width:100%}.meta{font-size:13px;line-height:1.6;min-height:65px;word-break:break-all}.slots{display:flex;gap:3px;margin:8px 0}.slot{height:8px;flex:1;background:#7e4650}.slot.available{background:#47b6a0}.slot.active{outline:2px solid white}details{margin:12px 0}pre{white-space:pre-wrap;word-break:break-all}small{color:#bfd0e4}h2{font-size:18px;margin:0 0 10px}</style>
<main><h1>20 星阵少女 · 候选动作检查</h1><p class="notice">__SUMMARY__。素材状态为候选；视觉及动态审核以人工记录为准。本预览不证明动作通过。缺帧按时间线显示空槽，不重复已有图片补齐。固定导出根点 (512, 922)，虚线为诊断参考，实际接地仍需人工核实；全序列使用同一画布变换。</p><p><a href="manifest.json">导出清单与逐帧来源</a> · 绿色短条表示可读取候选，红色表示缺失。跑步正常1×统一960ms/圈，16帧均匀60ms，无额外尾帧停留；客户端尚未接入。战斗动作保留原节奏，慢放为4倍时长。逐帧可暂停、前进、后退或拖动滑条。</p><div class="grid" id="groups"></div><details><summary>验证错误（__ERROR_COUNT__）</summary><pre id="errors"></pre></details></main>
<script>const data=__DATA__;
document.getElementById('errors').textContent=JSON.stringify(data.errors,null,2);
for(const group of data.groups){
 const article=document.createElement('article');article.innerHTML=`<h2>${group.action} / ${group.direction} · ${group.available}/${group.count}</h2><div class="stage"><img alt="角色候选帧"><div class="blank"></div><div class="ground"></div><span class="pivot">+</span></div><div class="slots"></div><div class="controls"><button data-key="toggle">播放</button><select><option value="1">正常 ${group.durationMs}ms/帧</option><option value="4">慢放 ${group.durationMs*4}ms/帧</option></select><button data-key="prev">上一帧</button><button data-key="next">下一帧</button></div><input type="range" min="0" max="${group.count-1}" value="0"><div class="meta"></div><small>本组 ${group.available===group.count?'槽位齐全；动态未验收':'帧组不完整；动态未验收'}</small>`;
 document.getElementById('groups').append(article);
 const img=article.querySelector('img'),blank=article.querySelector('.blank'),meta=article.querySelector('.meta'),slider=article.querySelector('input'),speed=article.querySelector('select'),toggle=article.querySelector('[data-key=toggle]');let frame=0,timer=null,playing=false;
 if(group.action==='run')speed.innerHTML='<option value="1">正常 960ms/圈 · 60ms/帧</option><option value="4">4倍慢放 · 3840ms/圈</option>';
 const slots=group.frames.map(f=>{const e=document.createElement('span');e.className='slot'+(f&&f.exported?' available':'');article.querySelector('.slots').append(e);return e});
 function draw(){const f=group.frames[frame];slider.value=frame;slots.forEach((e,i)=>e.classList.toggle('active',i===frame));if(f&&f.exported){img.src=f.previewUrl;img.hidden=false;blank.style.display='none';meta.textContent=`帧 ${frame+1} / ${group.count} · ${f.status||'candidate'} · visual: ${f.visualReview} · dynamic: not_verified\n来源：${f.source}`;}else{img.removeAttribute('src');img.hidden=true;blank.style.display='grid';blank.textContent=`${group.action} / ${group.direction}\n第 ${frame+1} 帧未提供`;meta.textContent=`帧 ${frame+1} / ${group.count} · 空槽`}}
 function schedule(){clearTimeout(timer);if(playing)timer=setTimeout(()=>{frame=(frame+1)%group.count;draw();schedule()},group.durationMs*Number(speed.value))}
 function pause(){playing=false;toggle.textContent='播放';clearTimeout(timer)}
 toggle.onclick=()=>{playing=!playing;toggle.textContent=playing?'暂停':'播放';schedule()};speed.onchange=schedule;
 article.querySelector('[data-key=prev]').onclick=()=>{pause();frame=(frame+group.count-1)%group.count;draw()};article.querySelector('[data-key=next]').onclick=()=>{pause();frame=(frame+1)%group.count;draw()};slider.oninput=()=>{pause();frame=Number(slider.value);draw()};draw();
}
</script></html>'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection", default="selection.json", help="根目录相对路径或绝对路径；只读")
    parser.add_argument("--preview-dir", default="preview", help="只能指向本角色目录内部")
    parser.add_argument("--dry-run", action="store_true", help="校验来源并写预览，不写候选 PNG")
    args = parser.parse_args()
    selection_path = source_path(args.selection)
    selection = read_json(selection_path)
    if selection.get("status") == "offline_delivery":
        import subprocess
        return subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "tools/build_delivery.py"), "--rebuild"]).returncode
    transform = validate_transform(selection.get("exportTransform", {}))
    preview_dir = inside_root(source_path(args.preview_dir))
    entries = selection.get("frames")
    if not isinstance(entries, list):
        raise ValueError("selection.frames 必须是数组")
    indexed, errors = {}, []
    for index, entry in enumerate(entries):
        try:
            action, direction, number = entry["action"], entry["direction"], entry["frame"]
            if action not in SPECS or direction not in SPECS[action]["directions"]:
                raise ValueError("动作或方向不符合规格")
            if type(number) is not int or not 1 <= number <= SPECS[action]["count"]:
                raise ValueError("frame 必须是规格范围内的1起始整数")
            key = (action, direction, number)
            if key in indexed:
                raise ValueError("同槽位重复选择；请先明确唯一来源")
            indexed[key] = None
            if entry.get("status") in {"rejected", "superseded", "missing"}:
                raise ValueError("selection 含拒稿、淘汰或缺失条目，不导出")
            indexed[key] = export_frame(entry, transform, args.dry_run)
        except (KeyError, ValueError, OSError, TypeError) as exc:
            errors.append({"selectionIndex": index, "slot": {k: entry.get(k) for k in ("action", "direction", "frame")}, "error": str(exc)})
    groups = []
    for action, spec in SPECS.items():
        for direction in spec["directions"]:
            frames = [indexed.get((action, direction, number)) for number in range(1, spec["count"] + 1)]
            for frame in frames:
                if frame and frame["exported"]:
                    import os
                    frame["previewUrl"] = quote(Path(os.path.relpath(ROOT / frame["candidate"], preview_dir)).as_posix())
            groups.append({"action": action, "direction": direction, "count": spec["count"], "durationMs": spec["durationMs"],
                           "available": sum(bool(f and f["exported"]) for f in frames), "frames": frames})
    count = sum(g["available"] for g in groups)
    manifest = {"character": ROOT.name, "generatedAt": datetime.now(ZoneInfo("America/New_York")).isoformat(),
                "selection": relative(selection_path), "selectionSha256": sha256(selection_path), "dryRun": args.dry_run,
                "exportTransform": transform, "expectedFrames": 196, "exportedFrames": count,
                "status": "candidate_complete_slots" if count == 196 else "candidate_incomplete",
                "dynamicReview": "not_verified", "clientIntegration": "not_integrated", "runTiming": RUN_TIMING, "groups": groups, "errors": errors}
    write_json(preview_dir / "manifest.json", manifest)
    encoded = json.dumps(manifest, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    page = PAGE.replace("__DATA__", encoded).replace("__SUMMARY__", f"本次导出 {count} / 196 帧，缺失 {196-count} 帧" + ("（dry-run）" if args.dry_run else "")).replace("__ERROR_COUNT__", str(len(errors)))
    (preview_dir / "index.html").write_text(page, encoding="utf-8")
    print(json.dumps({"exported": count, "expected": 196, "errors": errors, "preview": str(preview_dir / "index.html")}, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
