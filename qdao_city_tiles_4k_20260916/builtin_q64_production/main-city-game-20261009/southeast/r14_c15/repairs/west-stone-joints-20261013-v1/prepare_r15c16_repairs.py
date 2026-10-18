from pathlib import Path
import json,hashlib,datetime
import numpy as np
from PIL import Image,ImageDraw

S=Path(__file__).resolve().parents[3]
T=S/'r15_c16'
Q=S/'r14_c15/review/independent-r15_c16-0cd62b74724ba75d'
R=T/'repairs/independent-seam-fixes-20261013-v1'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,o):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    assert not p.exists(),p
    p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def ev(p,**kw): return dict(path=str(p),sha256=sha(p),**kw)
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
idx=read(Q/'index.json'); sources=idx['sourceFiles']
for e in sources.values(): assert sha(e['path'])==e['sha256']
core=Image.open(sources['candidate']['path']).convert('RGB')
west=Image.open(sources['west']['path']).convert('RGB')
active=read(T/'active-native-map.json')
audits=[]
for key,v in active.items():
    prep=read(T/'records'/f'{v}.preparation.json')
    parent=prep.get('nativeCorrectionOf')
    if not parent: continue
    p=Path(parent['path']); assert sha(p)==parent['sha256']
    rec=read(str(p)+'.generation.json');e=rec['evidence']
    pp=read(e['preparation']); receipt=read(e['receipt'])
    for path,h in [(e['preparation'],e['preparationSha256']),(e['receipt'],e['receiptSha256']),(pp['request'],pp['requestSha256']),(pp['prompt'],pp['promptSha256'])]: assert sha(path)==h
    assert rec['tool']=='image_gen.imagegen' and rec['route']=='builtin'
    assert receipt.get('actualModel') is None and receipt.get('actualQuality') is None
    assert not receipt.get('resizedAfterGeneration') and not receipt.get('finalArtUpscaled')
    assert prep['anchors']==pp['anchors'] and prep['references'][:3]==pp['references'][:3]
    assert Image.open(p).size==(1254,1254)
    target=Path(pp['references'][-1]['path']);d=read(str(target)+'.derived.json')
    replay=Image.open(d['layoutSource']).convert('RGB')
    for a in pp['anchors']:
        assert sha(a['path'])==a['sha256']
        replay.paste(Image.open(a['path']).convert('RGB').crop(a['sourceCrop']),a['target'][:2])
    assert np.array_equal(np.array(replay),np.array(Image.open(target).convert('RGB')))
    audits.append(dict(logicalPatch=key,currentVersion=v,parentNative=ev(p),parentReceipt=ev(e['receipt']),parentPreparation=ev(e['preparation']),parentOriginalAnchoredGuide=ev(target),parentGuidePixelReplay=True,currentInputIsActualNativeNotDerived=True,actualModel=None,actualQuality=None))
assert len(audits)==2
reviewed=[e for e in idx['evidence'] if e['name'].startswith(('v','h','j','external-'))]
assert len(reviewed)==41
issues=[dict(id='I01',status='failed_pending_native_local_repair',coreBox=[2035,965,2180,1015],evidence=['v2048-q0','j2048-1024'],description='Short horizontal stone grout has a blind left end within the large pale wall slab, immediately left of the vertical joint and gold suspension cap; surrounding main wall silhouette remains continuous.'),dict(id='W01',status='failed_pending_native_local_repair',coreBox=[0,3515,140,3705],neighborBox=[4032,3515,4096,3705],evidence=['external-west-q3'],description='At the true core join, capstone top contour makes a short horizontal shoulder and material changes from fine beige grid-like stone on west to larger grey mottling on child. Repair child only; preserve west core and child y3712..4096.')]
for e in reviewed:
    assert sha(e['path'])==e['sha256']
    e['visuallyViewedAtNativeResolution']=True
    e['status']='passed_no_blocking_discontinuity_observed'
    if e['name'] in ['v2048-q0','j2048-1024','external-west-q3']:
        e['status']='failed_local_issue_recorded'
write(Q/'visual-qa.json',dict(schemaVersion=1,tile='r15_c16',reviewer='/root/assembly_support',recordedAt=now,sourceFiles=sources,evidenceCount=41,evidence=reviewed,extractedButNotClaimedViewed=16,internalStatus='failed_local_I01_other_32_internal_evidence_passed',northStatus='passed_against_b0fe_core',westStatus='failed_W01_q3_other_quarters_passed',eastStatus='not_reviewed_in_this_task',southStatus='root_local_pass_separate_external_join_pending',formalAccepted=False,issues=issues))
write(Q/'native-edit-lineage-audit.json',dict(schemaVersion=1,recordedAt=now,helper=ev(S/'production_workflow_native_edit_v1.py'),scope='Read-only current two native corrections; parent original anchored guide replayed, not current edited pixels',status='current_evidence_passed',parentLineages=audits,formalAccepted=False))

def prepare(name,origin,dest,edit_prompt):
    out=R/name;out.mkdir(parents=True,exist_ok=False)
    ox,oy=origin
    if ox<0:
        target=Image.new('RGB',(1254,1254))
        target.paste(west.crop((4096+ox,oy,4096,oy+1254)),(0,0))
        target.paste(core.crop((0,oy,1254+ox,oy+1254)),(-ox,0))
        pixel_sources=[dict(source=sources['west'],sourceCrop=[4096+ox,oy,4096,oy+1254],target=[0,0,-ox,1254]),dict(source=sources['candidate'],sourceCrop=[0,oy,1254+ox,oy+1254],target=[-ox,0,1254,1254])]
    else:
        target=core.crop((ox,oy,ox+1254,oy+1254));pixel_sources=[dict(source=sources['candidate'],sourceCrop=[ox,oy,ox+1254,oy+1254],target=[0,0,1254,1254])]
    target.save(out/'target-1254.png')
    local=[dest[0]-ox,dest[1]-oy,dest[2]-ox,dest[3]-oy]
    mask=Image.new('L',(1254,1254));ImageDraw.Draw(mask).rectangle((local[0],local[1],local[2]-1,local[3]-1),fill=255);mask.save(out/'edit-mask.png')
    marked=target.copy();overlay=Image.new('RGB',(1254,1254),(255,0,255));marked.paste(overlay,(0,0),mask);marked.save(out/'target-marked.png')
    prompt='Use case: precise-object-edit. Output exactly 1254 by 1254 pixels, opaque PNG, same framing and native scale as Image 1. Image 1 is the actual unchanged native context and edit target. Image 2 is only an editing-location guide: its magenta rectangle is the ONLY editable area, and magenta must not appear in output. '+edit_prompt+' Preserve all pixels and geometry outside that rectangle. Preserve the exact daytime hand-painted Daoist game-map style, natural stone detail, shadow, scale and perspective. No new props, ornaments, vegetation, text, border, blur, rescale or camera shift. Return the full Image 1 composition with only this small precise repair.'
    (out/'prompt.txt').write_text(prompt,encoding='utf-8')
    request=dict(prompt=prompt,referenced_image_paths=[str(out/'target-1254.png'),str(out/'target-marked.png')],transparent_background=False)
    write(out/'request.json',request)
    write(out/'preparation.json',dict(schemaVersion=1,tile='r15_c16',id=name,preparedAt=now,tool='image_gen.imagegen',route='builtin',actualModel=None,actualQuality=None,expectedNativeSize=[1254,1254],base=sources['candidate'],contextOriginInCore=origin,sourceCrop=local,destinationCoreBox=dest,referenceImages=[ev(out/'target-1254.png',role='unchanged actual native context'),ev(out/'target-marked.png',role='editing-location guide only')],mask=ev(out/'edit-mask.png'),pixelSources=pixel_sources,prompt=ev(out/'prompt.txt'),request=ev(out/'request.json'),resized=False,protectedCoreBox=[0,3712,4096,4096],compositePlan='Integer crop RGB from returned actual native, saved minimum-error plus alpha; no RGB correction; all outside edit box immutable',formalAccepted=False))
    return dict(id=name,request=str(out/'request.json'),preparation=str(out/'preparation.json'))
prepared=[]
prepared.append(prepare('W01-west-capstone',[-627,2842],[0,3380,360,3712],'The fixed left 627 columns belong to the already selected west neighbor and MUST remain unchanged. The stone balustrade cap crosses x=627 near y=695. Within the magenta area on the right side only, remove the short horizontal shoulder at the join: continue the existing left capstone top/front contour smoothly in the same up-right diagonal, with the same thickness, highlight, small pale warm stone texture and shadow. Gently reconcile the right mottled grey texture to the left small natural stone texture at x=627. This is one continuous diagonal stone cap, not a new block, step, ledge or notch. Keep the existing legitimate transverse block joint and all distant cap geometry. Rows y>=870 must remain exactly as in Image 1.'))
prepared.append(prepare('I01-blind-stone-grout',[1500,400],[2010,950,2164,1024],'Inside the tiny magenta rectangle, erase only the short horizontal blind-ended groove on the pale stone face, located approximately image x550..660,y585..600. Replace that short stray groove with the same continuous pale stone face and its subtle hand-painted mineral texture. Preserve the adjoining vertical joint at image x660 and the gold ball, gold square cap, suspension cord, all longer legitimate stone joints and every architectural edge. Do not extend the stray horizontal groove or add any new seam.'))
write(R/'prepared-index.json',dict(recordedAt=now,requests=prepared,qa=ev(Q/'visual-qa.json'),lineageAudit=ev(Q/'native-edit-lineage-audit.json'),formalAccepted=False))
print(json.dumps(dict(prepared=prepared,qa=ev(Q/'visual-qa.json'),lineageCount=len(audits)),ensure_ascii=False))
