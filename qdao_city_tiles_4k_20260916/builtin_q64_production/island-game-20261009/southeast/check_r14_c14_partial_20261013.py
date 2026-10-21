from workflow import *
import sys
tid='r14_c14'; rev=sys.argv[1]
selected={f'{r}{c}':('v02' if (r,c)==(1,4) else 'v01') for r in range(1,5) for c in range(1,5) if (ROOT/'native'/f'{tid}_p{r}{c}_{"v02" if (r,c)==(1,4) else "v01"}.png').exists()}
q=ROOT/'qa'/f'{tid}-partial-{rev}';q.mkdir(exist_ok=False)
cores={rc:Image.open(ROOT/'native'/f'{tid}_p{rc}_{v}.png').convert('RGB').crop((115,115,1139,1139)) for rc,v in selected.items()}
entries=[]; groups={'h':[],'v':[]}
previous=read(ROOT/'qa'/f'{tid}-partial-{sys.argv[2]}'/'manifest.json') if len(sys.argv)>2 else {}
reused=[]
for rc,a in cores.items():
 r,c=map(int,rc)
 for typ,nrc in [('v',f'{r}{c+1}'),('h',f'{r+1}{c}')]:
  if nrc not in cores:continue
  old=next((e for e in previous.get('entries',[])+previous.get('reusedEntries',[]) if e['pair']==[rc,nrc] and all(sha(Path(s['file']))==s['sha256'] for s in e['sources'])),None)
  if old:reused.append(old);continue
  b=cores[nrc]
  if typ=='v':
   im=Image.new('RGB',(512,1024));im.paste(a.crop((768,0,1024,1024)));im.paste(b.crop((0,0,256,1024)),(256,0))
  else:
   im=Image.new('RGB',(1024,512));im.paste(a.crop((0,768,1024,1024)));im.paste(b.crop((0,0,1024,256)),(0,256))
  f=q/f'{rc}-{nrc}.png';im.save(f);groups[typ].append(im)
  entries.append({'pair':[rc,nrc],'file':str(f),'sha256':sha(f),'sources':[{'file':str(ROOT/'native'/f'{tid}_p{i}_{selected[i]}.png'),'sha256':sha(ROOT/'native'/f'{tid}_p{i}_{selected[i]}.png')} for i in [rc,nrc]]})
for typ,ims in groups.items():
 w,h=(1024,512) if typ=='h' else (512,1024)
 for start in range(0,len(ims),4):
  batch=ims[start:start+4];cols=2 if typ=='h' else min(4,len(batch));sheet=Image.new('RGB',(cols*w,((len(batch)+cols-1)//cols)*h))
  for i,im in enumerate(batch):sheet.paste(im,((i%cols)*w,(i//cols)*h))
  sheet.save(q/f'contact-{typ}-{start+1}.png')
preview=Image.new('RGB',(2048,2048),(128,128,128))
for rc,im in cores.items():r,c=map(int,rc);preview.paste(im.resize((512,512)),((c-1)*512,(r-1)*512))
preview.save(q/'layout-preview-not-final.png')
write(q/'manifest.json',{'tile':tid,'selectedVersions':selected,'uniqueCoreCount':len(selected),'nativeFileCount':len(list((ROOT/'native').glob(tid+'*.png'))),'entries':entries,'reusedEntries':reused,'status':'awaiting_visual_review','finalArtModified':False,'previewNotFinalArt':True})
print(q)
