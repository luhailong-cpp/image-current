"""Read-only pixel replay with explicit missing-reference evidence gaps."""
from pathlib import Path
import sys,importlib.util,json,hashlib,io,datetime
import numpy as np
from PIL import Image
sys.dont_write_bytecode=True
B=Path(__file__).resolve().parent;T=B/'r13_c13';R=T/'repairs'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pngsha(im):
    out=io.BytesIO();im.save(out,format='PNG');return hashlib.sha256(out.getvalue()).hexdigest()
gate=B.parent.parent/'capacity-layout-gate-20261010.json';assert read(gate)['holdGenerationAtNewCoordinates']
guard_paths=[B/'progress.json',T/'candidate'/'r13_c13-4k-candidate.png',T/'candidate'/'r13_c13-4k-candidate-repaired.png',T/'candidate'/'r13_c13-context-4326-repaired.png',T/'candidate'/'replay-verification.json',T/'review'/'current'/'qa-report.json']
before={str(p):sha(p) for p in guard_paths};guards=dict(before);missing={};verified_reference_paths=set()
def check_file(p,digest):
    p=Path(p);assert p.is_file(),str(p);assert sha(p)==digest,str(p)+' SHA mismatch';guards[str(p)]=digest
def check_record(rec):
    check_file(rec['file'],rec['sha256']);assert Image.open(rec['file']).size==(1254,1254)
    check_file(rec['prompt'],rec['promptSha256']);request=read(rec['evidence']['request']);receipt=read(rec['evidence']['receipt'])
    assert request['prompt'].rstrip('\r\n')==Path(rec['prompt']).read_text(encoding='utf-8').rstrip('\r\n')
    assert receipt['status'].startswith('succeeded') and rec['actualModel'] is None and rec['actualQuality'] is None
    for ref in rec['references']:
        p=Path(ref['path'])
        if not p.is_file():
            k=(str(p),ref['sha256']);missing.setdefault(k,{'path':str(p),'expectedSha256':ref['sha256'],'expectedDimensions':ref['dimensions'],'affectedGeneratedIds':[]})['affectedGeneratedIds'].append(rec['id'])
            continue
        check_file(p,ref['sha256']);assert list(Image.open(p).size)==ref['dimensions'];verified_reference_paths.add(str(p))
manifest=read(T/'candidate'/'assembly-manifest.json');sources=manifest['nativeSources'];active=read(T/'active-native-map.json')
assert len(sources)==16 and manifest['activeNativeMapSnapshot']==active
pixels=[]
for item in sources:
    p=Path(item['generationRecord']);check_file(p,item['generationRecordSha256']);rec=read(p);assert rec==item['generationRecordSnapshot'];check_record(rec)
    pixels.append(np.asarray(Image.open(rec['file']).convert('RGB')).copy())
spec=importlib.util.spec_from_file_location('assembly',B/'assemble_candidate.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
rows=[pixels[r*4:(r+1)*4] for r in range(4)];seams={};strips=[]
for r,patches in enumerate(rows,1):
    arr=patches[0]
    for c,patch in enumerate(patches[1:],2):arr,_=m.append_patch(arr,patch,f'r{r}c{c}',seams)
    strips.append(arr)
combined=strips[0].transpose(1,0,2)
for r,strip in enumerate(strips[1:],2):combined,_=m.append_patch(combined,strip.transpose(1,0,2),f'row{r}',seams)
context=Image.fromarray(combined.transpose(1,0,2));im=context.crop((115,115,4211,4211))
assert pngsha(context)==sha(T/'candidate'/'r13_c13-context-4326.png')
state=pngsha(im);assert state==sha(T/'candidate'/'r13_c13-4k-candidate.png')==manifest['output']['sha256']
repair_count=0
for step in read(R/'composition-history.json')['steps']:
    assert state==step['sourceSha256'];rec=read(R/f"{step['id']}-native.png.generation.json");check_record(rec)
    meta=rec['targetMetadata'];box=step['placement'];check_file(meta['target'],meta['targetSha256'])
    assert np.array_equal(np.asarray(im.crop(box)),np.asarray(Image.open(meta['target']).convert('RGB')))
    check_file(step['mask'],step['maskSha256']);check_file(step['native'],step['nativeSha256'])
    im.paste(Image.composite(Image.open(step['native']).convert('RGB'),im.crop(box),Image.open(step['mask'])),(box[0],box[1]))
    state=pngsha(im);assert state==step['outputSha256'];repair_count+=1
step=read(R/'context-composition.json');rec=read(step['generationRecord']);check_record(rec);derive=step['sourceDerivation']
assert state==derive['currentCoreSha256'];check_file(derive['baseContext'],derive['baseContextSha256'])
context=Image.open(derive['baseContext']).convert('RGB');context.paste(im,(115,115))
assert pngsha(context)==step['sourceSha256'];check_file(step['source'],step['sourceSha256'])
box=step['placementIn4326'];meta=rec['targetMetadata'];check_file(meta['target'],meta['targetSha256'])
assert np.array_equal(np.asarray(context.crop(box)),np.asarray(Image.open(meta['target']).convert('RGB')))
check_file(step['mask'],step['maskSha256']);check_file(step['native'],step['nativeSha256'])
context.paste(Image.composite(Image.open(step['native']).convert('RGB'),context.crop(box),Image.open(step['mask'])),(box[0],box[1]))
assert pngsha(context)==step['outputContextSha256']==sha(step['outputContext'])
im=context.crop(step['finalCropBox']);state=pngsha(im);assert state==step['outputCoreSha256']==sha(step['outputCore']);repair_count+=1
for p,digest in guards.items():assert sha(p)==digest
assert before=={str(p):sha(p) for p in guard_paths}
qa=read(T/'review'/'current'/'qa-report.json');assert qa['imageSha256']==state
record={'schemaVersion':1,'verifiedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'gateFile':str(gate),'gateSha256':sha(gate),'imageGenerationCalls':0,'modifiedExistingArtwork':False,'existingGuardedFilesUnchanged':True,'checkedExistingFiles':before,'sourceNativeCount':16,'sourceNativeDimensions':[1254,1254],'initialAssemblyReplayedFrom16NativeSources':True,'initialContextSize':[4326,4326],'initialCoreSize':[4096,4096],'nativeRepairStepsReplayed':repair_count,'finalCoreSha256':state,'finalCoreExactReplay':True,'finalContextExactReplay':True,'allHistoricalReferencesPresent':not bool(missing),'missingReferenceEvidence':list(missing.values()),'presentReferenceFilesVerified':len(verified_reference_paths),'actualModel':None,'actualQuality':None,'internalQaVerdict':qa['internalVerdict'],'externalQaVerdict':qa['externalVerdict'],'formalAccepted':False,'capacity5000Validated':False,'worldSize':None,'note':'16native core sources and7repair sources replayed exactly; missing historical reference files explicitly listed. Existing generation records not rewritten; reference presence is not falsely inferred from hash records.'}
(B/'capacity-gate-provenance-review.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:record[k] for k in ['sourceNativeCount','initialAssemblyReplayedFrom16NativeSources','nativeRepairStepsReplayed','finalCoreSha256','finalCoreExactReplay','allHistoricalReferencesPresent','missingReferenceEvidence','internalQaVerdict','externalQaVerdict','formalAccepted']}))


