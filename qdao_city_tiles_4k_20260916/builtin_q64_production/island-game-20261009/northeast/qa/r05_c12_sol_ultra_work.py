"""Mechanical native crop/paste and local evidence only; no drawn/resampled art."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from native_work import *

TID='r05_c12'; OX=45056; OY=16384
def save(im,p):
    p=Path(p)
    if p.exists(): raise RuntimeError('Refusing to overwrite PNG: '+str(p))
    im.save(p)
def mosaic():
    s=read(ZONE/f'selection-{TID}.json'); im=Image.new('RGB',(4096,4096)); sources=[]
    for r,row in enumerate(s['cores']):
        for c,ident in enumerate(row):
            p=ZONE/'native'/f'{ident}.png'; rec=read(p.with_suffix('.png.generation.json')); src=Image.open(p)
            assert src.size==(1254,1254) and sha(p)==rec['sha256']
            im.paste(src.crop(tuple(rec['coreCrop'])),(c*1024,r*1024))
            sources.append({'id':ident,'file':p.as_posix(),'sha256':sha(p),'coreCrop':rec['coreCrop'],'tileLocalPaste':[c*1024,r*1024]})
    overlays=[]
    for ident in s['overlays']:
        q=read(ZONE/'qa'/f'{ident}.overlay.json'); assert q['review'].startswith('passed_') and sha(q['source'])==q['sha256']
        im.paste(Image.open(q['source']).crop(tuple(q['coreCrop'])),tuple(q['tileLocalPaste'])); overlays.append(q)
    return im,sources,overlays

def prepare(ident,y):
    x=1536; im,sources,overlays=mosaic(); box=[x-115,y-115,x+1139,y+1139]
    p=ZONE/'guides'/f'{ident}.png'; save(im.crop(tuple(box)),p)
    d={'operation':'exact selected native core assembly and passed overlays, unscaled crop for seam repair','sources':sources,'existingOverlays':overlays,'tileLocalBox':box,'nativeWorldBox':[OX+box[0],OY+box[1],OX+box[2],OY+box[3]],'coreWorldBox':[OX+x,OY+y,OX+x+1024,OY+y+1024],'coreCrop':[115,115,1139,1139],'finalArt':False}
    write(p.with_suffix('.png.derivation.json'),d)
    ns=['r05_c12_p03_02','r05_c12_p03_03_v2'] if y<2500 else ['r05_c12_p04_02_v2','r05_c12_p04_03']
    plate=Image.new('RGB',(2508,1254)); anchors=[]
    for i,n in enumerate(ns):
        src=ZONE/'native'/f'{n}.png'; plate.paste(Image.open(src),(i*1254,0)); anchors.append({'file':src.as_posix(),'sha256':sha(src),'role':'unchanged original native stair geometry'})
    pp=ZONE/'guides'/f'{ident}.native-neighbors.png'; save(plate,pp); write(pp.with_suffix('.png.derivation.json'),{'operation':'exact native neighbor plate, no resizing','sources':anchors,'finalArt':False})
    refs=[{'file':p.as_posix(),'sha256':sha(p),'role':'edit target, exact current native mosaic. Repair stair seam only while preserving surrounding scene and outer115px context'},{'file':pp.as_posix(),'sha256':sha(pp),'role':'unaltered adjacent native cores, left-to-right original west then east; preserve context','sources':anchors},*current_references()]
    write(ZONE/'prompts'/f'{ident}.inputs.json',refs)
    prompt=f'''Use case: precise-object-edit
Asset type: native seamless Q-style Daoist daylight game map repair, square1254x1254.
Primary request: Edit Image1 at its exact original composition and pixel dimensions. Mend the narrow vertical stair/foundation discontinuity near x512..627 of Image1. The pasted old anchor begins at x512; that artificial cut must disappear. Continue each step's sloping front edge, tread plane and pale gray stone riser into the geometry already visible on the right. Keep the original number, spacing, perspective and direction of all steps. Upper cream foundation behind the red wooden door must meet continuously. Produce coherent fitted stone blocks without changing any architecture position or size.
Input images: Image1 exact current native mosaic edit target; Image2 exact native neighboring west/east cores, context only; Image3 sole approved full-map layout, position authority only; Image4 approved stone and festival material style only; Image5 approved user Daoist Q painting style only, ignore UI and night.
Style/medium: same existing crisp painterly Q-style game art, natural irregular pale gray/cyan stone, subtle facets, clear warm daylight, original soft shadows.
Constraints: Preserve original camera, scale, lighting, materials, all doors, red columns, cream walls, stone ball, existing shrubs, ornament and location. Preserve the full outer115pixel context of Image1 exactly so its central1024pixel core can be pasted into the map without a new edge. Concentrate corrections around x512..627 and join smoothly to intact slopes on both sides. Do not redesign the staircase or introduce a landing, new step, new pillar, new plants or decorations. No blur, no seam stripe, no sharp square repair boundary, no extra objects, no characters, no UI, no labels, no watermark. Return only the finished square image with unchanged1254x1254 framing. Daylight remains unchanged.'''
    if y>=2500: prompt+='\nThis is the lower continuation: mend remaining final stair riser and paving lines near the upper third. Preserve the already repaired upper context exactly, then join into the open paved courtyard below.'
    (ZONE/'prompts'/f'{ident}.prompt.txt').write_text(prompt,encoding='utf-8')
    print(json.dumps({'id':ident,'guide':p.as_posix(),'nativeWorldBox':d['nativeWorldBox'],'references':refs},ensure_ascii=False))

def inspect(ident):
    im,sources,overlays=mosaic(); p=ZONE/'native'/f'{ident}.png'; rec=read(p.with_suffix('.png.generation.json')); src=Image.open(p); assert src.size==(1254,1254)
    x,y=rec['coreWorldBox'][0]-OX,rec['coreWorldBox'][1]-OY; im.paste(src.crop(tuple(rec['coreCrop'])),(x,y))
    target=ZONE/'qa'/f'{ident}.candidate-native.png';save(im,target)
    for side,box in {'top':[x,y-128,x+1024,y+128],'bottom':[x,y+896,x+1024,y+1152],'left':[x-128,y,x+128,y+1024],'right':[x+896,y,x+1152,y+1024]}.items():save(im.crop(tuple(box)),ZONE/'qa'/f'{ident}-{side}-100pct.png')
    write(ZONE/'qa'/f'{ident}.overlay.json',{'operation':'exact native1024 repair core overlay; no feathering or scaling','source':p.as_posix(),'sha256':sha(p),'generationRecord':p.with_suffix('.png.generation.json').as_posix(),'coreCrop':rec['coreCrop'],'tileLocalPaste':[x,y],'worldPaste':rec['coreWorldBox'][:2],'review':'pending four-edge inspection','targetMosaic':target.as_posix()})
    print(target.as_posix())

def select(ident):
    q=ZONE/'qa'/f'{ident}.overlay.json';d=read(q);d.update(review='passed_native_four_perimeters_and_stair_geometry',reviewedAtUtc=now(),reviewer='repair_sol_ultra',finding='Native1254 candidate and all four exact1024 perimeter crops visually reviewed; stair slopes and stone surfaces continuous.');write(q,d)
    p=ZONE/'native'/f'{ident}.png.generation.json';d=read(p);d.update(status='usable_native_repair',internalSeams='passed_native_four_perimeters',externalSeams='tile whole boundaries pending');write(p,d)
    p=ZONE/f'selection-{TID}.json';s=read(p);s['overlays'].append(ident);s['updatedAtUtc']=now();write(p,s)
    print(json.dumps({'selected':ident,'sha256':d['sha256']}))

def stage(ident):
    q=ZONE/'qa'/f'{ident}.overlay.json';d=read(q);d.update(review='passed_top_left_right_bottom_pending_paired_lower_repair',reviewedAtUtc=now(),reviewer='repair_sol_ultra',finding='Top,left,right joins visually continuous. Bottom still carries the original vertical stair fault below the core, deferred to paired lower repair.');write(q,d)
    p=ZONE/f'selection-{TID}.json';s=read(p);s['overlays'].append(ident);s['updatedAtUtc']=now();write(p,s)
    print('Staged upper repair provisionally for paired lower input; no complete pass claimed.')

def assemble():
    im,sources,overlays=mosaic();version='sol-v1';p=ZONE/'tiles'/f'{TID}-{version}.png';save(im,p)
    qa=ZONE/'qa'/f'{TID}-{version}-final';qa.mkdir(exist_ok=True);crops=[]
    for r in range(4):
        for c in range(4):
            n=f'core-{r+1}-{c+1}-100pct.png';save(im.crop((c*1024,r*1024,(c+1)*1024,(r+1)*1024)),qa/n);crops.append(n)
    for i in range(1,4):
        for j in range(4):
            n=f'vertical-{i}-segment-{j+1}-100pct.png';save(im.crop((i*1024-128,j*1024,i*1024+128,(j+1)*1024)),qa/n);crops.append(n)
            n=f'horizontal-{i}-segment-{j+1}-100pct.png';save(im.crop((j*1024,i*1024-128,(j+1)*1024,i*1024+128)),qa/n);crops.append(n)
    for r in range(1,4):
        for c in range(1,4):
            n=f'cross-{r}-{c}-100pct.png';save(im.crop((c*1024-256,r*1024-256,c*1024+256,r*1024+256)),qa/n);crops.append(n)
    preview=im.copy();preview.thumbnail((1536,1536));pp=ZONE/'qa'/f'{TID}-{version}-preview.png';save(preview,pp)
    rec={'tileId':TID,'file':p.as_posix(),'sha256':sha(p),'size':[4096,4096],'worldBox':[OX,OY,OX+4096,OY+4096],'operation':'16 native1024 exact core crops and recorded native overlays, no resampling or feathering','sources':sources,'requiredOverlays':overlays,'baseCoverageMin':1,'baseCoverageMax':1,'uncoveredPixels':0,'finalArtUpscaled':False,'status':'complete_native_coverage_pending_whole_tile_QA','internalReview':'pending49crops','externalSeams':'pending upper/right whole boundaries','formalAccepted':False,'actualModel':None,'actualQuality':None,'assembledAtUtc':now(),'preview':pp.as_posix(),'inspectionCrops':qa.as_posix(),'cropCount':len(crops)}
    write(p.with_suffix('.png.derivation.json'),rec);print(json.dumps({'file':p.as_posix(),'sha256':rec['sha256'],'size':[4096,4096],'cropCount':len(crops)}))

def closepair():
    ident='r05_c12_cross_stair_upper_sol';q=ZONE/'qa'/f'{ident}.overlay.json';d=read(q);d.update(review='passed_native_four_perimeters_and_stair_geometry_with_lower_pair',finding='Top,left,right native joins passed; bottom passed in paired lower top1024 perimeter. Both native repair cores inspected.',pairedLowerRepair='r05_c12_cross_stair_lower_sol',reviewedAtUtc=now());write(q,d)
    p=ZONE/'native'/f'{ident}.png.generation.json';d=read(p);d.update(status='usable_native_repair',internalSeams='passed_native_four_perimeters_with_paired_lower_repair',externalSeams='whole tile pending');write(p,d)

def boundaries():
    p=ZONE/'tiles'/f'{TID}-sol-v1.png';mine=Image.open(p);refs=[]
    for other,direction in [('r04_c12','upper'),('r05_c13','right')]:
        op=ZONE/'tiles'/f'{other}.png';rec=read(op.with_suffix('.png.derivation.json'));assert sha(op)==rec['sha256'];nei=Image.open(op)
        full=Image.new('RGB',(4096,512) if direction=='upper' else (512,4096));parts=[]
        if direction=='upper':full.paste(nei.crop((0,3840,4096,4096)),(0,0));full.paste(mine.crop((0,0,4096,256)),(0,256))
        else:full.paste(mine.crop((3840,0,4096,4096)),(0,0));full.paste(nei.crop((0,0,256,4096)),(256,0))
        prefix=f'{TID}-sol-v1__{other}-{direction}-fullboundary';fp=ZONE/'qa'/f'{prefix}.png';save(full,fp)
        for i in range(4):
            sp=ZONE/'qa'/f'{prefix}-segment-{i+1}-100pct.png';box=(i*1024,0,(i+1)*1024,512) if direction=='upper' else (0,i*1024,512,(i+1)*1024);save(full.crop(box),sp);parts.append(sp.as_posix())
        refs.append({'neighbor':other,'direction':direction,'neighborFile':op.as_posix(),'neighborSha256':sha(op),'tileFile':p.as_posix(),'tileSha256':sha(p),'file':fp.as_posix(),'segments':parts,'inspectionScale':1,'status':'pending_visual_review'})
    write(ZONE/'qa'/f'{TID}-sol-v1-boundaries.json',{'tileId':TID,'boundaries':refs,'formalAccepted':False});print(json.dumps(refs))

def record():
    p=ZONE/'tiles'/f'{TID}-sol-v1.png';q=p.with_suffix('.png.derivation.json');d=read(q)
    qa=ZONE/'qa'/f'{TID}-sol-v1-final';crops=sorted(qa.glob('*-100pct.png'));assert len(crops)==49
    brp=ZONE/'qa'/f'{TID}-sol-v1-boundaries.json';br=read(brp)
    for b in br['boundaries']:b.update(status='passed_geometry_and_color_native_full4096_boundary',reviewer='repair_sol_ultra',reviewedAtUtc=now(),finding='All four1024 segments inspected at1:1; architecture, paving and shadows continuous.')
    write(brp,br)
    rp=ZONE/'qa'/f'{TID}-sol-v1-final-review.json';review={'tileId':TID,'candidatePath':p.as_posix(),'candidateSha256':sha(p),'derivationPath':q.as_posix(),'nativeSize':[4096,4096],'internalReview':'passed16core24seam9cross_native1to1','inspectionScale':1,'coreCount':16,'seamCount':24,'crossCount':9,'inspectionCrops':[{'file':x.as_posix(),'sha256':sha(x),'status':'passed_geometry_and_color'} for x in crops],'boundaryReview':brp.as_posix(),'reviewer':'repair_sol_ultra','reviewedAtUtc':now(),'formalAccepted':False,'remainingExternalBoundaries':['left r05_c11 pending generation','bottom r06_c12 outside current local candidate'],'requiredRepairOverlays':['r05_c12_cross_stair_upper_sol','r05_c12_cross_stair_lower_sol'],'finding':'Stair and cream foundation discontinuities removed by two native1024 overlay cores. All49 native internal crops and upper/right full4096 boundaries passed visual review. Daylight, residence footprint, stairs and walkable courtyard retained.','actualModel':None,'actualQuality':None}
    write(rp,review);d.update(status='internal_candidate_passed',internalReview=review['internalReview'],externalSeams='passed upper r04_c12 and right r05_c13 full4096 at1:1; left/bottom pending',reviewRecord=rp.as_posix(),formalAccepted=False);write(q,d)
    sp=ZONE/f'selection-{TID}.json';s=read(sp);s.update(candidatePath=p.as_posix(),derivationPath=q.as_posix(),candidateSha256=sha(p),internalReview=review['internalReview'],externalReview='upper and right full4096 boundaries passed',formalAccepted=False,pendingNativeRepairs=[],resolvedNativeRepairs=['p03_02 stair and cream foundation with upper cross overlay','p04_02 continuation with lower cross overlay'],updatedAtUtc=now(),reviewRecord=rp.as_posix());write(sp,s)
    for ident in ['r05_c12_p03_02','r05_c12_p04_02_v2']:
        gp=ZONE/'native'/f'{ident}.png.generation.json';g=read(gp);g.update(status='usable_native_core_with_required_stair_overlays',internalSeams='raw fault retained; resolved in final tile by recorded upper/lower native cross overlays',requiredOverlays=review['requiredRepairOverlays']);write(gp,g)
    print(json.dumps({'candidatePath':p.as_posix(),'derivationPath':q.as_posix(),'sha256':sha(p),'reviewRecord':rp.as_posix(),'internalReview':review['internalReview'],'formalAccepted':False}))

if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='prepare':prepare(sys.argv[2],int(sys.argv[3]))
    elif mode=='inspect':inspect(sys.argv[2])
    elif mode=='select':select(sys.argv[2])
    elif mode=='stage':stage(sys.argv[2])
    elif mode=='closepair':closepair()
    elif mode=='assemble':assemble()
    elif mode=='boundaries':boundaries()
    elif mode=='record':record()
