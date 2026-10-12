"""Publish the two visually selected AI shoe-yaw repairs, preserving history."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
from PIL import Image
from export_frame import run
R=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=lambda:datetime.now(timezone.utc).isoformat()
config=read(Path('D:/work/image/config/image-generation.json'))
baseline=read(R/'audit/straight-axis-baseline.json')
review=read(R/'review.json')
for n in ['05','06']:
    key=f'attack/E/{n}';dst=R/(key+'.png');meta=Path(str(dst)+'.generation.json')
    assert sha(dst)==baseline['frames'][key+'.png'], 'Already published or concurrent image edit; stop.'
    stem=f'attack-E-{n}-straight-axis-v1';req=read(R/f'provenance/{stem}.request.json');receipt=read(R/f'provenance/{stem}.receipt.json')
    host=Path(receipt['observedToolReturnedPath']);src=R/f'run/staging/{stem}.png'
    shutil.copy2(host,src)
    im=Image.open(src);assert im.mode=='RGBA' and im.getchannel('A').getextrema()==(0,255)
    refs=[{'path':p,'sha256':sha(Path(p)),'role':'edit target' if i==0 else ('primary approved style' if i==3 else 'adjacent frame shoe-yaw reference')} for i,p in enumerate(req['submittedParameters']['referenced_image_paths'])]
    gen={'file':src.relative_to(R).as_posix(),'sha256':sha(src),'generatedAt':datetime.fromtimestamp(host.stat().st_mtime,timezone.utc).isoformat(),'generatedAtEvidence':'host file mtime; no tool timestamp','recordedAt':now(),'width':im.width,'height':im.height,'format':'PNG','mode':im.mode,'alphaExtrema':[0,255],'tool':'image_gen__imagegen','route':'builtin','configSnapshot':config,'submittedParameters':dict(req['submittedParameters'],model=None,quality=None),'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具没有型号/质量选择器，返回未披露实际型号和质量。','evidence':{'toolReturnedPath':str(host),'receipt':f'provenance/{stem}.receipt.json','workspaceCopyShaMatchesSource':sha(src)==sha(host)},'request':f'provenance/{stem}.request.json','prompt':f'provenance/{stem}.request.json','references':refs,'review':{'status':'root_native_visually_selected'}}
    save(Path(str(src)+'.generation.json'),gen)
    old=read(meta);prior=R/f'provenance/straight-axis-prior-attack-E-{n}-{old["sha256"][:12]}.json'
    assert not prior.exists();save(prior,old)
    run(src,dst);m=read(meta)
    m['registrationTransform']={'status':'applied','method':'direct_registered_canvas_redraw','globalScale':1.0,'inheritedCharacterScale':.8,'sourceRoot':[512,942],'targetRoot':[512,942],'outputSha256':sha(dst),'note':'AI edit of registered frame; whole canvas downsample only. No anatomy warp, extra 0.8 scaling or sole realignment.'}
    m['straightAxisRepair']={'previousSha256':old['sha256'],'priorGenerationRecord':prior.relative_to(R).as_posix(),'observation':'Rear support boot was front-on toward viewer; returned to eastward three-quarter side view while retaining original bent leg, stance and hand action.','status':'static_selected_pending_sequence_review','reviewedAt':now()}
    save(meta,m)
    oldReview=review[key];save(R/f'provenance/straight-axis-prior-review-attack-E-{n}.json',oldReview)
    review[key]={'sha256':sha(dst),'visualStatus':'pending','reviewedAt':now(),'reviewer':'root','notes':'Local shoe-yaw AI repair; pending final 04→07 sequence and browser review.','clientValidated':False}
save(R/'review.json',review)
save(R/'audit/straight-axis-model-policy.json',{'verifiedAt':now(),'officialVerificationDate':'2026-10-05','sources':config['sources'],'evidenceSummary':'Official release confirms Images 2.5 availability; Sunburst model documentation lists low, medium, high, xhigh, max, auto. Configuration target retained.','configSnapshot':config,'builtinHasModelQualityParameters':False,'actualModel':None,'actualQuality':None})
print('Published attack/E/05 and 06; only these two review states pending sequence review.')
