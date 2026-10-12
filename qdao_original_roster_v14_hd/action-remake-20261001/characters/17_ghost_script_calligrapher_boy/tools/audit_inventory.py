"""Read-only PNG and provenance audit. Only writes inventory-audit.json, STATUS.md and MERGE_HANDOFF.md."""
from __future__ import annotations
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
import hashlib, json, re
from PIL import Image

BASE = Path(__file__).resolve().parents[1]
OLD = BASE.parents[2] / "combat-20260929" / "characters" / BASE.name
RUN_TIMING = json.loads((BASE / "animation-timing.json").read_text(encoding="utf-8"))["run"]
ACTIONS = {
    "run": {"directions":["N","NE","E","SE","S","SW","W","NW"],"frames":16,"duration_ms":RUN_TIMING["frameMs"]},
    "hit": {"directions":["E","W"],"frames":6,"duration_ms":40},
    "attack":{"directions":["E","W"],"frames":12,"duration_ms":30},
    "cast":{"directions":["E","W"],"frames":16,"duration_ms":45},
}
PRIOR = ["hit-E-03-v3","hit-W-03-v2","attack-E-06-v2","attack-W-06-v1","cast-E-10-v2","cast-W-10-v2"]
RX = re.compile(r"^(run|hit|attack|cast)-(N|NE|E|SE|S|SW|W|NW)-(\d{2})-v(\d+)\.png$")
TZ = timezone(timedelta(hours=-4))

def read_json(path):
    try: return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError): return None

def rel(path):
    try: return path.relative_to(BASE).as_posix()
    except ValueError: return path.as_posix()

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def resolve_record_path(raw, origin):
    if not raw: return None
    p=Path(raw)
    return p if p.is_absolute() else (BASE if origin=="current" else OLD.parents[1])/p

def inspect(path, origin, reviews):
    action,direction,frame,version=RX.fullmatch(path.name).groups()
    record_path=path.with_suffix(".png.generation.json") if origin=="current" else OLD/"provenance"/"receipts"/(path.stem+".json")
    record=read_json(record_path) or {}
    issues=[]
    digest=sha(path)
    with Image.open(path) as im:
        im.load()
        size=list(im.size); mode=im.mode
        alpha_range=list(im.getchannel("A").getextrema()) if "A" in im.getbands() else None
        alpha_bbox=list(im.getchannel("A").point(lambda x:255 if x>8 else 0).getbbox() or []) if "A" in im.getbands() else None
    if not record_path.is_file(): issues.append("missing_generation_record")
    elif not record: issues.append("unreadable_generation_record")
    if record and record.get("sha256")!=digest: issues.append("generation_record_sha_mismatch")
    if record and (record.get("width"),record.get("height"))!=tuple(size): issues.append("generation_record_size_mismatch")
    if min(size)<1024: issues.append("native_dimension_below_1024")
    if size[0]!=size[1]: issues.append("non_square_native_canvas_requires_review_no_stretch")
    if mode!="RGBA": issues.append("not_rgba")
    if alpha_range and alpha_range[0]!=0: issues.append("no_fully_transparent_pixels")
    prompt=resolve_record_path(record.get("prompt"),origin)
    if prompt is None or not prompt.is_file(): issues.append("missing_prompt_file")
    request=resolve_record_path(record.get("evidence",{}).get("request"),origin)
    if request is None: request=(BASE/"provenance" if origin=="current" else OLD/"provenance"/"receipts")/(path.stem+".request.json")
    req=read_json(request) or {}
    request_args=req.get("submittedParameters",req)
    if not request.is_file(): issues.append("missing_request_file")
    elif prompt and prompt.is_file() and (request_args.get("prompt") or "").rstrip("\r\n")!=prompt.read_text(encoding="utf-8-sig").rstrip("\r\n"): issues.append("saved_prompt_differs_from_request")
    for field in ("configSnapshot","submittedParameters","generatedAt","generatedAtEvidence","evidence"):
        if not record.get(field): issues.append("missing_record_field:"+field)
    for field in ("actualModel","actualQuality"):
        if field not in record: issues.append("missing_record_field:"+field)
    source_path=record.get("evidence",{}).get("toolReturnedPath")
    if not source_path: issues.append("missing_tool_returned_path")
    tool_result=(BASE/"provenance" if origin=="current" else OLD/"provenance"/"receipts")/(path.stem+".tool-result.json")
    review=reviews.get(path.name,{})
    status=review.get("status") or record.get("review",{}).get("status","pending")
    notes=review.get("visualNotes") or review.get("review") or review.get("notes") or review.get("issues") or record.get("review",{}).get("notes")
    return {
        "key":path.stem,"slot":f"{action}-{direction}-{frame}","action":action,"direction":direction,"frame":int(frame),"version":int(version),
        "origin":origin,"file":rel(path),"sha256":digest,"bytes":path.stat().st_size,"native_size":size,"mode":mode,"alpha_range":alpha_range,"alpha_bbox_gt8":alpha_bbox,
        "record":rel(record_path),"prompt":rel(prompt) if prompt else None,"request":rel(request),"tool_result_file":rel(tool_result) if tool_result.is_file() else None,
        "tool_result_metadata_in_record":bool(record.get("evidence",{}).get("returnedFields") and source_path),
        "target_model":record.get("configSnapshot",{}).get("model"),"target_quality":record.get("configSnapshot",{}).get("quality"),
        "actual_model":record.get("actualModel"),"actual_quality":record.get("actualQuality"),
        "generation_time_evidence":record.get("generatedAtEvidence"),"recorded_generation_time":record.get("generatedAt"),
        "review_status":status,"review_notes":notes,"audit_issues":issues}

def collect_reviews():
    by_name={}; explicit={}
    for path in sorted(list(BASE.glob("review-*.json"))+list((BASE/"review").glob("review-*.json")),key=lambda p:p.stat().st_mtime):
        data=read_json(path) or {}
        for key in ("selectedForSequenceReview","retainedPriorReferences","reviewed","attempts","frames"):
            for item in data.get(key,[]):
                raw=item.get("file") or item.get("currentFile") or item.get("selectedFile")
                if not raw and item.get("key"): raw=item["key"]+".png"
                if not raw: continue
                by_name[Path(raw).name]=item
                slot=item.get("slot")
                if not isinstance(slot,str) or not slot.startswith(("run","hit","attack","cast")):
                    slot=RX.match(Path(raw).name).group(0).rsplit("-v",1)[0] if RX.match(Path(raw).name) else None
                if key in ("selectedForSequenceReview","frames") and slot:
                    explicit[slot.replace("/","-")]=Path(raw).name
        for item in data.get("supersededAttempts",[]):
            if item.get("file"): by_name[Path(item["file"]).name]={"status":"superseded","notes":item.get("reason")}
    return by_name,explicit

def main():
    reviews,explicit=collect_reviews()
    current_paths=sorted((BASE/"staging").glob("*.png"))
    current=[inspect(p,"current",reviews) for p in current_paths if RX.fullmatch(p.name)]
    prior=[inspect(OLD/"staging"/(key+".png"),"prior",reviews) for key in PRIOR if (OLD/"staging"/(key+".png")).is_file()]
    by_slot=defaultdict(list)
    for item in prior+current: by_slot[item["slot"]].append(item)
    slots=[]
    for action,spec in ACTIONS.items():
        for direction in spec["directions"]:
            for frame in range(1,spec["frames"]+1):
                key=f"{action}-{direction}-{frame:02}"; candidates=by_slot.get(key,[])
                preferred=next((x for x in candidates if Path(x["file"]).name==explicit.get(key)),None)
                eligible=[x for x in candidates if "superseded" not in x["review_status"] and x["review_status"] not in ("rejected","failed")]
                selected=preferred or max(eligible or candidates,key=lambda x:(x["origin"]=="current",x["version"]),default=None)
                slots.append({"slot":key,"action":action,"direction":direction,"frame":frame,"duration_ms":spec["duration_ms"],
                    "event":"hit_contact" if action=="attack" and frame==6 else "cast_release" if action=="cast" and frame==10 else None,
                    "candidate_keys":[x["key"] for x in candidates],"selected_candidate":selected["key"] if selected else None,
                    "selected_file":selected["file"] if selected else None,"selected_sha256":selected["sha256"] if selected else None,
                    "selection_is_visual_approval":False,"status":"missing" if not selected else "passed" if selected["review_status"]=="passed" else "pending",
                    "sequence_review":"not_accepted","root_anchor_status":"not_accepted"})
    groups=[]
    for action,spec in ACTIONS.items():
        for direction in spec["directions"]:
            seq=[s for s in slots if s["action"]==action and s["direction"]==direction]
            groups.append({"action":action,"direction":direction,"expected":len(seq),"available":sum(s["selected_candidate"] is not None for s in seq),
                "missing_frames":[s["frame"] for s in seq if s["status"]=="missing"],"visual_passed":sum(s["status"]=="passed" for s in seq)})
    files=current+prior; dup=defaultdict(list)
    for item in files: dup[item["sha256"]].append(item["key"])
    defects=[{"key":x["key"],"origin":x["origin"],"issues":x["audit_issues"]} for x in files if x["audit_issues"]]
    selected_keys={s["selected_candidate"] for s in slots if s["selected_candidate"]}
    selected_defects=[x for x in defects if x["key"] in selected_keys]
    failures=[{"file":rel(p),"record":read_json(p)} for p in sorted((BASE/"provenance").glob("*.failure.json"))]
    requests=sorted((BASE/"provenance").glob("*.request.json")); png_keys={x["key"] for x in current}
    requests_without_image=[rel(p) for p in requests if p.name.removesuffix(".request.json").split(".retry-")[0] not in png_keys]
    previews=read_json(BASE/"preview"/"manifest-preview.json") or {}; preview_keys={x.get("key") for x in previews.get("current_inventory",[])}
    runtime=sorted((BASE/"runtime").rglob("*.png")) if (BASE/"runtime").exists() else []
    now=datetime.now(TZ).isoformat()
    counts={"expected_slots":len(slots),"covered_slots":sum(s["selected_candidate"] is not None for s in slots),"missing_slots":sum(s["status"]=="missing" for s in slots),
        "visually_passed_slots":sum(s["status"]=="passed" for s in slots),"current_png_attempts":len(current),"current_unique_slots":len({x["slot"] for x in current}),
        "prior_keyframe_references":len(prior),"sequence_accepted_groups":0,"runtime_png_files":len(runtime),"record_or_format_issue_files":len(defects),"selected_record_or_format_issue_files":len(selected_defects),"failure_records":len(failures)}
    data={"schema_version":1,"character":BASE.name,"audited_at":now,"timezone":"America/New_York",
        "method":"Inspect actual PNGs, SHA-256, alpha, dimensions, generation records and requests; no pixel editing, no visual approval inferred.",
        "counts":counts,"actions":ACTIONS,"groups":groups,"slots":slots,"current_images":current,"prior_keyframes":prior,
        "run_timing":{"normal_cycle_ms":RUN_TIMING["cycleMs"],"frame_ms":RUN_TIMING["frameMs"],"uniform":True,"client_tested":False,"preview":"preview/timing-grounding.html"},
        "missing_prior_files":[key for key in PRIOR if not (OLD/"staging"/(key+".png")).is_file()],
        "duplicate_sha_groups":[{"sha256":digest,"keys":keys} for digest,keys in dup.items() if len(keys)>1],
        "audit_issues":defects,"selected_audit_issues":selected_defects,"unknown_staging_names":[rel(p) for p in current_paths if not RX.fullmatch(p.name)],
        "requests_without_image":requests_without_image,"failures":failures,
        "preview":{"exists":(BASE/"preview"/"index.html").is_file(),"built_at":previews.get("built_at"),"stored_counts":previews.get("counts"),
            "current_images_absent_from_preview":sorted(png_keys-preview_keys),"preview_images_no_longer_in_staging":sorted(preview_keys-png_keys)},
        "runtime_files":[{"file":rel(p),"sha256":sha(p)} for p in runtime],
        "acceptance":{"hands_and_feet_run":"not_accepted","transparent_edges":"not_accepted","camera_scale_root":"not_accepted",
            "normal_slow_frame_step_sequence":"not_accepted","client_integration":"not_integrated","client_runtime":"not_tested"},
        "anchor":{"canvas_reference":[1254,1254],"root_x_target":640,"virtual_ground_y_target":1155,"formal_canvas":[1024,1024],
            "status":"prompt target only; not verified across frames; no per-frame lowest-foot alignment or bbox scaling"},
        "notes":["候选选择用于检查，不表示可合并到游戏。","实际模型和质量按原逐图记录保留；null表示未确认。",
            "旧6关键帧保持原路径和SHA，不重复计成本批新图。","请求文件不等于生成成功；未有PNG的槽位保持缺失。"]}
    dest=BASE/"provenance"/"inventory-audit.json"; dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    table="\n".join(f"| {g['action']} | {g['direction']} | {g['available']}/{g['expected']} | {g['visual_passed']} | {', '.join(f'{n:02}' for n in g['missing_frames']) or '无；仍待验收'} |" for g in groups)
    format_bad=[x for x in files if any(i.startswith(("native_dimension","non_square","not_rgba")) for i in x["audit_issues"])]
    bad_text="\n".join(f"- {x['key']}: {' × '.join(map(str,x['native_size']))} {x['mode']}；{'当前选图异常' if x['key'] in selected_keys else '历史尝试，已不在当前明确选图中'}。" for x in format_bad) or "- 无尺寸/通道格式异常；仍需美术与动态审核。"
    common=f"""更新时间：{now}（America/New_York）。此为真实文件盘点快照；再次运行 tools/audit_inventory.py 刷新。

当前 **{counts['covered_slots']}/196 槽位有候选图，缺 {counts['missing_slots']} 槽位**。本批实际 PNG 尝试 {counts['current_png_attempts']} 张，覆盖 {counts['current_unique_slots']} 个槽位；另保留 6 张旧关键帧原来源引用。不同版本不重复计槽位。
**视觉通过 {counts['visually_passed_slots']} 槽位，动态验收通过 0 组；本角色 runtime 目录内 PNG {counts['runtime_png_files']} 张。未接入客户端，未运行客户端验收。跑步手脚修复尚未通过，不能宣称已完成。**

| 动作 | 方向 | 有候选/目标 | 视觉通过 | 缺帧 |
| --- | --- | ---: | ---: | --- |
{table}

全部尝试中的尺寸异常（原生稿不会强行拉伸为方形；当前选图记录/格式异常 {len(selected_defects)} 张）：
{bad_text}
"""
    status="# 17 灵篆书生 · 当前制作状态\n\n"+common+f"""
验收剩余事项：

- 跑步逐段核对左右腿交替、膝踝连续、反向摆臂、笔卷握持、蹬地/腾空与首尾衔接。已有手脚修改只代表候选生成，不等于全组通过。
- 跑步脚掌外撇须按鞋长轴、膝、踝是否沿各自移动方向判断，不能只缩窄腿距。用户已指定09竹弓少女当前版作同方向动作参照；实际看图后保留本角色身份与持物，不复制她的像素或机械照抄帧号。
- 按用户最新要求，八方向跑步统一1200ms/圈、16帧各75ms；当前预览已移除偏快旧档，只保留正常、0.25慢放、暂停和逐帧。见[接地与逐帧检查](preview/timing-grounding.html)。未修改客户端。
- 所有动作核对头身比例、方向、相机、虚拟地面与根点；不能按逐帧包围盒缩放或最低脚贴地。
- 已有审查记录指出部分帧有红/青/白边、流苏挂点和多余饰物问题，仍需处理并重新审核。
- 补齐缺槽后做正常、慢速和逐帧检查；核实通过后再导出 1024×1024 RGBA 与交付。
- 每图来源、请求、SHA 与异常详见 [inventory-audit.json](provenance/inventory-audit.json)。目前记录或格式异常涉及 {counts['record_or_format_issue_files']} 张（包含非方形画布）；不以文件存在替代美术通过。
- 预览 [index.html](preview/index.html) 的快照时间为 {previews.get('built_at','未知')}；有 {len(png_keys-preview_keys)} 张本批 PNG 尚不在该快照中。运行既有 tools/build_preview.py 刷新后，再运行盘点脚本。
- 保留当前唯一在制稿、源记录和预览引用；成品确认落盘且引用完整后才能删除已淘汰图片。旧目录只读。

本状态由 tools/audit_inventory.py 自动生成；具体美术结论以 review-*.json 与后续逐帧验收记录为准。
"""
    (BASE/"STATUS.md").write_text(status,encoding="utf-8")
    old_rows="\n".join(f"| {x['key']} | {x['file']} | {x['sha256']} |" for x in prior)
    handoff="# 17 灵篆书生 · 合并交接（在制，未验收）\n\n"+common+f"""
本机本角色唯一写入目录：{BASE.as_posix()}。本角色仍在制作，不能用候选覆盖游戏正式素材。当前未操作客户端或 Git 暂存/提交/推送；其他电脑未提交内容不在本盘点范围。

每张实际图片的文件路径、SHA-256、原生尺寸、记录/请求路径与目标/实际型号在 [inventory-audit.json](provenance/inventory-audit.json) 的 current_images/prior_keyframes 中；196 个槽位与候选映射在 slots 中。逐图生成模型/质量实际值未披露时保持 null（未确认），不能把配置目标 GPT Image 2.5 Sunburst / max 当作显式参数或实测结果。

帧时长与标记：

| 动作 | 每帧 | 全段 | 标记 |
| --- | ---: | ---: | --- |
| run | 75 ms（均匀） | 1200 ms | 用户最新指定；完整16帧，首尾无额外停顿；客户端未接入 |
| hit | 40 ms | 240 ms | 无正式事件标记 |
| attack | 30 ms | 360 ms | 第06帧接触候选 |
| cast | 45 ms | 720 ms | 第10帧释放候选 |

锚点：新稿提示中的参考画布 1254×1254、根点 x=640、虚拟地面 y=1155 **只是目标，并未逐帧视觉确认**。最终画布 1024×1024 RGBA。完整画布统一映射规则须经审核确定；不得逐帧最低脚贴地或按包围盒独立缩放，也不得将非方形原生稿拉伸成方形。运行跳跃应保留真实起伏。

旧6关键帧只读引用（不计本批新图）：

| 关键帧 | 原文件 | SHA-256 |
| --- | --- | --- |
{old_rows}

未解决事项：缺帧、跑步左右腿/摆臂/关节/持物连续性、透明边缘杂色、部分流苏/饰物错误、全局比例与根点、全部动作正常/慢速/逐帧验收。查看 [STATUS.md](STATUS.md) 和已有 review 文件获取详细情况。未找到审核记录的候选保持待验收。

[本地预览](preview/index.html) 支持正常、0.25慢速、逐帧、深浅棋盘底；页面使用静态清单，需在新图登记后运行 tools/build_preview.py。预览代码可播放不等于动画美术已通过。

刷新：使用含 Pillow 的 Python 运行 tools/audit_inventory.py。它只读取图片/原记录并重写本交接、STATUS.md 与 provenance/inventory-audit.json，不修改图像，不导出、不删除、不访问 Git。
"""
    (BASE/"MERGE_HANDOFF.md").write_text(handoff,encoding="utf-8")
    print(json.dumps({"counts":counts,"groups":groups,"issues":defects,"preview_missing":len(png_keys-preview_keys)},ensure_ascii=False))
if __name__=="__main__": main()

