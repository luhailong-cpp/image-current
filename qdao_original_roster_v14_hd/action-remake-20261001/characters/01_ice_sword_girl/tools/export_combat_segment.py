"""Private combat export and diagnostic sheets. Never edits source PNGs."""
import argparse,hashlib,json
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('action',choices=['hit','attack','cast']);p.add_argument('direction',choices=['E','W']);p.add_argument('versions',nargs='+');a=p.parse_args()
count={'hit':6,'attack':12,'cast':16}[a.action];ms={'hit':40,'attack':30,'cast':45}[a.action]
assert len(a.versions)==count
out=R/'candidate'/a.action/a.direction;out.mkdir(parents=True,exist_ok=True)
frames=[];sheet=Image.new('RGB',(256*4,(256+28)*((count+3)//4)),(39,54,65));draw=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15)
for i,version in enumerate(a.versions,1):
 rel=f'drafts/{a.action}/{a.direction}/{i:02}-v{version}.png';src=R/rel;im=Image.open(src);assert min(im.size)>=1024 and im.mode=='RGBA'
 genrel=rel+'.generation.json';g=json.loads((R/genrel).read_text(encoding='utf-8-sig'));assert sha(src)==g['sha256']
 receipt=json.loads((R/g['evidence']['receipt']).read_text(encoding='utf-8-sig'))
 dest=out/f'{i:02}.png';im.resize((1024,1024),Image.Resampling.LANCZOS).save(dest)
 destrel=dest.relative_to(R).as_posix();dg={'schemaVersion':1,'file':destrel,'sha256':sha(dest),'exportedAt':datetime.now(timezone.utc).isoformat(),'generatedAt':g['generatedAt'],'width':1024,'height':1024,'format':'PNG','mode':'RGBA','nativeFrameSize':list(im.size),'tool':g['tool'],'route':'native_builtin_then_whole_canvas_export','configSnapshot':g['configSnapshot'],'actualModel':g['actualModel'],'actualQuality':g['actualQuality'],'unverifiedReason':g['unverifiedReason'],'derivedFrom':{'path':rel,'sha256':sha(src),'generationRecord':genrel,'generationRecordSha256':sha(R/genrel)},'operation':{'type':'whole_canvas_resize','sourceSize':list(im.size),'targetSize':[1024,1024],'resampling':'Pillow LANCZOS','translation':[0,0],'bboxFit':False,'lowestAlphaAlignment':False},'visualReview':{'status':'candidate_sequence_review','clientRuntimeVerified':False}}
 dest.with_name(dest.name+'.generation.json').write_text(json.dumps(dg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 frames.append({'frame':i,'path':destrel,'sourcePath':rel,'sha256':sha(dest),'sourceSha256':sha(src),'generationRecord':destrel+'.generation.json','sourceGenerationRecord':genrel,'nativeSize':list(im.size),'status':'selected_for_review','durationMs':ms,'plannedPhase':receipt.get('plannedPhase'),'actualContact':None,'notes':'Actual stage/contact observations are in paired combat review report; not inferred from filename.','actualModel':None,'actualQuality':None})
 t=im.resize((256,256),Image.Resampling.LANCZOS);x=(i-1)%4*256;y=(i-1)//4*284;sheet.paste(t,(x,y+28),t);draw.text((x+6,y+3),f'{a.action}/{a.direction}/{i:02}-v{version} | {ms}ms',font=font,fill='white')
sel={'schemaVersion':1,'characterId':'01_ice_sword_girl','action':a.action,'direction':a.direction,'createdAt':datetime.now(timezone.utc).isoformat(),'canvasSize':[1024,1024],'nativeCanvasSize':[1254,1254],'root':{'point':[512,975.872],'farFootGroundY':970.752,'status':'provisional_global_diagnostic_only','definition':'Shared character diagnostic root; not used to translate or fit any PNG. Actual combat foot variation must be inspected.'},'timing':{'status':'offline_trial_client_unconfirmed','uniformCycleMs':count*ms,'frameDurationsMs':[ms]*count},'frames':frames,'events':{},'artStatus':'candidate_segment_needs_motion_review','clientRuntimeVerified':False,'formalExportCount':0}
report=R/f'review/combat-{a.action}-{a.direction}-selection.json';report.write_text(json.dumps(sel,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');sheet.save(R/f'review/combat-{a.action}-{a.direction}-contact-sheet.png')
assert len({f['sha256'] for f in frames})==count
print(json.dumps({'selection':str(report),'candidateFrames':count,'native':[1254,1254],'output':[1024,1024],'totalMs':count*ms,'shaDistinct':True}))

