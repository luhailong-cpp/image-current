"""Character-local PNG cleanup. Default: validated dry-run plan; never rebuild assets."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
from datetime import datetime, timezone
from PIL import Image

BASE = Path(__file__).absolute().parent.parent
EXPECTED_BASE = Path("D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/03_lotus_healer_girl")
GROUPS = [("run", d, 16) for d in ("E","NE","N","NW","W","SW","S","SE")] + [
    (a,d,n) for a,n in (("hit",6),("attack",12),("cast",16)) for d in ("E","W")]
VERSION = 1
REPARSE_POINT = 0x400


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def stamp():
    return datetime.now(timezone.utc).isoformat()


def canonical(data):
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",",":")).encode("utf-8")


def fingerprint(data):
    return hashlib.sha256(canonical(data)).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def absolute(path):
    return Path(os.path.abspath(path))


def inside(path, root):
    return absolute(path).is_relative_to(absolute(root))


def no_links(path):
    """Reject symlinks AND Windows junction/reparse points in every existing ancestor."""
    path = absolute(path)
    for item in (path, *path.parents):
        if not os.path.lexists(item):
            continue
        info = item.lstat()
        require(not stat.S_ISLNK(info.st_mode), f"Symlink refused: {item}")
        require(not (getattr(info, "st_file_attributes", 0) & REPARSE_POINT),
                f"Reparse point refused: {item}")
    return path


def regular(path):
    path = no_links(path)
    require(path.is_file(), f"Missing/non-file: {path}")
    require(stat.S_ISREG(path.stat().st_mode), f"Not regular: {path}")
    return path


def asset(value):
    p = Path(value)
    return regular(p if p.is_absolute() else BASE / p)


def deletion_path(path, root=None):
    root = absolute(root or BASE / "generation")
    p = absolute(path)
    require(inside(p, root) and p != root, f"Outside generation boundary: {p}")
    require(p.suffix.lower() == ".png", f"Only PNG is deletable: {p}")
    require(not any(":" in part for part in p.relative_to(root).parts),
            f"Alternate stream refused: {p}")
    regular(p)
    require(p.stat().st_nlink == 1, f"Hardlinked PNG refused: {p}")
    return p


def walk_files(root):
    """No following directory links. Fail closed if one is encountered."""
    root = no_links(root)
    require(root.is_dir(), f"Missing directory: {root}")
    for folder, dirs, files in os.walk(root, followlinks=False):
        no_links(folder)
        for name in dirs:
            no_links(Path(folder) / name)
        for name in files:
            yield regular(Path(folder) / name)


def entry(path):
    path = regular(path)
    return {"path": path.as_posix(), "sha256": sha(path)}


def image_info(path, export=False):
    with Image.open(path) as image:
        image.load()
        require(image.format == "PNG" and image.mode == "RGBA", f"Not RGBA PNG: {path}")
        require(image.width == image.height and image.width >= 1024, f"Invalid size: {path}")
        if export:
            require(image.size == (1024,1024), f"Export not 1024 square: {path}")
        alpha = image.getchannel("A").getextrema()
        require(alpha[0] == 0 and alpha[1] > 0, f"Missing transparency/content: {path}")
        return {"size": list(image.size), "mode": image.mode,
                "alphaExtrema": list(alpha),
                "rgbaPixelSha256": hashlib.sha256(image.tobytes()).hexdigest()}


def slots(data, expected):
    frames = data.get("frames", [])
    index = {int(f.get("frame", f.get("slot", 0))): f for f in frames}
    require(len(frames) == expected and sorted(index) == list(range(1,expected+1)),
            f"Expected exactly unique slots 1..{expected}")
    return index


def pair_check(source, exported, source_sha, export_sha):
    require(sha(source) == source_sha, f"Source changed: {source}")
    require(sha(exported) == export_sha, f"Export changed: {exported}")
    native_info = image_info(source)
    export_info = image_info(exported, export=True)
    with Image.open(source) as native, Image.open(exported) as final:
        expected_pixels = native.resize((1024,1024), Image.Resampling.LANCZOS).tobytes()
        require(expected_pixels == final.tobytes(), f"Export pixels do not match full-canvas source: {exported}")
    return native_info, export_info


def verify_selections():
    """Read and verify all 14 current inputs, exported selections, aggregate and pixels."""
    overview_path = asset("review/all-actions-selection.json")
    overview = read(overview_path)
    require(overview.get("selectedExported") == 196 and overview.get("target") == 196,
            "Aggregate is not complete 196/196")
    groups = overview.get("groups", [])
    index = {(g["action"],g["direction"]):g for g in groups}
    require(len(groups) == 14 and set(index) == {(a,d) for a,d,_ in GROUPS},
            "Aggregate must contain exactly the expected14 groups")
    rows, controls, record_snapshots = [], {str(overview_path):entry(overview_path)}, []
    for action, direction, count in GROUPS:
        key = f"{action}-{direction}"
        inp_path = asset(f"review/{key}-sequence-input.json")
        selection_path = asset(f"review/{key}-selection.json")
        controls[str(inp_path)] = entry(inp_path)
        controls[str(selection_path)] = entry(selection_path)
        inputs = slots(read(inp_path), count)
        selected = slots(read(selection_path), count)
        aggregate = slots(index[(action,direction)], count)
        for number in range(1,count+1):
            f, selected_frame, agg = inputs[number], selected[number], aggregate[number]
            source = asset(f["source"])
            source_record = regular(Path(str(source)+".generation.json"))
            exported = asset(f"candidate/{action}/{direction}/{number:02d}.png")
            export_record = regular(Path(str(exported)+".generation.json"))
            require(inside(exported, BASE/"candidate"), "Export outside this character")
            source_hash, export_hash = sha(source), sha(exported)
            src_meta, out_meta = read(source_record), read(export_record)
            require(src_meta.get("sha256") == source_hash, f"Source metadata mismatch: {source}")
            require("actualModel" in src_meta and "actualQuality" in src_meta,
                    f"Missing model/quality evidence fields: {source_record}")
            if f.get("sourceSha256"):
                require(f["sourceSha256"] == source_hash, f"Input hash mismatch: {key}/{number}")
            for current in (selected_frame, agg):
                require(asset(current["source"]) == source and current.get("sourceSha256") == source_hash,
                        f"Stale selected source: {key}/{number}")
                require(asset(current["file"]) == exported and current.get("sha256") == export_hash,
                        f"Stale selected export: {key}/{number}")
                require(current.get("durationMs") == f.get("durationMs"), f"Stale timing: {key}/{number}")
            require(out_meta.get("sha256") == export_hash, f"Export metadata SHA mismatch: {exported}")
            require("actualModel" in out_meta and "actualQuality" in out_meta and
                    out_meta["actualModel"] == src_meta["actualModel"] and
                    out_meta["actualQuality"] == src_meta["actualQuality"],
                    f"Export model/quality evidence does not match source: {exported}")
            derived = out_meta.get("derivedFrom", {})
            require(asset(derived["file"]) == source and derived.get("sha256") == source_hash,
                    f"Export origin mismatch: {exported}")
            require(asset(derived["generationRecord"]) == source_record, "Origin record mismatch")
            op = out_meta.get("operation", {})
            require(op.get("type") == "full_canvas_uniform_downscale" and
                    op.get("to") == [1024,1024] and op.get("translation") == [0,0] and
                    op.get("crop") is None and op.get("perFrameFitting") is False and
                    op.get("alphaPreserved") is True, f"Unsupported export operation: {exported}")
            if action == "run":
                require(f.get("durationMs") == 60, f"Run timing must remain60ms: {key}/{number}")
            native_info, export_info = pair_check(source, exported, source_hash, export_hash)
            require(op.get("from") == native_info["size"], "Native operation size mismatch")
            declared_native = src_meta.get("native", {})
            require([declared_native.get("width"), declared_native.get("height")] == native_info["size"]
                    and declared_native.get("mode") == "RGBA", "Native metadata dimensions/mode mismatch")
            rows.append({"group":key, "slot":number, "source":source.as_posix(),
                         "sourceSha256":source_hash, "export":exported.as_posix(),
                         "exportSha256":export_hash, "sourceRecord":source_record.as_posix(),
                         "sourceRecordSha256":sha(source_record), "exportRecord":export_record.as_posix(),
                         "exportRecordSha256":sha(export_record), "exportInfo":export_info})
            record_snapshots.append({"source":source.as_posix(), "record":src_meta})
    require(len(rows) == 196 and len({f["sourceSha256"] for f in rows}) == 196,
            "Exactly196 distinct native-source SHA256 required")
    require(len({f["exportSha256"] for f in rows}) == 196,
            "Exactly196 distinct export SHA256 required")
    return rows, list(controls.values()), record_snapshots


def reference_closure(selected, inventory):
    """Historical references become explicit; local available parents kept in first-stage mode."""
    queue, seen, references = list(selected), set(), []
    while queue:
        p = queue.pop()
        if p in seen:
            continue
        seen.add(p)
        rec = Path(p + ".generation.json")
        if not rec.is_file():
            continue
        for ref in read(regular(rec)).get("references", []):
            raw = ref.get("path")
            if not raw:
                continue
            # Relative old records are interpreted relative to their character directory,
            # never to the running shell or generator host directory.
            owner = next((ancestor for ancestor in Path(p).parents
                          if ancestor.name == "03_lotus_healer_girl"), BASE)
            q = absolute(Path(raw) if Path(raw).is_absolute() else owner / raw)
            local = q.as_posix() in inventory
            exists = q.is_file()
            references.append({"owner":p, "path":q.as_posix(), "recordedSha256":ref.get("sha256"),
                               "exists":exists, "scope":"local_generation" if local else "read_only_external"})
            if local:
                actual = inventory[q.as_posix()]["sha256"]
                require(not ref.get("sha256") or ref["sha256"] == actual,
                        f"Reference hash changed: {q}")
                queue.append(q.as_posix())
    return seen, references


def retired(meta, png):
    status = str(meta.get("status", "")).lower()
    review = png.with_suffix(".review.json")
    if review.is_file():
        status += " " + str(read(regular(review)).get("status", "")).lower()
    return any(word in status for word in ("reject", "not_selected", "superseded", "discard", "replaced"))


def protected_files(controls, selected):
    """Minimum runnable exports plus unchanged text evidence; never native PNG backups."""
    paths = {row["path"] for row in controls}
    for row in selected:
        paths.update((row["export"],row["exportRecord"],row["sourceRecord"]))
    for name in ("manifest.json","animation-timing.json","validation.json","README.md","MERGE_HANDOFF.md",
                 "review/root-and-timing.json","review/action-events.json","review/source-index.csv",
                 "review/selected-source-index.csv","review/all-actions-technical-verification.json",
                 "review/delivery-integrity.json","review/slot-inventory.json","review/production-status.json",
                 "preview/actions.html","preview/actions.js","preview/timing.js"):
        paths.add(asset(name).as_posix())
    # Preserve every locally recorded prompt/job/receipt/review/version as hashed text evidence.
    for p in walk_files(BASE/"generation"):
        if p.suffix.lower() in (".json", ".txt", ".md"):
            paths.add(p.as_posix())
    return [entry(p) for p in sorted(paths)]


def build_plan(mode, keep_sources=(), retire_sources=()):
    rows, controls, snapshots = verify_selections()
    selected = {f["source"] for f in rows}
    inventory = {}
    for png in walk_files(BASE/"generation"):
        if png.suffix.lower() != ".png":
            continue
        deletion_path(png)
        inventory[png.as_posix()] = {"path":png.as_posix(), "sha256":sha(png)}
    keep_explicit = {deletion_path(BASE/p).as_posix() for p in keep_sources}
    retire_explicit = {deletion_path(BASE/p).as_posix() for p in retire_sources}
    require(not keep_explicit & retire_explicit, "A path cannot be both kept and retired")
    closure, references = reference_closure(selected, inventory)
    keep, remove = [], []
    for name, item in sorted(inventory.items()):
        p = Path(name)
        rec = Path(name+".generation.json")
        reason = None
        if name in keep_explicit:
            reason = "explicit_current_master"
        elif mode == "unselected" and name in selected:
            reason = "selected_current_master"
        elif mode == "unselected" and name in closure:
            reason = "reference_ancestor_of_current_master"
        elif not rec.is_file():
            reason = "missing_generation_record_hold"
        else:
            meta = read(regular(rec))
            require(meta.get("sha256") == item["sha256"], f"Inventory metadata mismatch: {name}")
            require("actualModel" in meta and "actualQuality" in meta, f"Incomplete evidence: {rec}")
            if name not in selected and name not in retire_explicit and not retired(meta,p):
                reason = "unreviewed_or_active_source_hold"
            item = dict(item, generationRecord=rec.as_posix(), generationRecordSha256=sha(rec),
                        status=meta.get("status"))
        if reason:
            keep.append(dict(item, reason=reason))
        else:
            remove.append(item)
    protected = protected_files(controls, rows)
    state = {"selection":rows, "controls":controls, "generationInventory":list(inventory.values()),
             "protected":protected, "toolSha256":sha(Path(__file__))}
    plan = {"schemaVersion":VERSION, "character":"03_lotus_healer_girl", "base":BASE.as_posix(),
            "mode":mode, "createdAt":stamp(), "dryRun":True, "deletionExecuted":False,
            "counts":{"groups":14,"selected":196,"uniqueSourceSha256":196,
                      "generationPng":len(inventory),"keep":len(keep),"delete":len(remove)},
            "keepSources":sorted(keep_explicit), "retireSources":sorted(retire_explicit),
            "stateFingerprint":fingerprint(state), "selected":rows, "controls":controls,
            "keep":keep,"delete":remove,"references":references,
            "requiredFiles":protected,
            "externalSelectedSources":[x for x in rows if not inside(x["source"],BASE/"generation")],
            "note":"Technical retention check only; no visual or client acceptance inferred."}
    return plan, snapshots


def review_output(value):
    p = absolute(value if Path(value).is_absolute() else BASE/value)
    require(inside(p,BASE/"review") and p.suffix.lower()==".json", "Output must be a review JSON")
    no_links(p)
    require(p.parent.is_dir(), "Output parent must already exist")
    return p


def write_new(path, data):
    path = review_output(path)
    with path.open("x",encoding="utf-8") as handle:
        json.dump(data,handle,ensure_ascii=False,indent=2)
        handle.write("\n")


def verify_frozen(path):
    frozen = read(regular(path))
    require(frozen.get("base") == BASE.as_posix() and frozen.get("schemaVersion") == VERSION,
            "Freeze belongs to another character/version")
    require(frozen.get("counts",{}).get("selected") == 196, "Incomplete freeze")
    require(fingerprint(frozen["payload"]) == frozen["payloadSha256"], "Freeze payload changed")
    payload = frozen["payload"]
    # External native source records were snapshotted inside this JSON; local text must remain.
    for item in payload["requiredFiles"]:
        if not inside(item["path"],BASE):
            continue
        require(sha(regular(item["path"])) == item["sha256"], f"Frozen file changed: {item['path']}")
    for row in payload["selected"]:
        exported = asset(row["export"])
        require(inside(exported,BASE/"candidate"), "Frozen export escaped")
        require(sha(exported) == row["exportSha256"], "Frozen export changed")
        require(image_info(exported,True) == row["exportInfo"], "Frozen pixels changed")
    return frozen


def seal(plan, snapshots, path):
    payload = {"selected":plan["selected"],"controls":plan["controls"],
               "requiredFiles":plan["requiredFiles"], "sourceRecordSnapshots":snapshots}
    frozen = {"schemaVersion":VERSION,"base":BASE.as_posix(),"createdAt":stamp(),
              "counts":{"groups":14,"selected":196},"payloadSha256":fingerprint(payload),
              "payload":payload,"nativeImageBackupsCreated":False,
              "meaning":"Frozen1024 exports and text provenance; not visual/client approval."}
    write_new(path,frozen)
    verify_frozen(path)


def apply_plan(path, freeze_path):
    saved = read(regular(path))
    require(saved.get("base")==BASE.as_posix() and saved.get("schemaVersion")==VERSION,
            "Plan character/version mismatch")
    require(saved.get("mode") in ("unselected","all-sources"), "Unknown plan mode")
    fresh, _ = build_plan(saved["mode"],saved.get("keepSources",()),saved.get("retireSources",()))
    # Do not trust a plan's target list or edit it into permission to remove something else.
    for key in ("stateFingerprint","delete","keep","selected","requiredFiles","controls"):
        require(saved.get(key)==fresh.get(key), f"Stale/edited plan ({key}); dry-run again")
    if saved["mode"]=="all-sources":
        frozen = verify_frozen(freeze_path)
        require(frozen["payload"]["selected"] == fresh["selected"], "Freeze/selection mismatch")
        require(saved.get("freezeSha256") == sha(freeze_path), "Freeze changed since plan")
    selected_by_path = {r["source"]:r for r in fresh["selected"]}
    journal = review_output("review/cleanup-applied-"+datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")+".json")
    result = {"createdAt":stamp(),"base":BASE.as_posix(),"mode":saved["mode"],
              "plan":str(path),"planSha256":sha(path),"deleted":[],"complete":False}
    write_new(journal,result)
    try:
        # Full source/export pixel equality has just been checked above for all196.
        # Check inputs/aggregate again before EACH unlink, then its own PNG and provenance.
        for item in fresh["delete"]:
            for control in fresh["controls"]:
                require(sha(regular(control["path"]))==control["sha256"], "Selection changed during cleanup")
            p = deletion_path(item["path"])
            require(sha(p)==item["sha256"], f"Delete target changed: {p}")
            require(sha(regular(item["generationRecord"]))==item["generationRecordSha256"],
                    "Provenance changed during cleanup")
            if str(p.as_posix()) in selected_by_path:
                row=selected_by_path[p.as_posix()]
                require(sha(regular(row["exportRecord"]))==row["exportRecordSha256"], "Export record changed")
                pair_check(p,asset(row["export"]),row["sourceSha256"],row["exportSha256"])
            # Final component/ancestor reparse and link count checks immediately before unlink.
            deletion_path(p).unlink()
            result["deleted"].append(item)
            journal.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        if saved["mode"] == "all-sources":
            verify_frozen(freeze_path)
        else:
            verify_selections()
        result["complete"]=True
    finally:
        result["finishedAt"]=stamp()
        journal.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return {"journal":journal.as_posix(),"deleted":len(result["deleted"]),"complete":True}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode",choices=("unselected","all-sources"),default="unselected")
    parser.add_argument("--plan-file",help="New JSON under review; defaults to timestamped plan")
    parser.add_argument("--keep-source",action="append",default=[],help="Explicit current master to preserve")
    parser.add_argument("--retire-source",action="append",default=[],help="Explicitly reviewed retired PNG; recorded in plan")
    parser.add_argument("--freeze-file",default="review/cleanup-export-freeze.json")
    parser.add_argument("--write-freeze",action="store_true",help="Explicit text-only frozen export inventory; never deletes")
    parser.add_argument("--verify-freeze",action="store_true",help="Verify frozen exports even after source PNG removal")
    parser.add_argument("--apply",metavar="PLAN",help="Explicit deletion of exact revalidated plan; absent means dry-run")
    args=parser.parse_args()
    require(absolute(BASE)==absolute(EXPECTED_BASE),"This tool is locked to the03 lotus character at the known workspace")
    no_links(BASE)
    freeze=review_output(args.freeze_file)
    if args.verify_freeze:
        require(not args.apply and not args.write_freeze,"Choose one operation")
        verify_frozen(freeze)
        print(json.dumps({"frozenExportsVerified":True,"deleted":0}))
        return
    if args.apply:
        require(not args.write_freeze and not args.keep_source and not args.retire_source,
                "Apply uses only the saved plan; no simultaneous modifications")
        print(json.dumps(apply_plan(review_output(args.apply),freeze),ensure_ascii=True))
        return
    plan,snapshots=build_plan(args.mode,args.keep_source,args.retire_source)
    if args.write_freeze:
        require(args.mode=="all-sources","Freeze is an explicit all-sources preparation")
        seal(plan,snapshots,freeze)
    if args.mode=="all-sources":
        frozen=verify_frozen(freeze)
        require(frozen["payload"]["selected"]==plan["selected"],"Frozen selection no longer current")
        plan["freezeFile"]=freeze.as_posix()
        plan["freezeSha256"]=sha(freeze)
    name=args.plan_file or ("review/cleanup-plan-"+args.mode+"-"+datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")+".json")
    output=review_output(name)
    write_new(output,plan)
    print(json.dumps({"plan":output.as_posix(),"dryRun":True,"deleted":0,**plan["counts"]},ensure_ascii=True))


if __name__=="__main__":
    try:
        main()
    except (ValueError,KeyError,OSError) as error:
        raise SystemExit("REFUSED: "+str(error))

