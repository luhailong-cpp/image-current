import sys,json
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent
BASE=HERE.parent.parent
sys.path.insert(0,str(BASE))
from review_external_seams import Sources,write_evidence,read_json,sha
tile=sys.argv[1]
folder=HERE/tile
folder.mkdir(exist_ok=True)
row,col=int(tile[1:3]),int(tile[5:7])
x,y=(col-1)*4096,(row-1)*4096
sources=Sources()
results=[]
old_path=BASE/tile/'qa'/'partial-internal-review.json'
old=read_json(old_path) if old_path.exists() else {}
reuse={e['id']:e for k in ('seams','crossings') for e in old.get(k,[])}
for r in range(4):
 for c in range(4):
  pid=f'p{r+1}{c+1}'
  for dr,dc in ((0,1),(1,0)):
   if r+dr>=4 or c+dc>=4:continue
   nid=f'p{r+dr+1}{c+dc+1}'
   sx,sy=x+(c+dc)*1024,y+(r+dr)*1024
   box=[sx-256,sy,sx+256,sy+1024] if dc else [sx,sy-256,sx+1024,sy+256]
   res=write_evidence(sources,folder,f'{pid}--{nid}',box,{'axis':'x' if dc else 'y','coordinateInImage':256})
   results.append(res)
for r in range(1,4):
 for c in range(1,4):
  cx,cy=x+c*1024,y+r*1024
  results.append(write_evidence(sources,folder,f'cross-r{r}-c{c}',[cx-256,cy-256,cx+256,cy+256],{'intersectionGlobal':[cx,cy],'intersectionInImage':[256,256]}))
for res in results:
 prev=reuse.get(res['id'])
 if prev and prev.get('visualStatus','').startswith('reviewed') and res['image'] and res['image']['sha256']==prev['sha256']:
  recpath=Path(res['report']);rec=read_json(recpath)
  if rec['visualReview']['status']=='pending_view_image_review':
   rec['visualReview']={'status':'reviewed_reused_identical_pixels','candidateUsable':True,'formalAccepted':False,'structuralBlockers':[],'colorOnlyRisks':[],'reusedFrom':str(old_path),'reusedReportSha256':sha(old_path),'evidencePngSha256Matched':True,'observations':[prev.get('reviewNotes','')]}
   recpath.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
   res['visualReview']=rec['visualReview']
out={'tile':tile,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'results':results,'formalAccepted':False}
(folder/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'tile':tile,'complete':sum(r['sourceComplete'] for r in results),'pendingView':[r['id'] for r in results if r['sourceComplete'] and r['visualReview']['status']=='pending_view_image_review']}))
