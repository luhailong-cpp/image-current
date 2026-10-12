from pathlib import Path
from PIL import Image
import numpy as np
from workflow import ROOT,read,write,sha,now,progress
tile='r10_c11';p=ROOT/'native/r10_c11_p14_v01.png';r=read(Path(str(p)+'.generation.json'));q=read(ROOT/'prompts/r10_c11_p14_v01.request.json');receipt=read(ROOT/'receipts/r10_c11_p14_v01.json')
original_sha=sha
def sha(path):
 return original_sha(path) if path.exists() else None
checks={'native1254':Image.open(p).size==(1254,1254),'nativeHash':sha(p)==r['sha256'],'sourceByteIdentical':sha(p)==sha(Path(r['sourceOutputPath'])),'promptHash':sha(Path(r['prompt']))==r['promptSha256'],'requestRefs':all(sha(Path(x['file']))==x['sha256'] for x in q['references']),'receiptReferencesMatch':[x['file'] for x in q['references']]==receipt['submittedArguments']['referenced_image_paths'],'receiptPromptMatches':Path(r['prompt']).read_text(encoding='utf-8').strip()==receipt['submittedArguments']['prompt'].strip(),'actualModelQualityUnknown':r['actualModel'] is None and r['actualQuality'] is None,'opaque':Image.open(p).mode=='RGB'}
guide=read(Path(q['references'][0]['file']+'.generation.json'));context=Image.open(q['references'][0]['file']).convert('RGB')
checks['guideDependenciesHash']=all(sha(Path(s['file']))==s['sha256'] for s in guide['derivedFrom'])
layout=Image.open(guide['derivedFrom'][0]['file']).convert('RGB')
for part in guide['placements']:layout.paste(Image.open(part['source']).convert('RGB').crop(part['sourceCrop']),tuple(part['destination']))
checks['guidePlacementReplayPixelIdentical']=np.array_equal(np.asarray(layout),np.asarray(context))
write(ROOT/'qa/r10_c11-gate-source-audit.json',{'reviewedAt':now(),'gate':'../../capacity-layout-gate-20261010.json','imageGenInFlight':False,'newCallsAfterGate':0,'generatedCoordinates':[r['coordinate']],'checks':checks,'allChecksPassed':all(checks.values()),'missingReferenceFiles':[x for x in q['references'] if not Path(x['file']).exists()],'candidateComplete':False,'formalAccepted':False,'preparedOnly':'r10_c11_p24 context/prompt exists; no generated result/request dispatched'})
# Exact real candidate edges; never fill missing lower-left with invented pixels.
paths={k:ROOT/'tiles'/f for k,f in [('nw','r09_c11.candidate.png'),('ne','r09_c12.candidate-v02.png'),('se','r10_c12.candidate-v02.png')]};ims={k:Image.open(v).convert('RGB') for k,v in paths.items()}
outputs=[]
def save(name,im,sources,operation):
 out=ROOT/'qa'/f'r10_c11-{name}.png';im.save(out);rec={'file':out.as_posix(),'sha256':sha(out),'operation':operation,'noResampling':True,'sources':[{'file':paths[k].as_posix(),'sha256':sha(paths[k])} for k in sources]};write(Path(str(out)+'.generation.json'),rec);outputs.append(rec)
for row in range(4):
 o=Image.new('RGB',(512,1024));o.paste(ims['nw'].crop((3840,row*1024,4096,row*1024+1024)),(0,0));o.paste(ims['ne'].crop((0,row*1024,256,row*1024+1024)),(256,0));save(f'gate-northpair-edge-{row+1}',o,['nw','ne'],'unscaled256+256 candidate edge hard join')
for col in range(4):
 o=Image.new('RGB',(1024,512));o.paste(ims['ne'].crop((col*1024,3840,col*1024+1024,4096)),(0,0));o.paste(ims['se'].crop((col*1024,0,col*1024+1024,256)),(0,256));save(f'gate-eastpair-edge-{col+1}',o,['ne','se'],'unscaled256+256 candidate edge hard join')
# only existing southwest p14 supplies junction; source comes directly from its native core.
o=Image.new('RGB',(512,512));o.paste(ims['nw'].crop((3840,3840,4096,4096)),(0,0));o.paste(ims['ne'].crop((0,3840,256,4096)),(256,0));o.paste(Image.open(p).crop((883,115,1139,371)),(0,256));o.paste(ims['se'].crop((0,0,256,256)),(256,256))
out=ROOT/'qa/r10_c11-gate-four-tile-junction.png';o.save(out);write(Path(str(out)+'.generation.json'),{'file':out.as_posix(),'sha256':sha(out),'operation':'unscaled four real256 corner crops; southwest from existing p14 native core','sources':[{'file':x.as_posix(),'sha256':sha(x)} for x in list(paths.values())+[p]],'noResampling':True,'formalAccepted':False})
progress(status='capacity_layout_gate_hold',usableNativeCount=1,currentPatch=None,nextStep='Await explicit root release; only existing-pixel QA/provenance/assembly allowed',lastError=None)
print({'checksPassed':all(checks.values()),'checks':checks,'seams':len(outputs),'inFlight':False})

