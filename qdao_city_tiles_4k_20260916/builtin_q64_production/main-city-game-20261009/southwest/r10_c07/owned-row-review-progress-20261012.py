from pathlib import Path
from datetime import datetime,timezone
import sys,json,hashlib
B=Path(__file__).resolve().parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
now=lambda:datetime.now(timezone.utc).isoformat()
tile,assembly,row,findings=sys.argv[1:];row=int(row);assert tile in {f'r{r:02d}_c{c:02d}' for r in range(9,17) for c in (7,8)}
a=read(assembly);assert a['tile']==tile;t=B/tile;q=t/'pipeline/qa'/Path(assembly).parent.name
names=[f'row{row:02d}-native-20261012/{f}' for f in ('whole-row.png','vertical-x1024.png','vertical-x2048.png','vertical-x3072.png')]
if row>1:names+=[f'horizontal_y{(row-1)*1024}_full.png']+[f'intersection_x{x}_y{(row-1)*1024}.png' for x in (1024,2048,3072)]
report={'tile':tile,'row':row,'reviewedAtUtc':now(),'assembly':str(assembly),'assemblySha256':sha(assembly),'sourceOutput':a['output'],'sourceContext':a['contextOutput'],'nativeRowAndVerticalSeamsActuallyViewed':True,'reviewedImages':[{'file':str(q/n),'sha256':sha(q/n)} for n in names],'findings':findings,'sourceResampling':False,'maximumFeatherRadiusPixels':2,'formalAccepted':False,'actualModel':None,'actualQuality':None}
p=q/f'row{row:02d}-visual-review-20261012.json';assert not p.exists();p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
selected=sorted(v.name.removesuffix('.png.generation.json') for v in (t/'native').glob('p??_??.png.generation.json'))
expected=[f'p{r:02d}_{c:02d}' for r in range(1,5) for c in range(1,5)];missing=[v for v in expected if v not in selected]
progress=t/'production-resume-20261012.json';d=read(progress) if progress.exists() else {'schemaVersion':2,'tile':tile,'worker':'/root/sol_right_20261012','builtinOnly':True,'paidApiAllowed':False,'historicalFreezeUnmodified':True,'formalAccepted':False,'actualModel':None,'actualQuality':None,'unsavedSuccessfulOutputCount':0,'rowReviews':[]}
d.update(selectedNativeCount=len(selected),nextMissingCoordinate=missing[0] if missing else None,status='native_art_production_active' if missing else 'full_candidate_provisional_pending_geometry_material_external_qa',latestNativeAssembly=str(assembly),updatedAtUtc=now(),formalAccepted=False)
d.setdefault('rowReviews',[]).append({'row':row,'qa':str(p),'sha256':sha(p),'findings':findings})
progress.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'qa':str(p),'selectedNativeCount':len(selected),'nextMissingCoordinate':d['nextMissingCoordinate']}))
