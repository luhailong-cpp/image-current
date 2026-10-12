from pathlib import Path
import sys,shutil,json
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent
sys.path.insert(0,str(T.parent))
import tile_native_workflow as w
import review_external_seams as ex
s=w.read(T/'selected-patches.json');assert len(s['patches'])==16
Q=T/'qa'/'color-20261012-v2';m=w.read(Q/'manifest.json');assert len(m['evidence'])==33
color=w.read(T/'colorpass-selected.json');assert 'colorpass-20261012-v2' in color['candidate']['file']
native=[]
for p in sorted((T/'native').glob('*.png')):
    r=w.read(p.with_suffix('.png.generation.json'));assert Image.open(p).size==(1254,1254) and w.sha(p)==r['sha256']
    stem=p.stem;receipt=w.read(T/(stem+'.receipt.json'));raw=Path(receipt['rawSourceCopy']);assert w.sha(raw)==r['sha256']
    native.append(dict(file=str(p),sha256=w.sha(p),dimensions=[1254,1254],rawCopyVerified=True,actualModel=r['actualModel'],actualQuality=r['actualQuality']))
outputs=[]
for item in color['outputRecords']:
    r=w.read(item['record']);src=Path(r['derivedFrom'][0]['file']);actual=np.asarray(Image.open(item['file']).convert('RGB'),dtype=np.int16);original=np.asarray(Image.open(src).convert('RGB'),dtype=np.int16)
    assert np.max(np.abs(actual-original))<=40 and w.sha(item['file'])==item['sha256'] and r['correctionEvidence']['reconstructionPixelsExactlyMatch']
    outputs.append(dict(file=item['file'],sha256=item['sha256'],maximumActualChannelChange=int(np.max(np.abs(actual-original))),actualCoordinateShift=r['actualCoordinateShift'],resampling=r['resampling'],imageBlur=r['imageBlur'],imagePixelBlending=r['imagePixelBlending']))
I=T/'qa'/'all-inner-boundaries-20261013';I.mkdir(exist_ok=True);entries=[]
for group in range(4):
    row=group+1;vertical=Image.new('RGB',(800,1024));horizontal=Image.new('RGB',(1024,800));ps=[]
    for col in range(1,5):
        pid=f'p{row}{col}';p=T/s['patches'][pid];im=Image.open(p).convert('RGB')
        vb=[130,115,330,1139];hb=[115,130,1139,330]
        v=im.crop(vb);h=im.crop(hb);v.save(I/(pid+'-x230-native.png'));h.save(I/(pid+'-y230-native.png'))
        vertical.paste(v,((col-1)*200,0));horizontal.paste(h,(0,(col-1)*200));ps.append(dict(patch=pid,file=str(p),sha256=w.sha(p),verticalCrop=vb,horizontalCrop=hb))
    vp=I/f'row{row}-vertical-four-native.png';hp=I/f'row{row}-horizontal-four-native.png';vertical.save(vp);horizontal.save(hp);entries.append(dict(row=row,verticalSheet=str(vp),horizontalSheet=str(hp),sources=ps,resamplingApplied=False))
w.write(I/'manifest.json',dict(tile=T.name,createdAt=w.now(),operation='32 exact 200px wide crops around conditioning x230/y230, assembled without scaling in row/column order',evidence=entries,visualReview='pending',formalAccepted=False))
E=T/'qa'/'external-20261013';E.mkdir(exist_ok=True);src=ex.Sources();external=[];ox,oy=36864,49152
for edge in ['north','west','east','south']:
    for i in range(4):
        if edge=='north':box=[ox+i*1024,oy-256,ox+(i+1)*1024,oy+256]
        elif edge=='south':box=[ox+i*1024,oy+4096-256,ox+(i+1)*1024,oy+4096+256]
        elif edge=='west':box=[ox-256,oy+i*1024,ox+256,oy+(i+1)*1024]
        else:box=[ox+4096-256,oy+i*1024,ox+4096+256,oy+(i+1)*1024]
        external.append(ex.write_evidence(src,E,f'{edge}-segment-{i+1}',box,dict(edge=edge)))
w.write(E/'manifest.json',dict(tile=T.name,createdAt=w.now(),selectionSha256=w.sha(T/'selected-patches.json'),evidence=external,formalAccepted=False))
candidate=T/'candidate'/'r13_c10-reviewed-native-4096-20261013.png';assert not candidate.exists();shutil.copy2(Q/'candidate-4096.png',candidate)
w.write(candidate.with_suffix('.png.derivation.json'),dict(file=str(candidate),sha256=w.sha(candidate),dimensions=[4096,4096],sources=m['sources'],sourceCandidate=str(Q/'candidate-4096.png'),sourceCandidateSha256=w.sha(Q/'candidate-4096.png'),operation='16 exact native cores [115,115,1139,1139] without resampling or blending',layoutPixelsUsed=False,formalAccepted=False,internalReady=False))
report=dict(tile=T.name,createdAt=w.now(),nativeOutputCount=len(native),selectedNativeCount=16,nativeOutputs=native,colorOutputs=outputs,maxColorChange=max(x['maximumActualChannelChange'] for x in outputs),candidate=str(candidate),candidateSha256=w.sha(candidate),regular33Viewed=True,additionalInnerManifest=str(I/'manifest.json'),externalManifest=str(E/'manifest.json'),internalReady=False,formalAccepted=False,inFlightRequests=0,actualModel=None,actualQuality=None,gitTouched=False,paidApiUsed=False)
w.write(T/'qa'/'native-verification-20261013.json',report)
s.update(candidate=str(candidate),candidateSha256=w.sha(candidate),internalReady=False,status='all_inner_boundary_visual_review_pending');w.write(T/'selected-patches.json',s)
print(json.dumps({k:v for k,v in report.items() if k not in ['nativeOutputs','colorOutputs']}))
