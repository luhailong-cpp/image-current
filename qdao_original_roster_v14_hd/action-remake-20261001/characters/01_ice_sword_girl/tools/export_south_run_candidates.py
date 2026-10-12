"""Private S/SE/SW whole-canvas candidate exporter. No image registration changes."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,sys
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
direction=sys.argv[1]
assert direction in ('S','SE','SW')
spec=json.loads((ROOT/f'review/run-{direction}-build-spec.json').read_text(encoding='utf-8'))
frames=[];now=datetime.now(timezone.utc).isoformat()
sheet=Image.new('RGB',(1024,1120),(217,223,227));draw=ImageDraw.Draw(sheet)
for obs in spec['observations']:
 n=obs['frame'];v=spec['versions'][str(n)];source_n=spec.get('sourceFrames',{}).get(str(n),n)
 source=ROOT/f'drafts/run/{direction}/{source_n:02}-v{v}.png';record=source.with_name(source.name+'.generation.json')
 original=json.loads(record.read_text(encoding='utf-8'));im=Image.open(source);assert im.mode=='RGBA' and min(im.size)>=1024
 destination=ROOT/f'candidate/run/{direction}/{n:02}.png';destination.parent.mkdir(parents=True,exist_ok=True)
 exported=im.resize((1024,1024),Image.Resampling.LANCZOS);exported.save(destination)
 outrec=destination.with_name(destination.name+'.generation.json')
 rec={'schemaVersion':1,'file':str(destination.relative_to(ROOT)).replace('\\','/'),'sha256':sha(destination),'generatedAt':original['generatedAt'],'exportedAt':now,'tool':'image_gen__imagegen','route':'builtin_then_whole_canvas_downsample','configSnapshot':original['configSnapshot'],'actualModel':None,'actualQuality':None,'unverifiedReason':original['unverifiedReason'],'width':1024,'height':1024,'mode':'RGBA','format':'PNG','nativeFrameSize':list(im.size),'derivedFrom':{'path':str(source.relative_to(ROOT)).replace('\\','/'),'sha256':sha(source),'generationRecord':str(record.relative_to(ROOT)).replace('\\','/'),'generationRecordSha256':sha(record)},'operation':{'type':'whole_canvas_downsample','size':[1024,1024],'scale':[1024/im.width,1024/im.height],'translation':[0,0],'bboxScaling':False,'lowestFootAlignment':False,'mirrored':False,'interpolatedFrames':False},'visualReview':{'status':'selected_candidate_needs_sequence_review','clientRuntimeVerified':False}}
 write(outrec,rec)
 frame={'frame':n,'path':str(source.relative_to(ROOT)).replace('\\','/'),'sourcePath':str(source.relative_to(ROOT)).replace('\\','/'),'sha256':sha(source),'nativeSize':list(im.size),'generationRecord':str(record.relative_to(ROOT)).replace('\\','/'),'candidatePath':str(destination.relative_to(ROOT)).replace('\\','/'),'candidateSha256':sha(destination),'candidateGenerationRecord':str(outrec.relative_to(ROOT)).replace('\\','/'),'status':'selected_for_preview','actualContact':{'left':obs['left'],'right':obs['right'],'confidence':'manual_visual_candidate_physical_contact_unverified','evidence':obs['evidence']},'notes':obs['evidence'],'durationMs':75,'actualModel':None,'actualQuality':None}
 frames.append(frame)
 tile=exported.resize((256,256),Image.Resampling.LANCZOS);x=(n-1)%4*256;y=(n-1)//4*280;sheet.paste(tile,(x,y+24),tile);draw.text((x+7,y+5),f'{direction}{n:02} src{source_n:02}v{v}',fill='black')
assert len(frames)==16 and len({f['sha256'] for f in frames})==16
sheet.save(ROOT/f'review/run-{direction}-selected-contact.png')
selection={'schemaVersion':1,'characterId':'01_ice_sword_girl','direction':direction,'createdAt':now,'canvasSize':[1024,1024],'nativeCanvasSize':[1254,1254],'root':{'status':'provisional_by_actual_direction_not_alpha_aligned','definition':'固定整画布；接触像素不是贴线规则，各脚前后投影需人工核对。'},'timing':{'status':'normal_preview_user_selected_client_unconfirmed','uniformCycleMs':1200,'frameDurationsMs':[75]*16,'comparisonsMs':[],'formallyAdopted':False,'offlineDefaultApplied':True,'reason':'用户指定16帧均匀75ms，1200ms一圈，接触事件按实图候选记录。'},'artStatus':'needs_sequence_review','clientIntegrated':False,'clientRuntimeVerified':False,'candidateExportCount':16,'formalExportCount':0,'referenceCharacter':'09_bamboo_archer_girl_current_user_confirmed','events':spec['events'],'issues':spec['issues'],'frames':frames}
write(ROOT/f'review/run-{direction}-selection.json',selection)
print(json.dumps({'direction':direction,'count':16,'cycleMs':1200,'nativeUnique':len({f['sha256'] for f in frames}),'selection':str(ROOT/f'review/run-{direction}-selection.json')}))

