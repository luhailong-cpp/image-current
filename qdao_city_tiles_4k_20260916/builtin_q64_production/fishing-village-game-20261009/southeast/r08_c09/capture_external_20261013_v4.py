import json,importlib.util,sys
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parent
Z=R.parent
spec=importlib.util.spec_from_file_location('external_sources',Z/'review_external_seams.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
O=R/'qa/external-bottom-row-20261013-v4';O.mkdir(parents=True,exist_ok=True)
sources=mod.Sources()
x,y=32768,28672;half=256;ch=384;edges=[];corners={}
for edge in ['north','east','south','west']:
 vertical=edge in ['east','west'];seam=x+4096 if edge=='east' else x if edge=='west' else y+4096 if edge=='south' else y
 start=y if vertical else x
 def box_at(lo,hi):return [seam-half,lo,seam+half,hi] if vertical else [lo,seam-half,hi,seam+half]
 geometry={'edgeOfCenterTile':edge,'seamAxis':'x' if vertical else 'y','seamGlobalCoordinate':seam,'seamCoordinateInStrip':half,'width':512}
 full=mod.write_evidence(sources,O,edge+'-full',box_at(start,start+4096),geometry)
 segments=[mod.write_evidence(sources,O,f'{edge}-segment-{i+1}',box_at(start+i*1024,start+(i+1)*1024),geometry) for i in range(4)]
 edges.append({'edge':edge,'full':full,'segments':segments})
 for i in range(5):
  px,py=(seam,start+i*1024) if vertical else (start+i*1024,seam)
  key=f'intersection-x{px}-y{py}'
  if key not in corners:
   corners[key]=mod.write_evidence(sources,O,key,[px-ch,py-ch,px+ch,py+ch],{'intersectionGlobal':[px,py],'intersectionInImage':[ch,ch]})
summary={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'centerTile':'r08_c09','tileCoreBox':[32768,28672,36864,32768],'coreCropNative':[115,115,1139,1139],'edges':edges,'intersections':list(corners.values()),'formalAccepted':False,'status':'native_visual_evidence_ready_or_pending_by_missing_sources','script':str(Path(__file__)),'scriptSha256':mod.sha(Path(__file__))}
(O/'external-seam-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps({'output':str(O),'edges':[{'edge':e['edge'],'readySegments':sum(s['sourceComplete'] for s in e['segments'])} for e in edges],'readyIntersections':[c['id'] for c in corners.values() if c['sourceComplete']]}))

