from pathlib import Path
from PIL import Image
from workflow import ROOT,read,write,sha,now
import json
base=ROOT/'tiles/r10_c11.candidate.png'; repair=ROOT/'native/r10_c11_wall-junction_v01.png'
canvas=Image.open(base).convert('RGB'); canvas.paste(Image.open(repair).convert('RGB'),(1421,2220))
out=ROOT/'tiles/r10_c11.candidate-v02.png'; canvas.save(out)
meta=read(Path(str(base)+'.generation.json')); meta.update({'file':out.as_posix(),'sha256':sha(out),'generatedAt':now(),'baseCandidate':{'file':base.as_posix(),'sha256':sha(base)},'operation':'16 original 1024 cores at 1:1, followed by one full 1254 native junction replacement at fixed original coordinates; hard paste only, no scaling or blend','overlays':[{'file':repair.as_posix(),'sha256':sha(repair),'generationRecord':str(repair)+'.generation.json','sourceCrop':[0,0,1254,1254],'destination':[1421,2220],'reason':'Full failed stone slab/coping junction corrected in one native redraw'}],'status':'candidate_pending_overlay_incoming_edge_review','formalAccepted':False})
write(Path(str(out)+'.generation.json'),meta)
selected=read(ROOT/'selected-native-r10_c11.json');selected.update({'candidateFile':out.as_posix(),'candidateSha256':sha(out),'baseCandidateFile':base.as_posix(),'overlays':meta['overlays']});write(ROOT/'selected-native-r10_c11.json',selected)
regions={'top':[1421,1964,2675,2476],'bottom':[1421,3218,2675,3730],'left':[1165,2220,1677,3474],'right':[2419,2220,2931,3474],'junction':[1792,2816,2304,3328]}
records=[]
for name,box in regions.items():
    f=ROOT/'qa'/f'r10_c11-junction-repair-v01-{name}.png';canvas.crop(box).save(f)
    records.append({'file':f.as_posix(),'sha256':sha(f),'source':out.as_posix(),'sourceSha256':sha(out),'sourceBox':box,'operation':'unscaled candidate crop','status':'pending_visual_review'})
write(ROOT/'qa/r10_c11-junction-repair-v01.json',records)
print(json.dumps({'file':out.as_posix(),'sha256':sha(out)}))
