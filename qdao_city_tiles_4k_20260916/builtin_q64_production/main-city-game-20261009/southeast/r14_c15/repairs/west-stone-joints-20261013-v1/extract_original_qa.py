from pathlib import Path
import argparse,json,hashlib
from PIL import Image
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser(description='Read-only original-pixel 4096 map QA extraction; 24 internal seam quarters + 9 junctions + 16 outer quarters. Optional true-core north/west joins.')
 ap.add_argument('--candidate',required=True);ap.add_argument('--sha256',required=True);ap.add_argument('--output',required=True);ap.add_argument('--north');ap.add_argument('--north-sha256');ap.add_argument('--west');ap.add_argument('--west-sha256');ap.add_argument('--plan-only',action='store_true')
 a=ap.parse_args();p=Path(a.candidate);assert sha(p)==a.sha256.lower(),'candidate hash mismatch'
 im=Image.open(p);assert im.size==(4096,4096) and im.mode in ('RGB','RGBA')
 records=[];sources={'candidate':{'path':str(p),'sha256':sha(p)}};out=Path(a.output)
 if not a.plan_only:out.mkdir(parents=True,exist_ok=False)
 def crop(name,box,source=im,sourcekey='candidate'):
  c=source.crop(box);record={'name':name,'box':box,'source':sourcekey,'pixels':list(c.size),'scale':'1:1','resampling':False}
  if not a.plan_only:
   q=out/(name+'.png');c.save(q)
   check=Image.open(q);assert check.size==c.size and check.tobytes()==c.tobytes()
   record.update(path=str(q),sha256=sha(q))
  records.append(record)
 for axis in ['v','h']:
  for c in [1024,2048,3072]:
   for q in range(4):
    box=[c-256,q*1024,c+256,(q+1)*1024] if axis=='v' else [q*1024,c-256,(q+1)*1024,c+256]
    crop(axis+str(c)+'-q'+str(q),box)
 for y in [1024,2048,3072]:
  for x in [1024,2048,3072]:crop('j'+str(x)+'-'+str(y),[x-450,y-450,x+450,y+450])
 for edge in ['north','east','south','west']:
  for q in range(4):
   box={'north':[q*1024,0,(q+1)*1024,512],'south':[q*1024,3584,(q+1)*1024,4096],'west':[0,q*1024,512,(q+1)*1024],'east':[3584,q*1024,4096,(q+1)*1024]}[edge]
   crop(edge+'-q'+str(q),box)
 assert len(records)==49
 for edge in ['north','west']:
  path=getattr(a,edge)
  if path:
   expected=getattr(a,edge+'_sha256');assert expected and sha(path)==expected.lower()
   n=Image.open(path);assert n.size==(4096,4096) and n.mode==im.mode
   sources[edge]={'path':path,'sha256':sha(path)}
   for q in range(4):
    join=Image.new(im.mode,(1024,512) if edge=='north' else (512,1024))
    nb=[q*1024,3840,(q+1)*1024,4096] if edge=='north' else [3840,q*1024,4096,(q+1)*1024]
    cb=[q*1024,0,(q+1)*1024,256] if edge=='north' else [0,q*1024,256,(q+1)*1024]
    join.paste(n.crop(nb),(0,0));join.paste(im.crop(cb),(0,256) if edge=='north' else (256,0))
    crop('external-'+edge+'-q'+str(q),[0,0,*join.size],join,'true_core_join')
    records[-1]['pixelSources']=[{'source':edge,'box':nb},{'source':'candidate','box':cb}]
 assert sha(p)==a.sha256.lower()
 for edge in ['north','west']:
  if edge in sources:assert sha(sources[edge]['path'])==sources[edge]['sha256']
 index={'schemaVersion':1,'sourceFiles':sources,'evidenceCount':len(records),'readOnlySourceFiles':True,'noPixelResampling':True,'formalAccepted':False,'status':'extraction_only_visual_review_pending','evidence':records}
 if not a.plan_only:(out/'index.json').write_text(json.dumps(index,indent=2),encoding='utf-8')
 print(json.dumps({'output':str(out),'evidenceCount':len(records),'planOnly':a.plan_only,'sourceFiles':sources}))
if __name__=='__main__':main()

