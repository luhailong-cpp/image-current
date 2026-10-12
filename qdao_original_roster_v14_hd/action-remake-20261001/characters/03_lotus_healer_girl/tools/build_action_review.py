"""Export explicit reviewed selections; never infer poses or fill missing slots."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import csv, hashlib, json, os
from PIL import Image, ImageDraw

BASE = Path(__file__).resolve().parent.parent
GROUPS = [("run", d, 16) for d in ("E", "NE", "N", "NW", "W", "SW", "S", "SE")] + [(a, d, n) for a, n in (("hit", 6), ("attack", 12), ("cast", 16)) for d in ("E", "W")]
STAMP = datetime.now(ZoneInfo("America/New_York")).isoformat()
RUN_FRAME_MS = 60
RUN_CYCLE_MS = 16 * RUN_FRAME_MS
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p): return os.path.relpath(p, BASE).replace("\\", "/")
def read(p): return json.loads(p.read_text(encoding="utf-8-sig"))
def write(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

groups, all_rows, errors = [], [], []
for action, direction, expected in GROUPS:
    key = f"{action}-{direction}"
    inp_path = BASE / f"review/{key}-sequence-input.json"
    if not inp_path.exists():
        groups.append(dict(action=action, direction=direction, expected=expected, present=0, status="no_selection_yet", frames=[dict(frame=n, file=None, durationMs=None) for n in range(1, expected+1)]))
        continue
    inp = read(inp_path)
    if action == "run":
        inp["timing"] = dict(frameMs=RUN_FRAME_MS, trialCycleMs=RUN_CYCLE_MS, offlineDefaultCycleMs=RUN_CYCLE_MS, mode="uniform", selectedProductionCycleMs=None)
        for source_frame in inp.get("frames", []):
            source_frame["durationMs"] = RUN_FRAME_MS
            if "startMs" in source_frame:
                source_frame["startMs"] = (int(source_frame.get("frame", source_frame.get("slot")))-1)*RUN_FRAME_MS
        for event in inp.get("contactEvents", []):
            number = event.get("frame", event.get("slot"))
            if number:
                event["atMs"] = (number-1)*RUN_FRAME_MS + event.get("cycleOffset",0)*RUN_CYCLE_MS
        if inp.get("contactEvents"):
            inp["events"] = [dict(event, frame=event.get("frame",event.get("slot")), type=event.get("type",event.get("event")), timeMs=(int(event.get("frame",event.get("slot")))-1)*RUN_FRAME_MS) for event in inp["contactEvents"]]
        for event in inp.get("events", []):
            number = event.get("frame", event.get("slot"))
            if number:
                event_type = event.get("type") or event.get("name") or event.get("event")
                if number == expected + 1 and event_type == "next_cycle_contact":
                    number = 1
                    event["cycleOffset"] = 1
                event["frame"] = number
                event["type"] = event_type
                event["timeMs"] = (number-1)*RUN_FRAME_MS + event.get("cycleOffset",0)*RUN_CYCLE_MS
                if "startMs" in event: event["startMs"] = event["timeMs"]
                if "atMs" in event: event["atMs"] = event["timeMs"]
                if "cycleBoundaryMs" in event: event["cycleBoundaryMs"] = RUN_CYCLE_MS
        if "durationMs" in inp: inp["durationMs"] = RUN_CYCLE_MS
        if "totalDurationMs" in inp: inp["totalDurationMs"] = RUN_CYCLE_MS
        if "timingBasis" in inp: inp["timingBasis"] = f"{RUN_CYCLE_MS}ms per cycle; 16 independent frames at uniform{RUN_FRAME_MS}ms; offline default, client unconfirmed"
        write(inp_path, inp)
    root = inp.get("root") or {"native": inp.get("nativeRoot"), "nativeCanvas": inp.get("canvas", inp.get("nativeCanvas")), "status": "provisional_not_client_approved", "alignmentApplied": False}
    if isinstance(root.get("nativeCanvas"), list):
        if len(set(root["nativeCanvas"])) != 1: raise ValueError(f"non-square canvas {key}")
        root["nativeCanvas"] = root["nativeCanvas"][0]
    if not root.get("native") or not root.get("nativeCanvas"): raise ValueError(f"explicit root/canvas required: {key}")
    rows, images, slots, hashes = [], {}, set(), set()
    for original in inp.get("frames", []):
        f = dict(original)
        slot = int(f.get("frame", f.get("slot", 0)))
        if slot not in range(1, expected+1) or slot in slots: raise ValueError(f"invalid/duplicate slot {key}/{slot}")
        slots.add(slot)
        src = (BASE / f["source"]).resolve()
        source_sha = sha(src)
        if source_sha in hashes: raise ValueError(f"duplicate pose source {key}/{slot}")
        hashes.add(source_sha)
        if f.get("sourceSha256") and f["sourceSha256"] != source_sha: raise ValueError(f"selection SHA mismatch {src}")
        rec_path = src.with_name(src.name + ".generation.json")
        rec = read(rec_path)
        if rec["sha256"] != source_sha: raise ValueError(f"generation SHA mismatch {src}")
        im = Image.open(src)
        if im.mode != "RGBA" or im.width != im.height or min(im.size) < 1024: raise ValueError(f"invalid native {src}")
        if im.width != root["nativeCanvas"]: raise ValueError(f"root canvas mismatch {src}")
        alpha = im.getchannel("A")
        bounds = alpha.point(lambda v: 255 if v > 8 else 0).getbbox()
        if not bounds: raise ValueError(f"empty source {src}")
        edges = {"left": alpha.crop((0,0,1,im.height)).getextrema()[1] > 8, "right": alpha.crop((im.width-1,0,im.width,im.height)).getextrema()[1] > 8, "top": alpha.crop((0,0,im.width,1)).getextrema()[1] > 8, "bottom": alpha.crop((0,im.height-1,im.width,im.height)).getextrema()[1] > 8}
        if any(edges.values()): errors.append(dict(group=key, frame=slot, kind="edge_alpha", edges=edges))
        ms = f.get("durationMs")
        if not isinstance(ms, (int, float)) or ms <= 0: raise ValueError(f"explicit positive frame duration required {key}/{slot}")
        out = BASE / f"candidate/{action}/{direction}/{slot:02d}.png"
        outrec = out.with_name(out.name + ".generation.json")
        operation = dict(type="full_canvas_uniform_downscale", **{"from": list(im.size), "to": [1024,1024]}, scale=1024/im.width, filter="Pillow LANCZOS", crop=None, translation=[0,0], perFrameFitting=False, alphaPreserved=True)
        prior = read(outrec) if outrec.exists() else {}
        reusable = out.exists() and prior.get("derivedFrom", {}).get("sha256") == source_sha and prior.get("sha256") == sha(out)
        if not reusable:
            out.parent.mkdir(parents=True, exist_ok=True)
            im.resize((1024,1024), Image.Resampling.LANCZOS).save(out)
            derivation = dict(schemaVersion=1, file=rel(out), sha256=sha(out), status="candidate_not_accepted", native=rec["native"], export=dict(width=1024,height=1024,format="PNG",mode="RGBA"), generatedAt=rec.get("generatedAt"), exportedAt=STAMP, actualModel=rec.get("actualModel"), actualQuality=rec.get("actualQuality"), unverifiedReason=rec.get("unverifiedReason"), derivedFrom=dict(file=rel(src),sha256=source_sha,generationRecord=rel(rec_path)), operation=operation, selection=dict(action=action,direction=direction,frame=slot,observedPhase=f.get("observedPhase")))
            write(outrec, derivation)
        f.update(frame=slot, slot=slot, source=rel(src), file=rel(out), sourceSha256=source_sha, sha256=sha(out), generationRecord=rel(outrec), sourceGenerationRecord=rel(rec_path), sourceDimensions=list(im.size), nativeBoundsAlphaGt8=list(bounds), exportTransform=operation)
        rows.append(f)
        images[slot] = im.copy()
        all_rows.append(dict(action=action,direction=direction,frame=slot,file=rel(out),source=rel(src),sourceSha256=source_sha,sha256=f["sha256"],sourceGenerationRecord=rel(rec_path),actualModel=rec.get("actualModel"),actualQuality=rec.get("actualQuality")))
    rows.sort(key=lambda f:f["frame"])
    selection = dict(inp, schemaVersion=1, action=action, direction=direction, root=root, frames=rows, exportRoot=[v*1024/root["nativeCanvas"] for v in root["native"]], exportCanvas=1024, status="candidate_not_accepted", visualAccepted=False, clientAccepted=False, exportedAt=STAMP)
    write(BASE / f"review/{key}-selection.json", selection)
    by_slot = {f["frame"]: f for f in rows}
    groups.append(dict(action=action,direction=direction,expected=expected,present=len(rows),status="candidate_not_accepted",selection=f"review/{key}-selection.json",root=root,exportRoot=selection["exportRoot"],exportCanvas=1024,cycleMs=sum(f["durationMs"] for f in rows),frames=[by_slot.get(n,dict(frame=n,file=None,durationMs=None)) for n in range(1,expected+1)]))
    # A contact sheet is a diagnostic rendering, never a new animation frame.
    cell, head, cols = 256, 30, 4
    sheet = Image.new("RGB", (cols*cell, ((expected+cols-1)//cols)*(cell+head)), (239,236,226))
    draw = ImageDraw.Draw(sheet)
    for n in range(1,expected+1):
        x, y = (n-1)%cols*cell, (n-1)//cols*(cell+head)
        draw.text((x+7,y+7), f"{direction}{n:02d} | {by_slot.get(n,{}).get('durationMs','?')}ms", fill=(25,61,53))
        if n in images:
            mini=images[n].resize((cell,cell),Image.Resampling.LANCZOS)
            sheet.paste(mini,(x,y+head),mini)
        gy=y+head+root["native"][1]/root["nativeCanvas"]*cell
        draw.line((x,gy,x+cell,gy),fill=(155,102,83))
    contact=BASE/f"preview/{key}-contact.jpg"
    contact.parent.mkdir(parents=True,exist_ok=True)
    sheet.save(contact,quality=92)
    write(contact.with_name(contact.name+".generation.json"),dict(file=rel(contact),sha256=sha(contact),operation="diagnostic montage, uniform full canvases; fixed provisional root overlay; not game art",derivedFrom=[dict(file=f["source"],sha256=f["sourceSha256"],generationRecord=f["sourceGenerationRecord"]) for f in rows]))

overview=dict(schemaVersion=1,character="03_lotus_healer_girl",updatedAt=STAMP,target=196,selectedExported=len(all_rows),visualAccepted=False,clientAccepted=False,groups=groups,note="Explicit source selections only. Missing slots remain empty. Playback duration does not prove grounding or visual acceptance.")
write(BASE/"review/all-actions-selection.json",overview)
duplicate_sources={h:[f"{f['action']}/{f['direction']}/{f['frame']:02d}" for f in all_rows if f['sourceSha256']==h] for h in {f['sourceSha256'] for f in all_rows} if sum(f['sourceSha256']==h for f in all_rows)>1}
verification=dict(checkedAt=STAMP,target=196,selectedExported=len(all_rows),allSlotsPresent=len(all_rows)==196,uniqueSourceShaCount=len({f['sourceSha256'] for f in all_rows}),duplicateSources=duplicate_sources,errors=errors,sourceHashesVerified=True,fullCanvasExportOnly=True,visualAccepted=False,clientAccepted=False,technicalStatus="passed_for_present_selections" if not errors and not duplicate_sources else "issues")
write(BASE/"review/all-actions-technical-verification.json",verification)
with (BASE/"review/selected-source-index.csv").open("w",encoding="utf-8-sig",newline="") as handle:
    fields=["action","direction","frame","file","source","sourceSha256","sha256","sourceGenerationRecord","actualModel","actualQuality"]
    writer=csv.DictWriter(handle,fieldnames=fields);writer.writeheader();writer.writerows(all_rows)
manifest=read(BASE/"manifest.json") if (BASE/"manifest.json").exists() else {}
manifest.update(schemaVersion=2,character="03_lotus_healer_girl",status="in_progress_not_all_actions_complete",updatedAt=STAMP,allActionsSelection="review/all-actions-selection.json",technicalVerification="review/all-actions-technical-verification.json",client="not_integrated_not_tested")
manifest["animationTiming"] = "animation-timing.json"
manifest["runDefault"] = dict(frameMs=RUN_FRAME_MS, cycleMs=RUN_CYCLE_MS, frames=16, mode="uniform", offlineApplied=True, clientVerified=False)
manifest.setdefault("counts",{}).update(finalTotalTarget=196,selectedCandidateExported=len(all_rows),visualAccepted=0,clientAccepted=0)
for g in groups:
    if not g.get("selection"): continue
    manifest.setdefault(g["action"],{})[g["direction"]]=dict(selection=g["selection"],status=g["status"],root=g["root"],exportRoot=g["exportRoot"],exportCanvas=1024,productionCycleMs=None,trialCycleMs=g["cycleMs"],frameDurationsMs=[f["durationMs"] for f in g["frames"]])
write(BASE/"manifest.json",manifest)
print(json.dumps(verification,ensure_ascii=False))
