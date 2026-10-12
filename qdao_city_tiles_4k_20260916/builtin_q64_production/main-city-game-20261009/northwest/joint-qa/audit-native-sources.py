import json, hashlib, os
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r06_c05/..").resolve()
tiles=["r05_c04","r05_c05","r06_c04","r06_c05"]
def read(p):return json.loads(p.read_text(encoding="utf-8-sig"))
cache={}
def sha(p):
 p=Path(p)
 k=str(p.resolve())
 if k not in cache:cache[k]=hashlib.sha256(p.read_bytes()).hexdigest()
 return cache[k]
def norm(v):return os.path.normcase(os.path.normpath(str(v)))
def strings(v):
 if isinstance(v,str):return [v]
 if isinstance(v,dict):return sum([strings(x) for x in v.values()],[])
 if isinstance(v,list):return sum([strings(x) for x in v],[])
 return []
snaps=[]
sels={}
for t in tiles:
 p=z/t/"selection.json";snaps.append({"tile":t,"file":str(p),"sha256":sha(p)});sels[t]=read(p)
entries=[];issues=[];legacy=[];refs={}
for t in tiles:
 for row in range(1,5):
  for col in range(1,5):
   key=f"s{row:02}_{col:02}";p=Path(sels[t].get(key,str(z/t/"native"/(key+".png"))))
   rp=p.with_suffix(".png.generation.json");r=read(rp);ev=r.get("evidence",{})
   reqp=Path(ev.get("request",str(z/t/"receipts"/(p.stem+".request.json"))))
   recp=Path(ev.get("receipt",str(z/t/"receipts"/(p.stem+".result.json"))))
   req=read(reqp) if reqp.exists() else {};receipt=read(recp) if recp.exists() else {}
   promptp=Path(r.get("prompt",str(z/t/"prompts"/(p.stem+".txt"))))
   host=Path(ev.get("hostOutputPath",""));bad=[];notes=[]
   im=Image.open(p);im.load()
   native=sha(p)
   if im.size!=(1254,1254) or r.get("width")!=1254 or r.get("height")!=1254:bad.append("dimensions")
   if im.format!="PNG":bad.append("non_png")
   if im.mode=="RGBA" and im.getchannel("A").getextrema()!=(255,255):bad.append("transparent_pixels")
   if native!=r.get("sha256"):bad.append("native_record_hash")
   if r.get("route") not in ["builtin","builtin_image_gen"]:bad.append("route")
   if r.get("resizedAfterGeneration") or r.get("finalArtUpscaled"):bad.append("upsampling_flag")
   if r.get("actualModel") is not None or r.get("actualQuality") is not None:bad.append("non_null_backend_claim")
   host_ok=host.is_file() and sha(host)==native
   if not host_ok:bad.append("host_missing_or_not_byte_identical")
   if not reqp.exists():bad.append("request_missing")
   if not recp.exists():bad.append("receipt_missing")
   if not promptp.exists():bad.append("prompt_missing")
   pars=req.get("parameters",req.get("submittedParameters",{}));submitted=r.get("submittedParameters",{})
   refs_sub=pars.get("referenced_image_paths",[])
   if refs_sub!=submitted.get("referenced_image_paths",[]):bad.append("request_generation_refs_differ")
   if pars.get("prompt","").strip()!=submitted.get("prompt","").strip():bad.append("request_generation_prompt_differ")
   if promptp.exists() and promptp.read_text(encoding="utf-8-sig").strip()!=pars.get("prompt","").strip():bad.append("prompt_file_differ")
   for field,fp in [("requestSha256",reqp),("receiptSha256",recp),("promptSha256",promptp)]:
    expected=ev.get(field,r.get(field))
    if expected and fp.exists() and sha(fp)!=expected:bad.append(field+"_mismatch")
   rrefs={norm(v["file"]):v for v in r.get("references",[])}
   qrefs={norm(v["file"]):v for v in req.get("references",[])}
   ref_bad=[]
   for f in refs_sub:
    fp=Path(f);meta=rrefs.get(norm(f),qrefs.get(norm(f),{}));expected=meta.get("sha256") or qrefs.get(norm(f),{}).get("sha256")
    actual=sha(fp) if fp.is_file() else None
    status="matched" if actual and actual==expected else ("missing_file" if actual is None else ("missing_recorded_hash" if not expected else "hash_mismatch"))
    rk=(norm(f),expected);refs[rk]={"file":str(fp),"recordedSha256":expected,"currentSha256":actual,"status":status}
    if status!="matched":ref_bad.append({"file":str(fp),"status":status})
   if ref_bad:bad.append("reference_evidence_gap")
   canonical={"layout":any("tianyong-spring-natural-stone-v9.png" in v for v in refs_sub),"detail":any("tianyong-natural-stone-detail-v1.png" in v for v in refs_sub),"currentUserJPG":any("mail-daoist-style.jpg" in v for v in refs_sub)}
   if not canonical["currentUserJPG"]:legacy.append(t+":"+key)
   if "resizedAfterGeneration" not in r:notes.append("legacy_resize_flag_absent; unchanged host bytes independently checked")
   host_receipt=any(norm(str(host)) in norm(s) for s in strings(receipt))
   if not host_receipt:notes.append("receipt_host_literal_not_found; host path retained in generation evidence")
   e={"tile":t,"patch":key,"selectedId":p.stem,"explicitSelection":key in sels[t],"nativeSha256":native,"generationRecordSha256":sha(rp),"requestSha256":sha(reqp) if reqp.exists() else None,"receiptSha256":sha(recp) if recp.exists() else None,"pixels":list(im.size),"hostOutputPath":str(host),"hostByteIdentical":host_ok,"submittedReferenceCount":len(refs_sub),"canonicalReferences":canonical,"referenceIssues":ref_bad,"checksFailed":bad,"notes":notes}
   entries.append(e)
   if bad:issues.append({"tile":t,"patch":key,"checksFailed":bad,"referenceIssues":ref_bad})
end=[]
for s in snaps:
 p=Path(s["file"]);actual=hashlib.sha256(p.read_bytes()).hexdigest()
 if actual!=s["sha256"]:end.append({"tile":s["tile"],"startSha256":s["sha256"],"endSha256":actual})
snapshot=hashlib.sha256(json.dumps([{"tile":e["tile"],"patch":e["patch"],"id":e["selectedId"],"sha256":e["nativeSha256"]} for e in entries],sort_keys=True,separators=(",",":")).encode()).hexdigest()
report={"createdAtUtc":datetime.now(timezone.utc).isoformat(),"scope":"Effective64 selected sources across r05_c04/r05_c05/r06_c04/r06_c05; read-only mechanical evidence audit","snapshotSha256":snapshot,"selectionSnapshots":snaps,"selectionChangedDuringAudit":end,"summary":{"sources":len(entries),"native1254":sum(e["pixels"]==[1254,1254] for e in entries),"hostByteIdentical":sum(e["hostByteIdentical"] for e in entries),"sourcesWithChecksFailed":len(issues),"uniqueSubmittedReferences":len(refs),"referenceIssues":sum(v["status"]!="matched" for v in refs.values()),"legacyCurrentUserJPGNotSubmitted":len(legacy)},"interpretation":"Exact host-byte equality plus1254 native PNG disproves post-generation resize for matching sources. Referenced paths/recorded hashes are audited against disk; records remain evidence of submission, not independent backend introspection. Actual model/quality fields checked for null; target configuration strings are not backend proof.","issues":issues,"legacyStyleReferenceSources":legacy,"pendingUpdate":{"tile":"r06_c05","patch":"s02_01","snapshotSelected":next(e["selectedId"] for e in entries if e["tile"]=="r06_c05" and e["patch"]=="s02_01"),"note":"May be replaced by joint_repair material revision after this snapshot; recheck this source and recompute selected-source snapshot before final delivery."},"entries":entries,"referenceAudit":list(refs.values()),"visualQAPerformed":False,"newArtGenerated":False,"formalAccepted":False}
import argparse
parser=argparse.ArgumentParser(description="Read-only current64 native source evidence audit; immutable output report.")
parser.add_argument("--output",required=True,help="New report filename within joint-qa")
options=parser.parse_args()
out=(z/"joint-qa"/options.output).resolve()
out.relative_to((z/"joint-qa").resolve())
if out.exists():raise FileExistsError("Refusing to overwrite historical audit: "+str(out))
out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"file":str(out),"snapshotSha256":snapshot,"summary":report["summary"],"issues":issues},ensure_ascii=True,indent=2))

