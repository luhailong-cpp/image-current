from pathlib import Path
from datetime import datetime,timezone
import json,sys
from review_external_seams import Sources,write_evidence
T=sys.argv[1];label=sys.argv[2];r,c=map(int,[T[1:3],T[5:7]]);x,y=(c-1)*4096,(r-1)*4096
F=Path(__file__).resolve().parent/'seam-qa'/f'{T}-{label}';assert not F.exists();F.mkdir(parents=True)
S=Sources();edges=[];cross={}
for side in ['north','east','south','west']:
 vert=side in ['east','west'];k=x+4096 if side=='east' else x if side=='west' else y+4096 if side=='south' else y;start=y if vert else x
 def box(lo,hi):return [k-256,lo,k+256,hi] if vert else [lo,k-256,hi,k+256]
 seg=[write_evidence(S,F,f'{side}-segment-{i+1}',box(start+i*1024,start+(i+1)*1024),dict(edge=side,seamGlobalCoordinate=k,seamCoordinateInStrip=256)) for i in range(4)]
 edges.append(dict(edge=side,segments=seg))
 for i in range(5):
  px,py=(k,start+i*1024) if vert else (start+i*1024,k);ident=f'intersection-x{px}-y{py}'
  if ident not in cross:cross[ident]=write_evidence(S,F,ident,[px-384,py-384,px+384,py+384],dict(intersectionGlobal=[px,py],intersectionInImage=[384,384]))
m=dict(createdAt=datetime.now(timezone.utc).isoformat(),tile=T,edges=edges,intersections=list(cross.values()),formalAccepted=False)
(F/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(folder=str(F),readySegments=sum(e['sourceComplete'] for x in edges for e in x['segments']),readyCrossings=sum(e['sourceComplete'] for e in cross.values()),missing=[dict(id=e['id'],missing=e['missingSources']) for x in edges for e in x['segments'] if not e['sourceComplete']]),ensure_ascii=False))
