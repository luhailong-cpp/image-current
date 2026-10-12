from native_work import *
import sys

def recover():
    ident='r04_c10_p04_02'
    src=Path('C:/Users/luyua/.codex/generated_images/01a13495-6a72-7e10-acef-9a45bf43e354/exec-59879915-3ddf-4251-b136-d946b4fe0995.png')
    receipt=ZONE/'receipts'/f'{ident}.tool.json'
    assert not receipt.exists()
    write(receipt,{'receiptType':'local_recovery_evidence_not_original_tool_response','recoveredAtUtc':now(),'originalToolPath':src.as_posix(),'sha256':sha(src),'originalToolResponseAvailable':False,'identificationEvidence':['prior checkpoint currentPatch r04_c10_p04_02 prepared at 2026-10-13T10:22:23Z','same generated_images subagent directory as the immediately preceding r04_c10_p03_02 result','file saved at 2026-10-13T10:29:05Z after preflight','direct visual review confirms exact same distinctive top and right stone anchor geometry'],'actualModel':None,'actualQuality':None})
    from west_sol_ultra_20261012 import archive
    archive(ident,src)
    meta=ZONE/'native'/f'{ident}.png.generation.json';v=read(meta)
    v['evidence']['fields']=[];v['evidence']['originalToolResponseAvailable']=False
    v['evidence']['recoveryRecord']=receipt.as_posix();write(meta,v)

def finish(name,failed):
    dp=ZONE/'tiles'/f'{name}.png.derivation.json';d=read(dp)
    assert d['tileId']=='r04_c10'
    images=sorted(Path(d['inspectionCrops']).glob('*-100pct.png'));assert len(images)==49
    ext=[]
    for side in ('north','east'):
        q=ZONE/'qa'/f'r04_c10-west-recovery-{side}-border.json';v=read(q)
        v.update(status='passed_1to1_visual_review',reviewedAtUtc=now(),reviewer='west_continued_20261013',findings='All four final candidate edge segments reviewed at 1:1; continuous paving contours and material.')
        write(q,v);ext.append(v)
    record={'tileId':'r04_c10','candidatePath':d['file'],'sha256':d['sha256'],'size':[4096,4096],'preview':d['preview'],'status':'requires_local_material_repair' if failed else 'complete_internal_QA_passed','internalReview':'requires_local_material_repair' if failed else 'passed16core24seam9cross_native1to1','reviewer':'west_continued_20261013','reviewedAtUtc':now(),'inspectionScale':1,'coreReviewCount':16,'seamReviewCount':24,'crossReviewCount':9,'inspectedCrops':[{'file':p.as_posix(),'sha256':sha(p),'size':list(Image.open(p).size),'resized':False,'status':'requires_local_repair' if p.name in failed else 'passed_visual_100pct'} for p in images],'externalReviews':ext,'externalPending':['west r04_c09 unavailable','south r05_c10 unavailable'],'pendingIssues':failed,'formalAccepted':False,'actualModel':None,'actualQuality':None,'finalArtUpscaled':False,'assembly':d['operation']}
    rp=ZONE/'qa'/f'{name}-review.json';assert not rp.exists();write(rp,record)
    d.update(status=record['status'],internalReview=record['internalReview'],reviewPath=rp.as_posix(),pendingIssues=failed,externalSeams='north and east final candidate edges passed; west and south pending neighbors');write(dp,d)
    sp=ZONE/'selection-r04_c10.json';s=read(sp);s.update(internalReview=d['internalReview'],reviewPath=rp.as_posix(),pendingIssues=failed,selectionIsPartialCandidate=False,formalAccepted=False,updatedAtUtc=now());write(sp,s)
    from west_recovery_20261013 import checkpoint
    checkpoint(None,record['status'])
    print(json.dumps({'candidate':d['file'],'sha256':d['sha256'],'review':rp.as_posix(),'status':record['status']}))

if __name__=='__main__':
    if sys.argv[1]=='recover':recover()
    if sys.argv[1]=='finish':finish(sys.argv[2],sys.argv[3:])
