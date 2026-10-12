"""Apply the two independently reviewed shoe-heading edits to current native selections."""
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'review/axis-review-20261004'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
review=OUT/'side-repair-review.json'
review_text=review.read_text(encoding='utf-8-sig')
jobs=[('E',16,'axis-16-v1','b4d75db3fc6dd620b2bc9771436bf4b83b3763185468db8878ab1b0d0ac9730a','两鞋偏航回到E向运动平面，减少朝镜头的短正面鞋形；右悬空脚保持将落地的俯仰，左脚后侧支撑，膝踝与手持侧保留。'),
      ('W',15,'axis-15-v1','74339120198817e2d952d6e46b9de1b1ea54708526bb4a785994f5dbe6b138fd','前抬右鞋转回W向侧帮长轴，减小14→15→16的朝镜头偏航变化；左后撑鞋保留，膝踝与左右手未改变。')]
changes=[]
for direction,number,stem,expected,observation in jobs:
    source=f'generation/run/{direction}/{stem}.png';p=ROOT/source
    assert sha(p)==expected and expected in review_text
    with Image.open(p) as im:
        assert im.mode=='RGBA' and im.size==(1254,1254)
        pixels=hashlib.sha256(im.tobytes()).hexdigest()
    selection=ROOT/f'generation/run/{direction}/selection-middle4-side2-20261004.json'
    doc=read(selection);rows=doc if isinstance(doc,list) else doc['frames']
    row=next(x for x in rows if x['frame']==number);before=dict(row)
    row.update(source=source,sourceSha256=expected,generationRecord=source+'.generation.json',
               status='static_reviewed_candidate_recommended_with_limitations',observation=observation,
               latestRevisionEvidence='review/axis-review-20261004/side-repair-review.json')
    for k in ('nativePixelSha256','generationRecordSha256'):
        if k in row:row[k]=pixels if k=='nativePixelSha256' else sha(ROOT/(source+'.generation.json'))
    save(selection,doc)
    independent=ROOT/f'review/grounding-fourframes/{direction}-independent.json'
    report=read(independent);old_report_sha=sha(independent)
    evidence=next(x for x in report['frames'] if x['frame']==number);previous=dict(evidence)
    evidence.update(source=source,sourceSha256=expected,staticObservation=observation,observation=observation,
                    nativePixelSha256=pixels,generationRecordSha256=sha(ROOT/(source+'.generation.json')),
                    revisionReviewer='/root/axis_side_review',revisionEvidence=review.relative_to(ROOT).as_posix())
    report.setdefault('priorRevisions',[]).append({'reportSha256':old_report_sha,'selection':report['selection'],
                                                  'replacedFrame':previous,'reason':'shoe heading continuity follow-up'})
    report['selection']={'path':selection.relative_to(ROOT).as_posix(),'sha256':sha(selection)}
    report['latestRevision']={'atUtc':datetime.now(timezone.utc).isoformat(),'review':review.relative_to(ROOT).as_posix(),
                             'reviewSha256':sha(review),'frame':number,'sourceSha256':expected,'dynamicVerified':False}
    save(independent,report)
    changes.append({'direction':direction,'frame':number,'before':before,'after':row,'independentReport':independent.relative_to(ROOT).as_posix()})
    # Fixed complete canvas and a fixed diagnostic crop; no artwork changes.
    full=Image.new('RGB',(1120,1240),'#eeeae2');lower=Image.new('RGB',(1360,1000),'#eeeae2')
    fd=ImageDraw.Draw(full);ld=ImageDraw.Draw(lower)
    for i,r in enumerate(rows):
        with Image.open(ROOT/r['source']) as im:
            thumb=im.resize((280,280),Image.Resampling.LANCZOS);x=i%4*280;y=i//4*310
            full.paste(thumb,(x,y+27),thumb);fd.text((x+5,y+5),f'{i+1:02d} {Path(r["source"]).stem}',fill='black')
            crop=im.crop((220,770,1100,1254)).resize((340,187),Image.Resampling.LANCZOS);x=i%4*340;y=i//4*250
            lower.paste(crop,(x,y+45),crop);ld.text((x+5,y+5),f'{i+1:02d} {Path(r["source"]).stem}',fill='black')
    name='E-middle4' if direction=='E' else 'W-independent'
    full.save(ROOT/f'review/grounding-fourframes/{name}-contact.jpg',quality=95)
    lower.save(ROOT/f'review/grounding-fourframes/{name}-lower.jpg',quality=95)
save(OUT/'adopted-repairs.json',{'atUtc':datetime.now(timezone.utc).isoformat(),'changes':changes,
                               'timing':'16 x75ms=1200ms; unchanged','dynamicVerified':False,'clientIntegrated':False})
print(json.dumps({'adoptedNativeRepairs':len(changes),'frames':[f'{d}{n:02d}' for d,n,*_ in jobs]}))
