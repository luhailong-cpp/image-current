from pathlib import Path
import sys,json,importlib.util
T=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("p",T.parent/"production_v2.py");p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
identifier=sys.argv[1];note=sys.argv[2];pending=sys.argv[3].split(",") if len(sys.argv)>3 and sys.argv[3] else []
out=T/"qa/source-review"/identifier;m=p.read(out/"manifest.json")
record=dict(status="usable_for_nonconflicting_neighbor_continuation_pending_local_repair" if pending else "passed_available_native_source_review",source=m["source"],actuallyViewed=True,viewDetail="original",viewedNative=True,crops=[dict(file=x["file"],sha256=x["sha256"],actuallyViewed=True,verdict="needs_repair" if Path(x["file"]).stem in pending else "pass") for x in m["crops"]],notes=note,fullTileInternalQA=False,formalAccepted=False,reviewer="/root/resume_r06_c03_oct13")
p.write_json(out/"review-oct13-resume.json",record)
print(json.dumps(p.record_selection("r06_c03",identifier[:6],identifier,note,str(out/"review-oct13-resume.json"))))
