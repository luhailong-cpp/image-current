"""Export current WIP for review only; never promote it to approved runtime art."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from datetime import datetime,timezone
import hashlib,json
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
selection=json.loads((R/'review/run-E-selection.json').read_text(encoding='utf-8-sig'))
outputs=[]
for frame in selection['frames']:
    if not frame:continue
    source=R/frame['sourcePath'];out=R/f"candidate/run/E/{frame['frame']:02}.png"
    out.parent.mkdir(parents=True,exist_ok=True)
    im=Image.open(source).convert('RGBA');im.resize((1024,1024),Image.Resampling.LANCZOS).save(out)
    record={'file':out.relative_to(R).as_posix(),'sha256':sha(out),'width':1024,'height':1024,'mode':'RGBA','nativeFrameSize':frame['nativeSize'],'derivedFrom':{'file':frame['sourcePath'],'sha256':sha(source),'generationRecord':frame['generationRecord']},'operation':{'type':'whole_canvas_LANCZOS_downsample','inputSize':list(im.size),'outputSize':[1024,1024],'translation':[0,0],'crop':None,'alphaFootAlignment':False,'bboxNormalization':False,'mirrored':False,'poseInterpolation':False},'actualModel':None,'actualQuality':None,'modelQualityEvidence':frame['generationRecord'],'status':'wip_review_only_not_runtime_approved','clientRuntimeVerified':False}
    write(out.with_name(out.name+'.generation.json'),record)
    outputs.append({'frame':frame['frame'],'path':record['file'],'sha256':record['sha256'],'durationMs':frame['durationMs'],'sourcePath':frame['sourcePath'],'generationRecord':out.with_name(out.name+'.generation.json').relative_to(R).as_posix()})
write(R/'candidate/manifest.json',{'createdAt':datetime.now(timezone.utc).isoformat(),'characterId':R.name,'status':'WIP_DO_NOT_REPLACE_CLIENT_RUNTIME','selectedFrameCount':len(outputs),'formalApprovedFrames':0,'clientIntegrated':False,'clientRuntimeVerified':False,'root':selection['root'],'timing':selection['timing'],'files':outputs})
# Contact sheet is a review visualization; native sprite pixels remain untouched.
cell=256;head=32;sheet=Image.new('RGB',(cell*4,(cell+head)*4),(233,239,237));d=ImageDraw.Draw(sheet)
for f in outputs:
    i=f['frame']-1;x=(i%4)*cell;y=(i//4)*(cell+head)
    d.text((x+8,y+7),f"E{i+1:02} | {f['durationMs']}ms | WIP",fill=(25,55,56))
    thumb=Image.open(R/f['path']).resize((cell,cell),Image.Resampling.LANCZOS)
    sheet.paste(thumb,(x,y+head),thumb)
    gy=y+head+round(.953*cell);d.line((x,gy,x+cell-1,gy),fill=(192,115,82),width=1)
sheet.save(R/'preview/selected-16-contact.png')
print(json.dumps({'exportedCandidateFrames':len(outputs),'formalApprovedFrames':0,'allSourceShaBound':all(sha(R/f['sourcePath'])==selection['frames'][f['frame']-1]['sha256'] for f in outputs)}))
