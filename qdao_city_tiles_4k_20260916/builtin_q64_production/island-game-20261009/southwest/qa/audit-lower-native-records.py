from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from production import ROOT,load,dump,hashfile,now
from PIL import Image

results=[]
for path in sorted((ROOT/'native').glob('r10_*.png.generation.json')):
    rec=load(path)
    if rec.get('tool')!='image_gen.imagegen': continue
    art=Path(rec['file']); issues=[]
    if not art.exists() or hashfile(art)!=rec['sha256']: issues.append('source hash mismatch or missing')
    with Image.open(art) as im:
        if list(im.size)!=[rec['width'],rec['height']] or im.size!=(1254,1254): issues.append('native dimensions mismatch')
    if rec.get('actualModel') is not None or rec.get('actualQuality') is not None: issues.append('unverified actual model/quality claim')
    if not Path(rec['prompt']).exists(): issues.append('prompt missing')
    for ev in rec['evidence']:
        if not Path(ev['path']).exists(): issues.append('receipt missing')
    refchecks=[]
    for ref in rec['references']:
        rp=Path(ref['path']); ok=rp.exists() and hashfile(rp)==ref['sha256']
        refchecks.append({'path':str(rp),'matchesRecordedHash':ok})
        if not ok: issues.append('reference changed: '+str(rp))
    results.append({'source':str(art),'sourceSha256':rec['sha256'],'issues':issues,'referenceChecks':refchecks})
report={'checkedAtUtc':now(),'scope':'snapshot of r10 builtin native generation records; this is provenance verification, not visual acceptance','count':len(results),'allPass':not any(x['issues'] for x in results),'results':results}
dump(ROOT/'qa/lower-native-records-audit.json',report)
print({'count':len(results),'allPass':report['allPass'],'issues':[x for x in results if x['issues']]})
