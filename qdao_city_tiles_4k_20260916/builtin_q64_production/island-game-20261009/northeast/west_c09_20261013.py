"""Scoped r04_c09 native map production bookkeeping; mechanical guides and QA only."""
from native_work import *
import sys,argparse
import west_sol_ultra_20261012 as west

TID='r04_c09'
def scoped(ident):
    assert ident.startswith(TID+'_'), 'Outside assigned coordinate'
west.scoped=scoped

def allowed():
    policy=ROOT/'AGENTS.md';allocation=ROOT/'docs/MAP_PARALLEL_SPLIT_20261013.json'
    raw=policy.read_text(encoding='utf-8-sig');split=read(allocation)
    assert '允许继续使用现有内置绘图工具' in raw
    reserved=[t for b in split['batches'] if b.get('status')=='allocated_root_reserved' and b.get('map')=='island-game-20261009' for t in b['tiles']]
    assert TID not in reserved
    return {'readAtUtc':now(),'rootInstructionsSha256':sha(policy),'allocationSha256':sha(allocation),'allocatedElsewhere':reserved,'ownershipCheck':'parent assigned r04_c09 and no current reserved conflict'}

def plan():
    check=allowed();pp=ZONE/f'patch-plan-{TID}.json';sp=ZONE/f'selection-{TID}.json'
    assert not pp.exists() and not sp.exists() and not list((ZONE/'native').glob(TID+'*.png'))
    refs=current_references();layout=Image.open(refs[0]['file']).convert('RGB');assert sha(refs[0]['file'])==refs[0]['sha256'];patches=[]
    for r in range(4):
        for c in range(4):
            ident=f'{TID}_p{r+1:02}_{c+1:02}';x,y=32768+c*1024,12288+r*1024;box=[x-115,y-115,x+1139,y+1139];sb=[v*1254/57344 for v in box]
            p=ZONE/'guides'/f'{ident}.layout-only.png';assert not p.exists()
            layout.transform((1254,1254),Image.Transform.EXTENT,sb,Image.Resampling.BICUBIC).save(p)
            rec={'id':ident,'coreWorldBox':[x,y,x+1024,y+1024],'nativeWorldBox':box,'expectedNativeSize':[1254,1254],'coreCrop':[115,115,1139,1139],'layoutBox':sb,'guide':p.as_posix(),'guideSha256':sha(p),'guideRole':'layout-only enlarged coordinate crop, forbidden as final artwork pixels','operation':'Pillow EXTENT BICUBIC of exact floating box, layout-only','derivedFrom':refs[0],'status':'not_started'}
            write(p.with_suffix('.png.derivation.json'),rec);patches.append(rec)
    write(pp,{'patches':patches,'adjacentNativeOverlapPixels':230,'noFinalArtScaling':True,'scopeCheck':check})
    write(sp,{'tileId':TID,'cores':[[None]*4 for _ in range(4)],'overlays':[],'formalAccepted':False,'updatedAtUtc':now()})
    checkpoint(None,'prepared_layout_guides')
    print(json.dumps({'tile':TID,'nativeCount':0,'preparedLayoutGuides':16,'scopeCheck':check}))

def checkpoint(ident=None,status='native_production',error=None):
    s=read(ZONE/f'selection-{TID}.json');chosen=[i for row in s['cores'] for i in row if i]
    record={'worker':'west_continued','tileId':TID,'updatedAtUtc':now(),'status':status,'selectedCoreCount':len(chosen),'requiredCoreCount':16,'selected':chosen,'currentPatch':ident,'error':error,'actualModel':None,'actualQuality':None,'generationRoute':'builtin image_gen.imagegen','formalAccepted':False}
    write(ZONE/'qa'/'west-c09-checkpoint-20261013.json',record)

def prepare(ident,neighbors):
    scoped(ident);allowed()
    for suffix in ('.anchored-layout-only.png','.native-neighbors.png'):
        assert not (ZONE/'guides'/f'{ident}{suffix}').exists()
    guide(argparse.Namespace(id=ident,neighbor=neighbors,base=None))
    ip=ZONE/'prompts'/f'{ident}.inputs.json';refs=read(ip);target=patch(ident)['coreWorldBox'];roles=[]
    for n in neighbors:
        b=patch(n)['coreWorldBox'];roles.append('UPPER' if b[1]<target[1] else 'RIGHT' if b[0]>target[0] else 'LOWER' if b[1]>target[1] else 'LEFT')
    refs[1]['role']='native neighbor plate left-to-right: '+', '.join(roles) if len(roles)>1 else 'exact native '+roles[0]+' neighbor'
    write(ip,refs)
    prompt=f'''Use case: sketch-to-render. Finish image1 as a native opaque 1254x1254 daylight Daoist Q hand-painted map crop {ident}. The sharp 230px overlap strips on the {' and '.join(roles)} sides are fixed accepted native anchors; preserve their exact positions, contour entries, colors and scale. Image2 shows native neighbors left-to-right in this order: {', '.join(roles)}. Images3-5 are approved full-island layout, materials and hand-painted style; no UI or night content. The blurry interior is exact coordinate layout only, not finished pixels. Repaint it as crisp natural pale gray stone paving, matching the established diagonal rectangular slab grid and soft rounded bevels. Continue every incoming grout line from the anchors at its exact position and direction. Use natural cream and blue-gray mineral mottling and restrained hand-painted details with no repeated ornamental grid. Keep all existing layout silhouettes in the blurry region at their exact coordinates; do not import unrelated buildings or props from the other references. Empty areas remain walkable paving. Preserve daylight and existing soft shadows. Stones and materials must remain continuous across x1024 and y230, without straight material cutoffs, color bands or artificial edges. Do not shift, zoom, crop, reframe, add people, UI, text, borders or margins. Output one opaque 1254x1254 square.'''
    fp=ZONE/'prompts'/f'{ident}.prompt.txt';assert not fp.exists();fp.write_text(prompt,encoding='utf-8')
    print(json.dumps({'id':ident,'refs':[r['file'] for r in refs],'prompt':prompt}))

def preflight(ident):
    scoped(ident);check=allowed();assert not (ZONE/'native'/f'{ident}.png').exists()
    refs=read(ZONE/'prompts'/f'{ident}.inputs.json')
    for ref in refs:assert sha(ref['file'])==ref['sha256']
    write(ZONE/'receipts'/f'{ident}.preflight.json',check);checkpoint(ident,'prepared_for_builtin_generation')
    print(json.dumps({'prompt':(ZONE/'prompts'/f'{ident}.prompt.txt').read_text(encoding='utf-8-sig'),'references':[r['file'] for r in refs],'preflight':check}))

if __name__=='__main__':
    cmd=sys.argv[1]
    if cmd=='plan':plan()
    elif cmd=='prepare':prepare(sys.argv[2],sys.argv[3:])
    elif cmd=='preflight':preflight(sys.argv[2])
    elif cmd=='archive':west.archive(sys.argv[2],sys.argv[3])
    elif cmd=='checks':west.checks(sys.argv[2],sys.argv[3:])
    elif cmd=='accept':west.accept(sys.argv[2],sys.argv[3:]);checkpoint()
