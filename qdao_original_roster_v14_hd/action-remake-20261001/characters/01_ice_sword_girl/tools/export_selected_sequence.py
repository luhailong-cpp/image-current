"""Full-canvas candidate export with native evidence binding. No pose transforms."""
from pathlib import Path
import json,hashlib,sys
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1]
selection_path=(R/sys.argv[1]).resolve()
if not selection_path.is_relative_to(R):raise ValueError('Outside character directory')
s=json.loads(selection_path.read_text(encoding='utf-8-sig'))
action=s.get('action','run');direction=s['direction']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
outfiles=[]
for f in s['frames']:
 p=R/f['sourcePath'];im=Image.open(p).convert('RGBA')
 if min(im.size)<1024 or sha(p)!=f['sha256']:raise ValueError(str(p))
 out=R/f"candidate/{action}/{direction}/{f['frame']:02}.png";out.parent.mkdir(parents=True,exist_ok=True)
 im.resize((1024,1024),Image.Resampling.LANCZOS).save(out)
 rec={'file':out.relative_to(R).as_posix(),'sha256':sha(out),'width':1024,'height':1024,'mode':'RGBA','nativeFrameSize':list(im.size),'derivedFrom':{'file':f['sourcePath'],'sha256':sha(p),'generationRecord':f['generationRecord']},'operation':{'type':'whole_canvas_LANCZOS_downsample','inputSize':list(im.size),'outputSize':[1024,1024],'translation':[0,0],'crop':None,'alphaFootAlignment':False,'bboxNormalization':False,'mirrored':False,'poseInterpolation':False},'actualModel':None,'actualQuality':None,'modelQualityEvidence':f['generationRecord'],'status':'selected_sequence_for_review','clientRuntimeVerified':False}
 write(out.with_name(out.name+'.generation.json'),rec);outfiles.append(out)
for cell in [128,256]:
 rows=(len(outfiles)+3)//4;sheet=Image.new('RGB',(cell*4,(cell+24)*rows),'#c6d4d9');d=ImageDraw.Draw(sheet)
 for i,p in enumerate(outfiles):
  x=i%4*cell;y=i//4*(cell+24);im=Image.open(p).resize((cell,cell),Image.Resampling.LANCZOS)
  sheet.paste(im,(x,y+24),im);d.text((x+4,y+4),f'{direction}{i+1:02} {s["frames"][i]["durationMs"]}ms',fill='black')
 sheet.save(R/f'preview/{action}-{direction}-selected-{cell}.png')
print(json.dumps({'action':action,'direction':direction,'exported':len(outfiles),'cycleMs':sum(f['durationMs'] for f in s['frames'])}))
