from pathlib import Path
from PIL import Image
import json,hashlib,subprocess,sys
from workflow import ROOT,read,write,sha,now,progress
tile='r09_c11'
versions={p:'v01' for p in ['11','12','13','14','21','22','23','24','31','32','33','34','41','42','43','44']}
versions.update({'12':'v02','13':'v02','21':'v02','23':'v03','34':'v02','43':'v03'})
canvas=Image.new('RGB',(4096,4096));sources=[];selected={}
for rc,v in versions.items():
 f=ROOT/'native'/f'{tile}_p{rc}_{v}.png'; im=Image.open(f).convert('RGB');assert im.size==(1254,1254)
 x=(int(rc[1])-1)*1024;y=(int(rc[0])-1)*1024
 canvas.paste(im.crop((115,115,1139,1139)),(x,y))
 rec={'patch':f'{tile}_p{rc}','version':v,'file':f.as_posix(),'sha256':sha(f),'generationRecord':str(f)+'.generation.json','sourceCrop':[115,115,1139,1139],'destination':[x,y],'status':'candidate_only'}
 sources.append(rec);selected[rc]=f.name
output=ROOT/'tiles'/f'{tile}.candidate.png';canvas.save(output)
meta={'file':output.as_posix(),'sha256':sha(output),'generatedAt':now(),'width':4096,'height':4096,'format':'PNG','operation':'hard crop each native1254 source to 1024 core and paste at 1:1; no resampling, feathering or synthetic pixels','derivedFrom':sources,'singleShotNative4K':False,'formalAccepted':False,'externalEdges':{'right':'candidate visually checked against r09_c12 native; root review required','top':'pending adjacent tile','left':'pending adjacent tile','bottom':'pending adjacent tile'},'status':'complete_4k_candidate_pending_quality_acceptance'}
write(Path(str(output)+'.generation.json'),meta)
write(ROOT/f'selected-native-{tile}.json',{'tile':tile,'selectedAt':now(),'selected':sources,'formalAccepted':False,'selectionPurpose':'complete 4K candidate assembly, not final approval'})
for r in range(1,5):
 for c in range(1,5):
  a=f'{r}{c}'
  if c<4:
   b=f'{r}{c+1}';subprocess.run([sys.executable,str(ROOT/'qa/check_pair.py'),selected[a],selected[b],'horizontal',f'{tile}-p{a}-p{b}'],check=True,capture_output=True)
  if r<4:
   b=f'{r+1}{c}';subprocess.run([sys.executable,str(ROOT/'qa/check_pair.py'),selected[a],selected[b],'vertical',f'{tile}-p{a}-p{b}'],check=True,capture_output=True)
junctions=[]
for r in range(1,4):
 for c in range(1,4):
  b=[c*1024-256,r*1024-256,c*1024+256,r*1024+256]
  f=ROOT/'qa'/f'{tile}-junction-{r}{c}.png';canvas.crop(b).save(f)
  record={'file':f.as_posix(),'sha256':sha(f),'operation':'unscaled 512 square crop from hard-cut candidate','sourceBox':b,'derivedFrom':[{'file':output.as_posix(),'sha256':sha(output)}],'status':'pending_visual_review'}
  write(Path(str(f)+'.generation.json'),record);junctions.append(record)
write(ROOT/'qa'/f'{tile}-junctions.json',junctions)
progress(status='complete_4k_candidate_pending_quality_review',usableNativeCount=16,complete4kCount=1,formalAcceptedCount=0,currentPatch=None,nextStep='Review all24 seams and9 junctions; root external acceptance pending',candidateFile=output.as_posix(),candidateSha256=sha(output))
print(json.dumps({'candidate':str(output),'sha256':sha(output),'pixels':[4096,4096],'selectedNativeCount':len(sources),'junctions':len(junctions),'formalAccepted':False}))
