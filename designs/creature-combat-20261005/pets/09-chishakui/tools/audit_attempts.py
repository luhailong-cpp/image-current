from pathlib import Path
import json,hashlib,datetime
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    adopted={}
    for p in (ROOT/'runtime').rglob('*.generation.json'):
        g=json.loads(p.read_text(encoding='utf-8-sig'))
        adopted[str(Path(g['derivedFrom']['path'])).lower()]=g['file']
    batch=json.loads((ROOT/'runtime/hit/E/01.png.generation.json').read_text(encoding='utf-8'))['configSnapshot']
    attempts=[]
    cleanup=json.loads((ROOT/'cleanup.json').read_text(encoding='utf-8')) if (ROOT/'cleanup.json').exists() else {}
    removed={str(Path(x['path'])).lower():x for x in cleanup.get('removed',[])}
    for rp in sorted((ROOT/'records').glob('*.receipt.json')):
        r=json.loads(rp.read_text(encoding='utf-8-sig'));src=r.get('sourcePath')
        if not src:continue
        p=Path(src);exists=p.is_file();native=r.get('native')
        if exists:
            with Image.open(p) as im:native={'width':im.width,'height':im.height,'mode':im.mode,'format':im.format}
        record={'receipt':rp.relative_to(ROOT).as_posix(),'sourcePath':src,'sourceSha256':sha(p) if exists else r.get('sourceSha256',r.get('sha256')),'native':native,'startedAt':r.get('startedAt'),'completedAt':r.get('completedAt'),'tool':'image_gen.imagegen','route':'builtin','configSnapshot':r.get('configSnapshot',batch),'configEvidence':'batch config was fixed; first-frame snapshot runtime/hit/E/01.png.generation.json','submittedParameters':{'model':None,'quality':None,'transparent_background':True,'references':r.get('references'),'promptFile':r.get('promptFile')},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host tool exposes/returns no model or quality identifier.','toolOutputHint':r.get('output_hint'),'adoptedFinal':adopted.get(str(p).lower()),'sourceExistedAtAudit':exists,'recordedVisualStatus':r.get('visualStatus',r.get('status'))}
        record['referenceEvidence']=[{'path':x,'sha256':sha(Path(x)) if Path(x).is_file() else removed.get(str(Path(x)).lower(),{}).get('sha256'),'hashScope':'file-at-final-audit or pre-cleanup hash, not necessarily original submitted bytes','historicalInputRemovedPerRetentionPolicy':str(Path(x)).lower() in removed,'role':'See exact image numbering in prompt'} for x in r.get('references',[])]
        attempts.append(record)
    out={'auditedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'entries':attempts,'note':'Repeated receipt entries may refer to the same attempt. Distinct source SHA identifies images. Native source lives in host generated-images cache outside the sole writable project directory; no native image backup is included in this package.'}
    (ROOT/'all-generation-attempts.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'receiptEntries':len(attempts),'uniqueGeneratedImages':len(set(x['sourceSha256'] for x in attempts if x['sourceSha256']))}))
if __name__=='__main__':main()
