"""Read-only provenance replay; only writes this QA report."""
from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
checks=[];issues=[]
for f in sorted((ROOT/'native').glob('*.png.generation.json')):
    r=load(f)
    if r.get('route')!='builtin':continue
    im=Path(r['file']); rec={'stem':im.stem,'dimensions':None,'imageHashMatches':False,'promptExists':Path(r['prompt']).exists(),'recordModelQualityUnconfirmed':r.get('actualModel') is None and r.get('actualQuality') is None,'submittedModelQualityUnspecified':r['submittedParameters'].get('model') is None and r['submittedParameters'].get('quality') is None,'references':[],'receipts':[]}
    if im.exists():
        with Image.open(im) as pic:pic.load();rec['dimensions']=list(pic.size)
        rec['imageHashMatches']=sha(im)==r['sha256']
    for ref in r['references']:
        p=Path(ref['path']);item={'path':p.as_posix(),'exists':p.exists(),'hashMatches':p.exists() and sha(p)==ref['sha256']}
        rec['references'].append(item)
    for e in r['evidence']:
        p=Path(e['path']);item={'path':p.as_posix(),'exists':p.exists()}
        if p.exists():
            receipt=load(p);item['outputPathPresentInReceipt']=r['sourceToolPath'].replace('\\','/') in json.dumps(receipt,ensure_ascii=False).replace('\\\\','/');item['actualModelQualityUnconfirmed']=receipt.get('actualModel') is None and receipt.get('actualQuality') is None
        rec['receipts'].append(item)
    rec['sourceToolPathExists']=Path(r['sourceToolPath']).exists()
    fail=[]
    if not rec['imageHashMatches']:fail.append('native_image_hash_or_existence')
    if rec['dimensions']!=[r['width'],r['height']]:fail.append('native_dimensions')
    if not rec['promptExists']:fail.append('prompt_missing')
    if any(not a['hashMatches'] for a in rec['references']):fail.append('reference_missing_or_mutated')
    if any(not a['exists'] for a in rec['receipts']):fail.append('receipt_missing')
    if not rec['recordModelQualityUnconfirmed'] or not rec['submittedModelQualityUnspecified']:fail.append('unexpected_model_quality_claim')
    rec['failures']=fail
    if fail:issues.append({'stem':im.stem,'failures':fail})
    checks.append(rec)
index=load(ROOT/'current-native-map.json');selected=[]
for tile,rows in index.items():
    if not (tile.startswith('r') and isinstance(rows,list)):continue
    for row in rows:
        for stem in row:
            if stem:
                f=ROOT/'native'/f'{stem}.png';r=load(str(f)+'.generation.json')
                selected.append({'stem':stem,'hashMatches':f.exists() and sha(f)==r['sha256'],'status':r.get('status'),'nativeBox':r['coordinates']['nativeGlobalBox'],'sourceRoute':r.get('route')})
out={'checkedAtUtc':datetime.now(timezone.utc).isoformat(),'operation':'read-only all builtin image records, native hash/dimensions, prompt/receipt existence, reference hashes, selected source checks','generatedRecordCount':len(checks),'selectedCoreCount':len(selected),'issues':issues,'generatedRecords':checks,'selectedSources':selected,'sharedConfigExists':Path('D:/work/image/config/image-generation.json').exists(),'limits':['Does not prove visual quality or final4K external acceptance','Derived source lineage is separately represented by assembly records and source-ID replay','Missing original tool cache is informational when copied native hash is valid'],'formalAccepted':False}
dest=ROOT/'qa/capacity-provenance-audit.json';dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'checked':len(checks),'selected':len(selected),'issues':issues,'missingOrChangedReferences':[{'stem':x['stem'],'refs':[r for r in x['references'] if not r['hashMatches']]} for x in checks if any(not r['hashMatches'] for r in x['references'])],'report':str(dest)},ensure_ascii=False))

