"""Merge selected worker slots and report concrete native source counts."""
import re
import production as p

def sync():
    idx=p.load(p.ROOT/'current-native-map.json')
    workers=[]
    for name in ['r10_c03-worker-map.json','r10_c04-worker-map.json','r10_c04-right-column-worker-map.json']:
        path=p.ROOT/'qa'/name
        if not path.exists():
            continue
        data=p.load(path)
        for tile in ('r10_c03','r10_c04'):
            array=data.get(tile)
            if not isinstance(array,list) or len(array)!=4:
                continue
            target=idx.setdefault(tile,[[None]*4 for _ in range(4)])
            for r,row in enumerate(array):
                for c,stem in enumerate(row):
                    if stem:
                        record=p.ROOT/'native'/f'{stem}.png.generation.json'
                        assert record.exists(),stem
                        target[r][c]=stem
            workers.append({'path':path.as_posix(),'tile':tile,'selectedArray':array})
    p.dump(p.ROOT/'current-native-map.json',idx)
    generated=[]
    coords=set()
    for path in (p.ROOT/'native').glob('*.png.generation.json'):
        try:
            rec=p.load(path)
        except (ValueError,OSError):
            continue
        if rec.get('tool')=='image_gen.imagegen' or rec.get('route')=='builtin':
            generated.append(path.name)
        match=re.fullmatch(r'(r\d{2}_c\d{2}_s\d{2}_\d{2})_v\d{2}\.png\.generation\.json',path.name)
        if match:
            coords.add(match.group(1))
    selected=sum(sum(s is not None for row in a for s in row) for k,a in idx.items() if re.fullmatch(r'r\d{2}_c\d{2}',k) and isinstance(a,list))
    p.update(generatedNativeCount=len(generated),corePositionsGenerated=len(coords),selectedCandidateCoreCount=selected,corePositionsCovered=selected,status='generating_contiguous2x2',currentTile='r10_c03/r10_c04',currentPatch='parallel native sources',nextStep='Finish current native row/column dependencies, compose lower4K candidates, apply recorded cross-row repairs and inspect all2x2 junctions')
    p.dump(p.ROOT/'qa'/'worker-selection-sync.json',{'checkedAtUtc':p.now(),'workers':workers,'selectedCandidateCoreCount':selected,'generatedNativeCount':len(generated),'corePositionsGenerated':len(coords),'formalAccepted':False})
    print({'generatedNativeCount':len(generated),'corePositionsGenerated':len(coords),'selectedCandidateCoreCount':selected})

if __name__=='__main__':
    sync()
