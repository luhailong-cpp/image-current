"""Source/reference integrity and exact APNG time checks. Does not assert visual playback."""
from pathlib import Path
import json,hashlib,datetime
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    m=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'));v=json.loads((ROOT/'validation.json').read_text(encoding='utf-8'))
    errors=[];sourceindex=[];previewchecks=[]
    cleanup=json.loads((ROOT/'cleanup.json').read_text(encoding='utf-8')) if (ROOT/'cleanup.json').exists() else {}
    removed={str(Path(x['path'])).lower():x for x in cleanup.get('removed',[])}
    for e in m['frames']:
        p=ROOT/e['generationRecord'];g=json.loads(p.read_text(encoding='utf-8'));rp=ROOT/g['evidence']['receipt'];receipt=json.loads(rp.read_text(encoding='utf-8'))
        prompt=ROOT/g['prompt']
        if not prompt.is_file():errors.append({'file':e['file'],'missingPrompt':str(prompt)})
        evidence=[]
        for ref in g['references']:
            refp=Path(ref)
            role='primary confirmed painting/material style' if '01-character-ui-no-affinity' in ref else 'original E identity and right-hand anatomy' if '09-chishakui-E.png' in ref else 'original W rear identity (hand corrected to match E)' if '09-chishakui-W.png' in ref else 'generated pose continuity / exact prompt role'
            removal=removed.get(str(refp).lower())
            evidence.append({'path':str(refp),'role':role,'existsAtAudit':refp.is_file(),'sha256':sha(refp) if refp.is_file() else removal.get('sha256') if removal else None,'hashScope':'file-at-final-audit, not necessarily original submitted bytes; consult receipt and superseded records for replaced runtime inputs','historicalInputRemovedPerRetentionPolicy':bool(removal)})
            if not refp.is_file() and not removal:errors.append({'file':e['file'],'missingReference':str(refp)})
        g['referenceEvidence']=evidence
        g['actualModel']=None;g['actualQuality']=None
        p.write_text(json.dumps(g,ensure_ascii=False,indent=2),encoding='utf-8')
        sourceindex.append({'file':e['file'],'generationRecord':e['generationRecord'],'receipt':g['evidence']['receipt'],'prompt':g['prompt'],'sha256':e['sha256'],'native':g['native'],'targetModel':g['configSnapshot']['model'],'targetQuality':g['configSnapshot']['quality'],'actualModel':None,'actualQuality':None})
    for group in m['groups']:
        for label,mult in [('normal',1),('slow025',4)]:
            p=ROOT/'preview'/f'{group["action"]}-{group["direction"]}-{label}.png'
            if not p.is_file():continue
            with Image.open(p) as im:
                times=[]
                for i in range(im.n_frames):im.seek(i);times.append(im.info.get('duration'))
                passed=im.n_frames==group['count'] and all(t==group['durationMs']*mult for t in times)
                previewchecks.append({'file':p.relative_to(ROOT).as_posix(),'frames':im.n_frames,'durationMs':times,'totalMs':sum(times),'expectedTotalMs':group['totalMs']*mult,'passed':passed})
                if not passed:errors.append({'preview':str(p),'type':'frame-count-or-duration'})
    v['sourceIntegrityIssues']=errors;v['previewTimingChecks']=previewchecks
    v['technicalPassed']=v['technicalPassed'] and not errors and len(previewchecks)==12
    v['visualPlayback']={'status':'not-verified','reason':'Browser security policy rejected file: URL; no workaround attempted. APNG timeline and frame files are checked separately.'}
    v['clientIntegration']='not-performed'
    (ROOT/'validation.json').write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'generation-index.json').write_text(json.dumps(sourceindex,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'frames':len(sourceindex),'technicalPassed':v['technicalPassed'],'sourceIssues':errors,'previewTimingChecks':len(previewchecks)},ensure_ascii=False))
if __name__=='__main__':main()
