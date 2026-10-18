from workflow import ROOT,read,write,sha,now
from pathlib import Path
from PIL import Image
import sys
tile,rc,v=sys.argv[1:4];assert tile in ['r13_c10','r14_c10'];a=Image.open(ROOT/'native'/f'{tile}_p{rc}_{v}.png');r,c=map(int,rc);sel=read(ROOT/f'selection-{tile}.json')['patchVersions'];d=ROOT/'qa'/f'left-resume-{tile}-p{rc}-{v}';d.mkdir(exist_ok=True);out=[]
north='r12_c10' if tile=='r13_c10' else 'r13_c10';east=tile.replace('c10','c11')
for side,nr,nc in [('N',r-1,c),('W',r,c-1),('E',r,c+1),('S',r+1,c)]:
 key=f'{nr}{nc}';f=None
 if key in sel:f=ROOT/'native'/f'{tile}_p{key}_{sel[key]}.png'
 elif side=='N' and r==1 and (ROOT/f'selection-{north}.json').exists():
  ss=read(ROOT/f'selection-{north}.json')['patchVersions'];k=f'4{c}'
  if k in ss:f=ROOT/'native'/f'{north}_p{k}_{ss[k]}.png'
 elif side=='E' and c==4 and (ROOT/f'selection-{east}.json').exists():
  ss=read(ROOT/f'selection-{east}.json')['patchVersions'];k=f'{r}1'
  if k in ss:f=ROOT/'native'/f'{east}_p{k}_{ss[k]}.png'
 if f is None or not f.exists():continue
 b=Image.open(f)
 if side in ['N','S']:
  im=Image.new('RGB',(1024,512));up,down=(b,a) if side=='N' else (a,b);im.paste(up.crop((115,883,1139,1139)),(0,0));im.paste(down.crop((115,115,1139,371)),(0,256))
 else:
  im=Image.new('RGB',(512,1024));left,right=(b,a) if side=='W' else (a,b);im.paste(left.crop((883,115,1139,1139)),(0,0));im.paste(right.crop((115,115,371,1139)),(256,0))
 dst=d/(side+'.png');im.save(dst);out.append(dict(file=str(dst),sha256=sha(dst),neighbor=str(f),neighborSha256=sha(f)))
write(d/'manifest.json',dict(createdAt=now(),target=str(ROOT/'native'/f'{tile}_p{rc}_{v}.png'),entries=out,status='pending_visual_review'));print(str(d))
