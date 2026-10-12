from pathlib import Path
R=Path(__file__).resolve().parent
s=(R/'r12_c13_resume_sol_20261012.py').read_text(encoding='utf-8')
s=s.replace("TID='r12_c13'", "TID=sys.argv.pop(1)\nassert TID in ['r13_c13','r14_c13']")
s=s.replace("PROGRESS=ROOT/'progress-r12_c13.json'", "PROGRESS=ROOT/f'progress-{TID}.json'")
s=s.replace("QA=ROOT/'qa/r12_c13-resume-sol-20261012'", "QA=ROOT/f'qa/{TID}-resume-sol-20261012'")
s=s.replace("if mode=='initialize':", "if mode=='legacy_unused_initialize':")
s=s.replace("    d=read(RESUME);d['selectedVersions'][rc]=ver", "    d=read(RESUME);d.setdefault('tileSelectedVersions',{}).setdefault(TID,{})[rc]=ver")
s=s.replace("if mode=='legacy_unused_initialize':", """if mode=='initialize':
    assert not PROGRESS.exists()
    pr=read(ROOT/'progress-r12_c13.json')
    d={'schemaVersion':1,'zone':'southeast','owner':'right_resume_sol','status':'guides_prepared','updatedAt':now(),'assigned4kCount':1,'generatedNativeCount':0,'usableNativeCount':0,'complete4kCount':0,'fullyCovered4kCount':0,'internalPassed4kCount':0,'externalPassed4kCount':0,'formalAcceptedCount':0,'currentTile':TID,'currentPatch':None,'selectedVersions':{},'missingPatchCoordinates':[f'{r}{c}' for r in range(1,5) for c in range(1,5)],'configSnapshot':pr['configSnapshot'],'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':pr['unverifiedReason'],'productionFrozen':False,'inFlightRequestCount':0,'unsavedSuccessfulOutputCount':0,'resumeAuthority':str(AUTH),'resumeRecord':RESUME.name,'nextStep':'Generate using accepted north native row and exact adjacent overlaps; coordinate west with root.'}
    write(PROGRESS,d)
    plan=next(t for t in read(ROOT/'coordinate-plan.json')['tiles'] if t['id']==TID)
    ref=read(ROOT/'references.json')[0]
    with Image.open(ref['file']) as im:
        for p in plan['patches']:
            out=ROOT/'guides'/f\"{p['id']}.layout-only.png\";assert not out.exists()
            im.transform((1254,1254),Image.Transform.EXTENT,tuple(p['layoutReferenceBox']),Image.Resampling.BICUBIC).save(out)
            write(Path(str(out)+'.generation.json'),{'file':str(out),'sha256':sha(out),'generatedAt':now(),'width':1254,'height':1254,'operation':'fractional-coordinate overview crop enlargement, guide ONLY; never final pixels','derivedFrom':[ref],'sourceCropBox':p['layoutReferenceBox'],'globalBox':p['nativeGlobalBox'],'usableAsFinalArt':False})
    rd=read(RESUME);rd.setdefault('tileSelectedVersions',{})[TID]={};rd['currentTile']=TID;rd['updatedAtUtc']=now();write(RESUME,rd)
    print(json.dumps({'tile':TID,'guides':16,'selected':0}))
elif mode=='legacy_unused_initialize':""")
(R/'right_next_tiles_resume_sol_20261012.py').write_text(s,encoding='utf-8')
print('Prepared right_next_tiles_resume_sol_20261012.py')
