"""Snapshot existing map pixels and concise progress; never creates artwork."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, shutil, os, uuid, argparse
from PIL import Image

ZONE = Path(__file__).resolve().parent
TILES = ['r13_c13', 'r13_c14', 'r14_c13', 'r14_c14']
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p, data):
    p=Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    tmp=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    os.replace(tmp,p)
def evidence(p):
    p=Path(p)
    with Image.open(p) as im: size=list(im.size)
    return {'path':str(p),'sha256':sha(p),'size':size}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--update', action='store_true'); args=ap.parse_args()
    now=datetime.now(timezone.utc); stamp=now.strftime('%Y%m%dT%H%M%S')
    out=ZONE/'review-notes'/('four-core-snapshot-'+stamp); out.mkdir(parents=True)
    images=[]; tiles=[]
    for name in TILES:
        td=ZONE/name; mapping=read(td/'active-native-map.json')
        if name=='r13_c13':
            candidate=td/'candidate'/'r13_c13-4k-candidate-repaired.png'
            context=td/'candidate'/'r13_c13-context-4326-repaired.png'
            assert sha(candidate)=='db5f956694c700b16094eb532ad9097e8a54f4a19d14797325f6fbd0ca18971f'
            p={'internalArtQA':'passed','externalNeighborSeamQA':'pending','nextStep':'Keep core immutable; review new neighboring boundaries.'}
            generated=29
        else:
            p=read(td/'progress.json'); candidate=Path(p['candidate']); context=Path(p['context'])
            generated=sum(1 for f in td.rglob('*generation.json') if f.is_file())
        with Image.open(candidate) as im:
            assert im.size==(4096,4096); core=im.convert('RGB')
        with Image.open(context) as im:
            assert im.size==(4326,4326)
            assert im.convert('RGB').crop((115,115,4211,4211)).tobytes()==core.tobytes(),name+' context core differs'
        images.append(core)
        tiles.append({'tile':name,'activeNativeCount':len(mapping),'recordedGeneratedNativeCount':generated,
                      'candidate':evidence(candidate),'context':evidence(context),
                      'internalArtQA':p.get('internalArtQA'),'internalSeamQA':p.get('internalSeamQA'),
                      'externalNeighborSeamQA':p.get('externalNeighborSeamQA'),'formalAccepted':False,
                      'nextStep':p.get('nextStep'),'tileProgress':str(td/'progress.json') if (td/'progress.json').exists() else None})
    preview=Image.new('RGB',(2048,2048))
    for k,im in enumerate(images): preview.paste(im.resize((1024,1024),Image.Resampling.LANCZOS),((k%2)*1024,(k//2)*1024))
    preview_path=out/'four-core-preview-only.png'; preview.save(preview_path)
    bridges=[]
    for label,a,b,vertical in [('north-west-east',0,1,True),('south-west-east',2,3,True),('west-north-south',0,2,False),('east-north-south',1,3,False)]:
        for pos in range(0,4096,1024):
            if vertical:
                im=Image.new('RGB',(768,1024)); im.paste(images[a].crop((3712,pos,4096,pos+1024)),(0,0)); im.paste(images[b].crop((0,pos,384,pos+1024)),(384,0))
            else:
                im=Image.new('RGB',(1024,768)); im.paste(images[a].crop((pos,3712,pos+1024,4096)),(0,0)); im.paste(images[b].crop((pos,0,pos+1024,384)),(0,384))
            path=out/(label+'-'+str(pos)+'-100pct.png'); im.save(path); bridges.append(str(path))
    corner=Image.new('RGB',(900,900))
    for im,box,dest in [(images[0],(3646,3646,4096,4096),(0,0)),(images[1],(0,3646,450,4096),(450,0)),(images[2],(3646,0,4096,450),(0,450)),(images[3],(0,0,450,450),(450,450))]: corner.paste(im.crop(box),dest)
    corner.save(out/'four-core-corner-100pct.png')
    joint_generated=sum(1 for folder in ZONE.glob('corner-repair-*') for f in folder.rglob('*generation.json') if f.is_file())
    manifest={'snapshotAtUtc':now.isoformat(),'tiles':tiles,'jointRepairNativeCount':joint_generated,'preview':str(preview_path),'previewOnlyResized':True,
              'artworkChanged':False,'bridgeImagesUnscaled':bridges,'cornerUnscaled':str(out/'four-core-corner-100pct.png'),
              'acceptance':'Snapshot only; no QA pass inferred from assembly or preview.'}
    write(out/'manifest.json',manifest)
    if args.update:
        pp=ZONE/'progress.json'; archive=out/'previous-progress.json'; shutil.copyfile(pp,archive)
        progress={'schemaVersion':2,'zone':'southeast','updatedAt':now.isoformat(),'status':'four_candidates_native_seam_repairs_in_progress',
                  'plannedTileCount':64,'startedTileCount':4,'notStartedTileCount':60,
                  'generatedNativeCount':sum(t['recordedGeneratedNativeCount'] for t in tiles)+joint_generated,
                  'jointRepairNativeCount':joint_generated,
                  'activeNativePatchCount':sum(t['activeNativeCount'] for t in tiles),'complete4kCandidateCount':4,
                  'fullyCovered4kCount':4,'missingFullyCoveredTileCount':60,'internalPassed4kCount':1,
                  'internalPassCountBasis':'Only the immutable r13_c13 full-art pass is counted; newer internal-seam-only passes exclude pending outer transitions.',
                  'externalPassed4kCount':0,'formalAcceptedCount':0,'missingFormalTileCount':64,
                  'underlyingTaskComplete':False,'builtinOnly':True,'paidApiAllowed':False,'actualModel':None,'actualQuality':None,
                  'artCanvasPixels':[65536,65536],'formalTilePixels':[4096,4096],'resizeFinalArtAllowed':False,
                  'tiles':tiles,'latestReviewSnapshot':str(out/'manifest.json'),'preview':str(preview_path),
                  'historicalProgressArchive':str(archive),'generationCountBasis':'Recorded successful native versions including superseded or rejected outputs; not an art acceptance count.',
                  'nextStep':'Finish native repairs on r13_c14 west, r14_c13 north and r14_c14 internal grout; review the complete 2x2 shared edges and corner, then extend only from verified core boundaries.'}
        write(pp,progress)
    print(json.dumps({'snapshot':str(out),'preview':str(preview_path),'generatedNativeCount':sum(t['recordedGeneratedNativeCount'] for t in tiles),'activeNativeCount':sum(t['activeNativeCount'] for t in tiles),'candidateCount':4},ensure_ascii=False))
if __name__=='__main__': main()
