"""Export individually reviewed N/NE native frames using whole-canvas downsample only."""
from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json,datetime,sys
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
for d in (sys.argv[1:] or ['N','NE']):
 a=read(R/f'review/run-{d}-final-visual.json');frames=[];imgs=[];seen=set();checks=[]
 for f in a['frames']:
  p=R/f['sourcePath'];gpath=p.with_name(p.name+'.generation.json');g=read(gpath);im=Image.open(p).convert('RGBA');source_sha=sha(p)
  assert im.width==im.height and min(im.size)>=1024 and im.getchannel('A').getextrema()==(0,255)
  assert source_sha==g['sha256']
  receipt=R/g['evidence']['receipt'];assert sha(receipt)==g['evidence']['receiptSha256']
  pix=hashlib.sha256(im.tobytes()).hexdigest();assert pix not in seen;seen.add(pix)
  g['visualReview']={'status':'agent_visual_selected','actualPhase':f['actualPhase'],'actualContact':f['actualContact'],'notes':f['notes'],'clientRuntimeVerified':False};write(gpath,g)
  dest=R/f"candidate/run/{d}/{f['frame']:02}.png";dest.parent.mkdir(parents=True,exist_ok=True);out=im.resize((1024,1024),Image.Resampling.LANCZOS);out.save(dest)
  outrec={'schemaVersion':1,'file':dest.relative_to(R).as_posix(),'sha256':sha(dest),'width':1024,'height':1024,'mode':'RGBA','nativeFrameSize':list(im.size),'derivedFrom':{'file':p.relative_to(R).as_posix(),'sha256':source_sha,'generationRecord':gpath.relative_to(R).as_posix()},'operation':{'type':'whole_canvas_LANCZOS_downsample','inputSize':list(im.size),'outputSize':[1024,1024],'translation':[0,0],'crop':None,'alphaFootAlignment':False,'bboxNormalization':False,'mirrored':False,'poseInterpolation':False},'actualModel':None,'actualQuality':None,'visualReview':g['visualReview'],'clientRuntimeVerified':False}
  cr=dest.with_name(dest.name+'.generation.json');write(cr,outrec)
  frames.append(dict(f,path=dest.relative_to(R).as_posix(),sha256=sha(dest),sourceSha256=source_sha,nativeSize=list(im.size),generationRecord=cr.relative_to(R).as_posix(),nativeGenerationRecord=gpath.relative_to(R).as_posix(),durationMs=75,actualModel=None,actualQuality=None,status='selected_for_preview'))
  imgs.append(out)
  checks.append({'frame':f['frame'],'nativeSha':source_sha,'candidateSha':sha(dest),'nativeSize':list(im.size),'candidateSize':[1024,1024],'sourceReceiptMatches':True,'alphaExtrema':list(out.getchannel('A').getextrema()),'uniquePixels':True})
 selection={k:v for k,v in a.items() if k!='frames'};selection.update(schemaVersion=1,characterId=R.name,action='run',direction=d,updatedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),canvasSize=[1024,1024],timing={'cycleMs':1200,'frameDurationsMs':[75]*16,'formalClientTimingConfirmed':False},frames=frames,clientIntegrated=False,clientRuntimeVerified=False)
 write(R/f'review/run-{d}-selection.json',selection)
 write(R/f'review/run-{d}-technical.json',{'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'nativeAndExportPassed':True,'count':16,'cycleMs':1200,'checks':checks})
 for size in [128,256]:
  sheet=Image.new('RGB',(size*4,(size+22)*4),'#cad2d5');draw=ImageDraw.Draw(sheet)
  for i,im in enumerate(imgs):
   x=(i%4)*size;y=(i//4)*(size+22);small=im.resize((size,size),Image.Resampling.LANCZOS);sheet.paste(small,(x,y+22),small);draw.text((x+3,y+4),f'{d}{i+1:02} 75ms',fill='black')
  sheet.save(R/f'preview/run-{d}-selected-{size}.png')
 foot=Image.new('RGB',(360*4,245*4),'#ccd2d2');dr=ImageDraw.Draw(foot)
 for i,im in enumerate(imgs):
  x=i%4*360;y=i//4*245;crop=im.crop((300,640,920,1024));crop.thumbnail((360,220),Image.Resampling.LANCZOS);foot.paste(crop,(x,y+24),crop);dr.text((x+3,y+5),f'{d}{i+1:02} {frames[i]["sourcePath"].split("/")[-1]}',fill='black')
 foot.save(R/f'review/run-{d}-paired-feet-final.png')
 small=[im.resize((256,256),Image.Resampling.LANCZOS) for im in imgs];small[0].save(R/f'preview/run-{d}-1x-1200ms.webp',save_all=True,append_images=small[1:],duration=[75]*16,loop=0,lossless=True,method=6)
 print(json.dumps({'direction':d,'exported':16,'sourceVersions':[f['sourcePath'] for f in frames],'technicalPass':True}))
