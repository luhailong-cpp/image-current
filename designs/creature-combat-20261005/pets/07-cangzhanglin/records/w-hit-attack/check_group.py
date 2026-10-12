from pathlib import Path
from PIL import Image, ImageDraw
import json, hashlib, datetime

root=Path(__file__).resolve().parents[2]
record_dir=root/'records/w-hit-attack'
out_dir=root/'qa/w-hit-attack'
out_dir.mkdir(parents=True,exist_ok=True)
frames=[]
for action,count,ms in [('hit',6,40),('attack',12,30)]:
    for n in range(1,count+1):
        key=f'{action}-W-{n:02d}'
        rec_path=record_dir/f'{key}.json'
        r=json.loads(rec_path.read_text(encoding='utf8'))
        path=root/r['file']
        im=Image.open(path)
        sha=hashlib.sha256(path.read_bytes()).hexdigest()
        assert im.size==(1024,1024) and im.mode=='RGBA',path
        assert r['sha256']==sha,path
        assert r['durationMs']==ms,path
        assert (root/r['prompt']).exists(),path
        assert r['actualModel'] is None and r['actualQuality'] is None
        assert r['submittedParameters']['model'] is None and r['submittedParameters']['quality'] is None
        for ref in r['references']:
            assert Path(ref['path']).exists(),ref
            assert hashlib.sha256(Path(ref['path']).read_bytes()).hexdigest()==ref['sha256'],ref
        a=im.getchannel('A')
        assert a.getextrema()==(0,255),path
        opaque=a.point(lambda v:255 if v>100 else 0).getbbox()
        r['visualReview']={'perFrameViewed':True,'method':'Tool-returned full image inspected individually, plus exported contact-sheet review','direction':'true W rear three-quarter; back, rump and rear hoof heels visible; left/up target direction','anatomy':'four quadruped legs (far limb may partly overlap), two branched antler groups, one cloud tail; no wings or weapon','dynamicStatus':'pending parent six-group normal/slow playback review','clientIntegration':'not performed'}
        r['status']='current_final_export'
        r['opaqueAlphaBBox']=opaque
        if key=='attack-W-08':
            r['replacesRejectedRecord']='records/w-hit-attack/attack-W-08.attempt-01.json'
            r['retryErrorRecord']='records/w-hit-attack/attack-W-08.retry-02-error.json'
        rec_path.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
        frames.append({'file':r['file'],'record':r['record'],'sha256':sha,'width':1024,'height':1024,'durationMs':ms,'alphaExtrema':a.getextrema(),'opaqueAlphaBBox':opaque})
assert len(frames)==18 and len(set(f['sha256'] for f in frames))==18
rejected=record_dir/'attack-W-08.attempt-01.json'
r=json.loads(rejected.read_text(encoding='utf8'));r['prompt']='prompts/w-hit-attack/attack-W-08.attempt-01.txt';rejected.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
for action,start,stop,name in [('hit',1,6,'hit-W'),('attack',1,6,'attack-W-01-06'),('attack',7,12,'attack-W-07-12')]:
    sheet=Image.new('RGB',(1536,1104),(38,45,49))
    d=ImageDraw.Draw(sheet)
    for k,n in enumerate(range(start,stop+1)):
        im=Image.open(root/f'runtime/{action}/W/{n:02d}.png').convert('RGBA').resize((512,512),Image.Resampling.LANCZOS)
        x=(k%3)*512;y=(k//3)*552
        d.text((x+16,y+12),f'{action} W {n:02d}',fill=(245,234,209))
        sheet.paste(im,(x,y+32),im)
    sheet.save(out_dir/f'{name}.png')
summary={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'frameCount':18,'technicalStatus':'passed','missingFrames':[],'duplicateHashes':[],'allRGBA1024':True,'allReferencesAndSHAsVerified':True,'modelQualityEvidence':'host-managed; actual model and quality not disclosed; null in every record','uniformExport':{'scaledCanvas':[960,960],'offset':[32,6],'outputCanvas':[1024,1024],'perFrameAlignment':False},'perFrameVisualStatus':'viewed; final review notes in frame records','dynamicReviewStatus':'pending parent six-group normal/slow playback review','clientIntegration':'not performed','frames':frames}
(record_dir/'CHECK.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
(record_dir/'SHA256SUMS.txt').write_text('\n'.join(f["sha256"]+'  '+f['file'] for f in frames)+'\n',encoding='utf8')
print(json.dumps({'frameCount':18,'technicalStatus':'passed','contactSheets':str(out_dir),'dynamicReviewStatus':summary['dynamicReviewStatus']},ensure_ascii=False))
