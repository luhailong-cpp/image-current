from pathlib import Path
import json,hashlib
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05");D=B/"repairs-audit-line-20261011";sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rejection={"status":"not_selected_not_deliverable","reason":"48px alpha exceeds inherited mechanical feather limit2px; local visual improvement is not acceptance","formalAccepted":False,"internalAccepted":False,"supersededBy":"pending new native strictly local protected-ROI edit and<=2px composition","sourceProposal":"roof-horizontal-join-v01/proposal-v02.json"}
(D/"integrated-local-v02/disposition.json").write_text(json.dumps(rejection,indent=2))
(D/"roof-horizontal-join-v01/proposal-v02.disposition.json").write_text(json.dumps(rejection,indent=2))
(D/"integrated-local-v01/disposition.json").write_text(json.dumps({"status":"not_selected","reason":"2px color-threshold mask produced visible holes/patch boundaries in gold; retain failed composite evidence","formalAccepted":False},indent=2))
q=json.loads((D/"roof-horizontal-join-v01/request.json").read_text());f=D/"roof-horizontal-protected-v02";f.mkdir(exist_ok=False)
p="Edit IMAGE1 only. Make ONE tiny local structural repair within pixel box x260..855,y420..860: remove the abrupt cut end of the extra short upper gold tongue and smoothly join it into the existing SINGLE gold rail rising toward the round boss. Keep the gold rail unchanged outside that box. Match its exact original brush texture, hue, brightness and highlight. Keep every pixel of the blue background, cream paving, teal molding, red support, large round gold boss and every image edge unchanged. DO NOT smooth, recolor, clean, or retexture the rest of the image. No new ornament, branch, or parallel rail. The exact rail continuation already enters the left side at y930 and must remain there. References2-5 context only. Same native1254square crop, opaquePNG, no rescale."
pf=f/"prompt.txt";pf.write_text(p)
q.update(attempt=f.name,prompt=p,promptFile=str(pf),promptSha256=sha(pf),visualDisposition="prepared exact local gold join correction; outside protected")
(f/"request.json").write_text(json.dumps(q,indent=2));print(json.dumps(q))

