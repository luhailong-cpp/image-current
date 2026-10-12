from pathlib import Path
import sys,json,shutil
from PIL import Image
T=Path(__file__).resolve().parent
sys.path.insert(0,str(T.parent))
import tile_native_workflow as w
VERSION=sys.argv[4] if len(sys.argv)>4 else 'v1'
w.CONFIG_PATH = T/'host-managed-image-config-20261012.json'
if not w.CONFIG_PATH.exists():
    w.write(w.CONFIG_PATH,dict(schemaVersion=1,route='builtin',tool='image_gen__imagegen',submittedParameters=dict(model=None,quality=None),actualModel=None,actualQuality=None,reason='Host-managed built-in tool has no model or quality selector and returns no verified model/quality metadata',legacyConfigMissingAtIngest='D:/work/image/config/image-generation.json'))

def prepare(pid,notes):
    row,col=int(pid[1]),int(pid[2]);tile=T.name;tr,tc=w.tile_indices(tile)
    sources=[]
    if row==1:
        nt=f'r{tr-1:02d}_c{tc:02d}';ns=w.read(T.parent/nt/'selected-patches.json');np=f'p4{col}'
        sources.append(f'{nt}:{np}:{ns["patches"][np]}')
    else:
        ns=w.read(T/'selected-patches.json');np=f'p{row-1}{col}';sources.append(f'{tile}:{np}:{ns["patches"][np]}')
    if col>1:
        ns=w.read(T/'selected-patches.json');np=f'p{row}{col-1}';sources.append(f'{tile}:{np}:{ns["patches"][np]}')
    if not (T/'left-boundary-sources.json').exists():w.refresh_left(tile)
    result=w.condition(tile,pid,sources)
    source=Path(result['file']);snap=T/'input-snapshots'/f'{pid}-{VERSION}-input-20261012.png';snap.parent.mkdir(exist_ok=True);assert not snap.exists();shutil.copy2(source,snap);shutil.copy2(source.with_suffix('.png.derivation.json'),snap.with_suffix('.png.derivation.json'))
    prompt='Use case: precise-object-edit. Finish ONLY the blurred layout region of Image1 as native 1254 by 1254 square game map artwork with exact original crop and scale. Sharp 230-pixel neighbor strips show the actual selected northern and western artwork: preserve their silhouettes, all beam or rock endpoints, water color and texture scale, and continue those shapes smoothly. '+notes+' Image2 is authoritative full-map layout A only; Image3 bright daylight material style B; Image4 PRIMARY approved rounded Q Chinese Daoist painterly style C. Soft bevels, fine readable material detail, clear bright daylight, clean saturated turquoise sea with delicate ripple and foam detail. Redraw all blurred pixels at native detail; no enlargement of the overview. Preserve exactly the supplied global layout; no new islands, buildings, posts, beams, boats or other objects absent from Image1. No people, NPCs, birds, animals, text, UI, icons, logos, labels, border or watermark. No artificial strip boundary, abrupt material seam or geometry shift.'
    refs=[str(snap)]+[r['path'] for r in w.approved_refs()]
    req=dict(prompt=prompt,referenced_image_paths=refs,transparent_background=False,submittedParameters=dict(model=None,quality=None),referenceRoles={'1':'edit target; actual native neighbor strips plus blurred layout to redraw','2':'authoritative layout A only','3':'daylight materials style B','4':'primary painterly style C'})
    (T/f'{pid}-{VERSION}.prompt.txt').write_text(prompt,encoding='utf-8');w.write(T/f'{pid}-{VERSION}.request.json',req)
    print(json.dumps(req))

def ingest(pid,source):
    source=Path(source);raw=T/'raw-sources'/f'{pid}-{VERSION}-source-20261012.png';raw.parent.mkdir(exist_ok=True)
    if raw.exists():assert w.sha(raw)==w.sha(source)
    else:shutil.copy2(source,raw)
    rp=T/f'{pid}-{VERSION}.receipt.json'
    receipt=w.read(rp) if rp.exists() else dict(receivedAt=w.now(),sourcePath=str(source),rawSourceCopy=str(raw),rawSourceSha256=w.sha(raw),route='builtin',tool='image_gen__imagegen',actualModel=None,actualQuality=None,result='generated image returned')
    assert receipt['sourcePath']==str(source)
    w.write(rp,receipt)
    r=w.ingest(T.name,pid,VERSION,str(source));assert r['nativeDimensions']==[1254,1254]
    p=T/'selected-patches.json';s=w.read(p) if p.exists() else dict(tile=T.name,patches={})
    s['patches'][pid]=f'native/{pid}-{VERSION}.png';s.update(updatedAt=w.now(),status='native_production_and_internal_QA',internalReady=False,formalAccepted=False);w.write(p,s)
    w.write(T/'progress-20261012.json',dict(tile=T.name,updatedAt=w.now(),selectedNativeCount=len(s['patches']),internalReady=False,formalAccepted=False,gitTouched=False))
    print(json.dumps(dict(**r,selectedPositions=len(s['patches']))))

def edit(pid,notes):
    selection=w.read(T/'selected-patches.json');source=T/selection['patches'][pid]
    snap=T/'input-snapshots'/f'{pid}-{VERSION}-input-20261012.png';assert not snap.exists();shutil.copy2(source,snap)
    w.write(snap.with_suffix('.png.derivation.json'),dict(operation='exact selected native edit target',source=str(source),sourceSha256=w.sha(source),resamplingApplied=False,dimensions=[1254,1254]))
    prompt='Use case: precise-object-edit. Repair Image1 as native 1254 by 1254 square game map artwork, original crop and exact pixel scale. '+notes+' Preserve every outermost 115-pixel overlap border exactly and every silhouette entering an image edge. Image2 is authoritative full-map layout A only; Image3 daylight materials style B; Image4 PRIMARY approved rounded Q Chinese Daoist painterly style C. Bright daylight, fine readable softly bevelled rounded stone and delicate turquoise water caustics, matching the existing artwork. No new objects, people, creatures, text, UI, labels, border or watermark. No rectangular adoption boundary or abrupt geometry splice.'
    refs=[str(snap)]+[r['path'] for r in w.approved_refs()]
    req=dict(prompt=prompt,referenced_image_paths=refs,transparent_background=False,submittedParameters=dict(model=None,quality=None),referenceRoles={'1':'edit target; exact selected native patch','2':'authoritative layout A only','3':'daylight materials style B','4':'primary painterly style C'})
    (T/f'{pid}-{VERSION}.prompt.txt').write_text(prompt,encoding='utf-8');w.write(T/f'{pid}-{VERSION}.request.json',req)
    print(json.dumps(req))

if sys.argv[1]=='prepare':prepare(sys.argv[2],sys.argv[3])
elif sys.argv[1]=='ingest':ingest(sys.argv[2],sys.argv[3])
elif sys.argv[1]=='edit':edit(sys.argv[2],sys.argv[3])
