import json, hashlib
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
SPECS={'run':(['N','NE','E','SE','S','SW','W','NW'],16,None),'hit':(['E','W'],6,40),'attack':(['E','W'],12,30),'cast':(['E','W'],16,45)}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
review_path=ROOT/'review.json'
reviews=json.loads(review_path.read_text(encoding='utf-8-sig')) if review_path.exists() else {}
timing_path=ROOT/'run-timing.json'
run_timing=json.loads(timing_path.read_text(encoding='utf-8'))
run_phases={d:json.loads((ROOT/'run'/d/'grounding-review.json').read_text(encoding='utf-8'))['frames'] for d in SPECS['run'][0] if (ROOT/'run'/d/'grounding-review.json').exists()}
items=[]; totals={}
for action,(dirs,count,ms) in SPECS.items():
    present=0; passed=0
    for direction in dirs:
        for i in range(1,count+1):
            key=f'{action}/{direction}/{i:02d}'; p=ROOT/(key+'.png'); meta=Path(str(p)+'.generation.json')
            duration=run_timing['directions'][direction]['durationsMs'][i-1] if action=='run' else ms
            row={'slot':key,'action':action,'direction':direction,'frame':i,'durationMs':duration,'path':p.relative_to(ROOT).as_posix() if p.exists() else None,'status':'missing','clientStatus':'not_integrated'}
            if action=='run' and direction in run_phases:
                phase=run_phases[direction][i-1]
                row['phase']=phase.get('phase',phase.get('observedPhase'))
                row['phaseReview']=f'run/{direction}/grounding-review.json'
            if p.exists():
                im=Image.open(p); h=sha(p); rec=json.loads(meta.read_text(encoding='utf-8-sig')) if meta.exists() else {}
                check=reviews.get(key,{})
                ok=check.get('sha256')==h and check.get('visualStatus')=='passed'
                row.update({'sha256':h,'width':im.width,'height':im.height,'mode':im.mode,'alphaExtrema':im.getchannel('A').getextrema() if im.mode=='RGBA' else None,'generationRecord':meta.relative_to(ROOT).as_posix() if meta.exists() else None,'status':'passed' if ok else 'pending_review','review':check if check.get('sha256')==h else None,'technicalExportValid':im.size==(1024,1024) and im.mode=='RGBA','nativeRecord':rec.get('derivedFrom')})
                row['registrationApplied']=rec.get('registrationTransform',{}).get('outputSha256')==h
                present+=1;passed+=int(ok)
            items.append(row)
    totals[action]={'expected':len(dirs)*count,'exported':present,'visualPassed':passed,'clientIntegrated':0}
manifest={'character':'14_short_hair_snow_summoner_girl','generatedAt':datetime.now(timezone.utc).isoformat(),'totals':totals,'expected':196,'exported':sum(v['exported'] for v in totals.values()),'visualPassed':sum(v['visualPassed'] for v in totals.values()),'clientStatus':'not_integrated','anchor':{'canvas':[1024,1024],'virtualRoot':[512,942],'globalScale':0.8,'registeredFrames':sum(bool(f.get('registrationApplied')) for f in items),'status':'complete' if all(f.get('registrationApplied') for f in items) else 'partially_applied','noPerFrameSoleAlignment':True,'noPerFrameBBoxFitting':True},'events':{'hit':{'impactFrame':2,'peakFrame':3},'attack':{'contactFrame':5},'cast':{'releaseFrame':9}},'frames':items}
manifest['runTiming']=run_timing
manifest['anchor']['directRegisteredCanvasRedraws']=sum(json.loads((ROOT/f['generationRecord']).read_text(encoding='utf-8-sig')).get('registrationTransform',{}).get('method')=='direct_registered_canvas_redraw' for f in items if f.get('generationRecord'))
manifest['anchor']['globalScaleMeaning']='Original identity normalization is 0.8; direct edits of an already registered canvas preserve it and apply no second scale. See per-frame records.'
(ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
template=(ROOT/'tools/preview_template.html').read_text(encoding='utf-8')
(ROOT/'index.html').write_text(template.replace('__MANIFEST__',json.dumps(manifest,ensure_ascii=False).replace('</','<\\/')),encoding='utf-8')
print(json.dumps(manifest['totals'],ensure_ascii=False))

