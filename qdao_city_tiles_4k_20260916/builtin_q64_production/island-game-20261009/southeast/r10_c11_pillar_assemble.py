from pathlib import Path
from PIL import Image
from workflow import ROOT,read,write,sha,now
import json
base=ROOT/'tiles/r10_c11.candidate-v02.png';repair=ROOT/'native/r10_c11_pillar-body_v01.png'
crop=[390,100,935,1020];destination=[2670,2550]
canvas=Image.open(base).convert('RGB');canvas.paste(Image.open(repair).convert('RGB').crop(crop),tuple(destination))
out=ROOT/'tiles/r10_c11.candidate-v03.png';canvas.save(out)
meta=read(Path(str(base)+'.generation.json'))
overlay={'file':repair.as_posix(),'sha256':sha(repair),'generationRecord':str(repair)+'.generation.json','sourceCrop':crop,'destination':destination,'reason':'Complete native pillar-body material correction; hard rectangular crop follows existing pillar body bounds'}
meta.update({'file':out.as_posix(),'sha256':sha(out),'generatedAt':now(),'operation':'16 original1024 cores followed by two original-size native repair crop/pastes; no resizing, interpolation, feathering or blending','previousCandidate':{'file':base.as_posix(),'sha256':sha(base)},'status':'candidate_pending_final_review','formalAccepted':False})
meta['overlays'].append(overlay);write(Path(str(out)+'.generation.json'),meta)
selected=read(ROOT/'selected-native-r10_c11.json');selected.update({'candidateFile':out.as_posix(),'candidateSha256':sha(out),'overlays':meta['overlays']});write(ROOT/'selected-native-r10_c11.json',selected)
x,y=destination;w=crop[2]-crop[0];h=crop[3]-crop[1]
regions={'top':[x-128,y-128,x+w+128,y+128],'bottom':[x-128,y+h-128,x+w+128,y+h+128],'left':[x-128,y,x+128,y+h],'right':[x+w-128,y,x+w+128,y+h],'body':[x-128,y-128,x+w+128,y+h+128]}
records=[]
for name,box in regions.items():
 f=ROOT/'qa'/f'r10_c11-pillar-repair-v01-{name}.png';canvas.crop(box).save(f)
 records.append({'file':f.as_posix(),'sha256':sha(f),'source':out.as_posix(),'sourceSha256':sha(out),'sourceBox':box,'operation':'unscaled candidate crop','status':'pending_visual_review'})
write(ROOT/'qa/r10_c11-pillar-repair-v01.json',records)
print(json.dumps({'file':out.as_posix(),'sha256':sha(out)}))
