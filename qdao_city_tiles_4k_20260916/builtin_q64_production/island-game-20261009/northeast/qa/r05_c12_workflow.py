import sys,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from native_work import *
mode,ident,*neighbors=sys.argv[1:]
if mode=='prepare':
 subprocess.run([sys.executable,str(ZONE/'native_work.py'),'guide',ident,*neighbors],check=True,stdout=subprocess.DEVNULL)
 p=ZONE/'prompts'/f'{ident}.inputs.json';r=read(p)
 if len(neighbors)>1:
  directions=[];a=patch(ident)['coreWorldBox']
  for n in neighbors:
   b=patch(n)['coreWorldBox'];directions.append('upper' if b[1]<a[1] else 'right' if b[0]>a[0] else 'left')
  r[1]['role']='exact native neighbor reference plate left-to-right: '+', '.join(directions)+'; each1254-square unscaled'
  write(p,r)
 print(json.dumps({'id':ident,'guide':r[0]['file'],'neighborRole':r[1]['role'],'nativeWorldBox':patch(ident)['nativeWorldBox']}))
elif mode=='inspect':
 seams=[];a=patch(ident)['coreWorldBox']
 for n in neighbors:
  b=patch(n)['coreWorldBox'];pair=[n,ident] if b[0]<a[0] or b[1]<a[1] else [ident,n]
  subprocess.run([sys.executable,str(ZONE/'inspect_seam.py'),*pair],check=True,stdout=subprocess.DEVNULL);seams.append('__'.join(pair))
 selected={}
 for tid in ['r04_c12','r05_c12']:
  s=read(ZONE/f'selection-{tid}.json')
  for row in s['cores']:
   for n in row:
    if n:selected[tuple(patch(n)['coreWorldBox'][:2])]=n
 coords=[(a[0],a[1]-1024),(a[0]+1024,a[1]-1024),(a[0],a[1]),(a[0]+1024,a[1])];selected[(a[0],a[1])]=ident
 corner=None
 if all(c in selected for c in coords):
  ns=[selected[c] for c in coords];subprocess.run([sys.executable,str(ZONE/'inspect_cross.py'),*ns],check=True,stdout=subprocess.DEVNULL);corner='cross_'+ns[-1]
 write(ZONE/'qa'/f'{ident}.local-inspection.json',{'id':ident,'seams':seams,'corner':corner,'status':'pending_visual_review'})
 print(json.dumps({'seams':seams,'corner':corner}))
elif mode=='select':
 p=ZONE/'qa'/f'{ident}.local-inspection.json';d=read(p)
 for seam in d['seams']:
  q=ZONE/'qa'/f'{seam}.json';s=read(q);s.update(status='passed_available_native_join',reviewer='repair_prepare_local',reviewedAtUtc=now(),geometryChecks={'visibleContours':'pass'},color='pass');write(q,s)
 if d['corner']:
  q=ZONE/'qa'/f'{d["corner"]}.json';s=read(q);s.update(status='passed_geometry_and_color',reviewer='repair_prepare_local',reviewedAtUtc=now());write(q,s)
 d.update(status='passed_available_neighbors_and_corner',reviewedAtUtc=now());write(p,d)
 p=ZONE/'native'/f'{ident}.png.generation.json';d=read(p);d.update(status='usable_native_candidate',internalSeams='passed available native neighbor joins and corner by repair_prepare_local',externalSeams='available core segments reviewed; full tile acceptance pending');write(p,d)
 p=ZONE/'selection-r05_c12.json';s=read(p);a=patch(ident)['coreWorldBox'];row=(a[1]%4096)//1024;col=(a[0]%4096)//1024;s['cores'][row][col]=ident;s['updatedAtUtc']=now();write(p,s)
 print(json.dumps({'selected':ident,'sha256':d['sha256']}))
