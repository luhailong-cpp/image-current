"""Read selected native patches; write only QA derivatives beside this script.

Run without arguments for r03_c10 or with --all for the four assigned tiles.
No source, selection, workflow, progress or acceptance fields are modified.
"""
from pathlib import Path
from PIL import Image
import argparse, hashlib, json
from datetime import datetime, timezone

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
TILES = ['r03_c10','r03_c11','r04_c10','r04_c11']

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def save(im, path, artifacts, kind):
    assert OUT in path.resolve().parents
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path)
    artifacts.append({'file':str(path),'dimensions':list(im.size),'kind':kind,'sha256':sha(path)})

def audit(tile):
    dest = OUT / tile
    patches, source, artifacts = {}, [], []
    for r in range(1,5):
        for c in range(1,5):
            selpath = ROOT / tile / 'records' / f'p{r}{c}.selection.json'
            if not selpath.exists():
                continue
            sel=read(selpath)
            rec=read(sel['generationRecord'])
            with Image.open(sel['file']) as native:
                assert native.size == tuple(rec['nativeDimensions'])
                core=native.convert('RGB').crop(tuple(rec['coreCropNative']))
                assert core.size == (1024,1024)
                patches[r,c]=core
            source.append({'patch':f'p{r}{c}','file':sel['file'],'sha256':sha(sel['file']),'nativeDimensions':rec['nativeDimensions'],'coreCropNative':rec['coreCropNative']})
    for r in range(1,5):
        if all((r,c) in patches for c in range(1,5)):
            strip=Image.new('RGB',(4096,1024))
            for c in range(1,5):
                strip.paste(patches[r,c],((c-1)*1024,0))
            save(strip,dest/f'row{r}-4096x1024-native.png',artifacts,'native unresampled row')
            save(strip.resize((2048,512)),dest/f'row{r}-preview-only.png',artifacts,'resized inspection preview only')
    for (r,c),im in patches.items():
        if (r,c+1) in patches:
            seam=Image.new('RGB',(512,1024))
            seam.paste(im.crop((768,0,1024,1024)),(0,0))
            seam.paste(patches[r,c+1].crop((0,0,256,1024)),(256,0))
            save(seam,dest/f'vertical-p{r}{c}-p{r}{c+1}-native.png',artifacts,'native seam; boundary x256')
        if (r+1,c) in patches:
            seam=Image.new('RGB',(1024,512))
            seam.paste(im.crop((0,768,1024,1024)),(0,0))
            seam.paste(patches[r+1,c].crop((0,0,1024,256)),(0,256))
            save(seam,dest/f'horizontal-p{r}{c}-p{r+1}{c}-native.png',artifacts,'native seam; boundary y256')
    if len(patches)==16:
        full=Image.new('RGB',(4096,4096))
        for (r,c),im in patches.items():
            full.paste(im,((c-1)*1024,(r-1)*1024))
        save(full,dest/'complete-tile-4096-qa-only.png',artifacts,'native unresampled full tile; not acceptance')
    return {'tile':tile,'selectedCoreCount':len(patches),'sources':source,'artifacts':artifacts,'formalAcceptance':False}

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--all',action='store_true')
    args=parser.parse_args()
    report={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'purpose':'read-only source QA; no acceptance','tiles':[audit(t) for t in (TILES if args.all else TILES[:1])]}
    (OUT/'qa-manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'manifest':str(OUT/'qa-manifest.json'),'tiles':[{'tile':t['tile'],'cores':t['selectedCoreCount'],'qaFiles':len(t['artifacts'])} for t in report['tiles']]}))
