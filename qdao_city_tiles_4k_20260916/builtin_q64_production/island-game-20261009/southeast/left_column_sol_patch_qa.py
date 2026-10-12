from pathlib import Path
from PIL import Image
from workflow import ROOT,read,write,sha,now
import sys
tile,rc=sys.argv[1:3];assert tile in ['r13_c11','r14_c11'];r,c=map(int,rc)
sel=read(ROOT/f'selection-{tile}.json')['patchVersions'];v=sel[rc];target=ROOT/'native'/f'{tile}_p{rc}_{v}.png';a=Image.open(target)
folder=ROOT/'qa'/f'{tile}_p{rc}-{v}-sol-neighbor-check';assert not folder.exists();folder.mkdir();entries=[]
def emit(side,source,crop,dest,pcrop,pdest,size):
    source=Path(source);b=Image.open(source);im=Image.new('RGB',size);im.paste(b.crop(crop),dest);im.paste(a.crop(pcrop),pdest);out=folder/(side+'.png');im.save(out);entries.append({'side':side,'file':str(out),'sha256':sha(out),'target':str(target),'targetSha256':sha(target),'targetCrop':pcrop,'neighbor':str(source),'neighborSha256':sha(source),'neighborCrop':crop,'operation':'Exact source pixels and hard paste only','status':'pending_visual_review'})
for side,nr,nc in [('north',r-1,c),('west',r,c-1),('east',r,c+1),('south',r+1,c)]:
    key=str(nr)+str(nc)
    if key not in sel:continue
    source=ROOT/'native'/f'{tile}_p{key}_{sel[key]}.png'
    if tile=='r13_c11' and rc=='24' and side=='north':
        emit(side,ROOT/'qa/r13_c11-first-row-sol-v01/first-row.png',[3072,768,4096,1024],(0,0),[115,115,1139,371],(0,256),(1024,512));continue
    if side=='north':emit(side,source,[115,883,1139,1139],(0,0),[115,115,1139,371],(0,256),(1024,512))
    elif side=='west':emit(side,source,[883,115,1139,1139],(0,0),[115,115,371,1139],(256,0),(512,1024))
    elif side=='east':emit(side,source,[115,115,371,1139],(256,0),[883,115,1139,1139],(0,0),(512,1024))
    else:emit(side,source,[115,115,1139,371],(0,256),[115,883,1139,1139],(0,0),(1024,512))
if r==1:
    north='r12_c11' if tile=='r13_c11' else 'r13_c11';source=Path(read(ROOT/f'progress-{north}.json')['candidate']);emit('external-north',source,[(c-1)*1024,3840,c*1024,4096],(0,0),[115,115,1139,371],(0,256),(1024,512))
write(folder/'manifest.json',{'createdAt':now(),'target':str(target),'targetSha256':sha(target),'entries':entries,'formalAccepted':False});print({'folder':str(folder),'count':len(entries)})
