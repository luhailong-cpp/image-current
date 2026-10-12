from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, shutil, sys
from PIL import Image
T=Path(__file__).resolve().parent;B=T.parent;D=T/'repairs-resume-20261012/full-context-native-v01'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
now=lambda:datetime.now(timezone.utc).isoformat()
def write(p,x):
    assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def prepare():
    a=T/'repairs-resume-20261012/inner-rim-upper-v01/integrated/assembly.json';v=read(a);target=v['contextOutput']['file'];assert sha(target)==v['contextOutput']['sha256']
    c=read(B.parent/'production-contract.json');refs=[{'file':target,'sha256':sha(target),'role':'edit target: complete actual 4326x4326 native assembled tile context with recorded repairs; preserve exact crop, no resizing'}]
    for key in ('layoutReference','detailStyleReference','primaryStyleReference'):
        p=c[key];refs.append({'file':p,'sha256':sha(p),'role':key})
    p=B/'pipeline-tools/local-continuation-audit-20261011/r12-firstrow/ref-stone-context.png';refs.append({'file':str(p),'sha256':sha(p),'role':'quiet clean natural stone surface finish only; copy no geometry or red paper'})
    prompt='''Use case: precise-object-edit. EDIT IMAGE 1 ONLY. Return ONE opaque PNG at the exact native canvas size 4326x4326 pixels. Preserve the full native canvas and exact framing; no downscaling, resizing, zoom, recentering, crop expansion or substitution with the entire city. This is one tightly cropped part of a much larger approved map.
Repair only the visibly broken or kinked stone edging/rim lines and material continuity. The huge off-canvas circular plaza enters from upper-right and is cut by the right and bottom borders. Its concentric edging and inner pale rim must follow ONE regular smooth gently curved ellipse, with no elbows, reversed curvature, S bends, abrupt width changes, duplicated line ends, gaps or sharp internal patch boundaries. Preserve all existing intersections and endpoints at the outer image borders. In the upper-right, eliminate the abrupt elbow in the thin pale rim joint. In the lower rim, remove its unintended reverse bend and continue the source-scale ellipse smoothly. Fix the remaining tiny bevel stubs and offsets where independent native patches joined.
Keep the existing huge cropped partial angular stone meanders and top-left cloud engraving at EXACTLY their original positions and source scale. Do not create a complete circle, new symbol, duplicate/cloud ornaments, additional grout grid, small repeating keys or additional panels. Keep all existing red arena railing fragments along the left, cream edges, gold tips, shadows, open paving slabs and all their geometry and coordinates. Copy no extra city content.
Material-only cleanup: make all pale-grey and blue-grey stone calmly hand-painted with broad smooth restrained tonal variation and only sparse very faint wear. Remove dense repeating cellular, scaled, woven, pebbly textures and branching cracks. Preserve clear rounded bevels, readable edges and daylight, never use blur as a shortcut. Match quiet natural stone Image5 without copying its grout layout or red paper.
Images2/3/4 are mandatory approved whole-city geometry, daylight natural-stone finish and polished Q-style Daoist painting references only. Never copy their whole scene, framing, UI, text, people, moon, buildings, objects or props. Output only the same full close tile context as Image1 at exactly native 4326x4326. The 115px halo on all sides and all outer-border object intersections must stay aligned. All unrelated features remain unchanged.'''
    D.mkdir(parents=True,exist_ok=True);pp=D/'prompt.txt';assert not pp.exists();pp.write_text(prompt,encoding='utf-8')
    r={'tile':'r09_c07','name':'full-context-native-v01','prompt':prompt,'promptFile':str(pp),'promptSha256':sha(pp),'references':refs,'referenced_image_paths':[q['file'] for q in refs],'transparent_background':False,'requestedNativePixels':[4326,4326],'inputAssembly':str(a),'inputAssemblySha256':sha(a),'inputContext':target,'inputContextSha256':sha(target),'contextWorldBox':v['assembledContextWorldBox'],'nativeCoreBox':[115,115,4211,4211],'actualModel':None,'actualQuality':None,'builtinOnly':True,'apiUsed':False,'sourceResampling':False,'preparedAtUtc':now(),'native16SlotsRemainIntact':True,'productionResumeEvidence':{'file':'D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json','sha256':sha('D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json')}}
    write(D/'request.json',r);print(json.dumps({'request':str(D/'request.json'),'target':target}))
def ingest(source,started):
    s=Path(source);r=read(D/'request.json');dest=D/'returned-original.png';assert not dest.exists();shutil.copy2(s,dest);assert sha(dest)==sha(s)
    with Image.open(dest) as im:p=list(im.size);fmt=im.format;mode=im.mode;opaque=mode!='RGBA' or im.getextrema()[3]==(255,255)
    matches=p==[4326,4326] and fmt=='PNG' and opaque
    receipt={'tool':'image_gen.imagegen','status':'returned_image','sourceOutputPath':str(s),'sourceOutputSha256':sha(s),'savedUnmodifiedOriginal':str(dest),'sha256':sha(dest),'actualNativePixels':p,'format':fmt,'mode':mode,'actualModel':None,'actualQuality':None,'apiUsed':False,'startedAtUtc':started,'recordedAtUtc':now(),'request':str(D/'request.json'),'requestSha256':sha(D/'request.json'),'sizeMatchesRequested':matches,'explicitlyRejected':not matches,'visualDisposition':'pending_full_native_comparison' if matches else 'wrong_actual_native_size_preserved_only_no_resize_no_selected_slot','output_hint':f'Generated images are saved to {s.parent} as {s} by default.'}
    write(D/'tool-result.json',receipt);write(D/'generation.json',{**r,'file':str(dest),'sha256':sha(dest),'sourceOutputPath':str(s),'sourceOutputSha256':sha(s),'actualNativePixels':p,'evidence':{'toolReceipt':str(D/'tool-result.json'),'toolReceiptSha256':sha(D/'tool-result.json')},'formalAccepted':False,'nativePixelsPreserved':True,'resizedAfterGeneration':False,'sizeMatchesRequested':matches})
    print(json.dumps({'original':str(dest),'pixels':p,'sha256':sha(dest),'matches':matches,'formalAccepted':False}))
if __name__=='__main__':
    if sys.argv[1]=='prepare':prepare()
    else:ingest(*sys.argv[2:])
