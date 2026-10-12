"""Audit/repair text evidence only. Never modifies images or generation receipts."""
from pathlib import Path
import copy, hashlib, json, re
from datetime import datetime, timezone
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PROV = ROOT / 'provenance'
NOW = datetime.now(timezone.utc).isoformat()

def load(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def save(p, d):
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def rel(p):
    return p.relative_to(ROOT).as_posix()

fixes = []
errors = []

# The rejected record was renamed without updating its three sibling paths.
p = PROV/'cast/E/08-rejected.json'
d = load(p)
expected = {'file':'work/cast/E/08-rejected.png', 'prompt':'prompts/cast/E/08-rejected.txt'}
for key, value in expected.items():
    if d[key] != value:
        fixes.append({'record':rel(p),'field':key,'old':d[key],'new':value})
        d[key] = value
if d['evidence']['receipt'] != 'provenance/cast/E/08-rejected.receipt.json':
    fixes.append({'record':rel(p),'field':'evidence.receipt','old':d['evidence']['receipt'],'new':'provenance/cast/E/08-rejected.receipt.json'})
    d['evidence']['receipt']='provenance/cast/E/08-rejected.receipt.json'
d['visualStatus']='rejected-glow-margin; historical-record'
d['rejectionReason']='The subsequent edit prompt requests bounded antler glow and transparent top margin; this is the superseded input of that edit.'
d['rejectionReasonEvidence']='prompts/cast/E/08.txt'
save(p,d)

# The first W01 workspace image was replaced, while its original tool file remains
# a source witness. Do not make its record point at the different current frame.
p=PROV/'cast/W/01.attempt1.json'
d=load(p)
source=Path(d['evidence']['hostSourcePath'])
if d['file']=='work/cast/W/01.png':
    d['formerWorkspaceFile']=d['file']
    d['file']=str(source)
    d['prompt']='prompts/cast/W/01.attempt1.txt'
    fixes.append({'record':rel(p),'issue':'Superseded W01 record pointed to the replacement image and prompt','source':str(source)})
d['visualStatus']='rejected-support-continuity; historical-record'
d['rejectionReason']='Initial support positions differed from the later sequence; independently redrawn using frame 16 composition.'
d['rejectionReasonEvidence']='provenance/cast/W/QA.json'
save(p,d)

# W06 first attempt has a real receipt, saved prompt and QA rejection SHA, but no
# standalone record. Reconstruct only from those witnesses, never invent times.
p=PROV/'cast/W/06.attempt1.json'
if not p.exists():
    receipt_path=PROV/'cast/W/06.receipt.json'
    receipt=load(receipt_path)
    match=re.search(r' as (.+?\.png) by default\.',receipt['output_hint'])
    if not match:
        raise RuntimeError('Original W06 receipt has no tool source path')
    source=Path(match.group(1))
    d=copy.deepcopy(load(PROV/'cast/W/06.json'))
    for key in ('generatedAtLocal','timezone','visualReview','auditEvidence','runtimeDerivative','exportRecord'):
        d.pop(key,None)
    d.update({'file':str(source),'formerWorkspaceFile':'work/cast/W/06.png',
        'sha256':'35da00e08c8a1b16194a988eeacb6c1e06fdfbcaf61fc56258c9c4e025b1a513',
        'generatedAt':receipt['completedAt'],'startedAt':receipt['startedAt'],
        'prompt':'prompts/cast/W/06.attempt1.txt',
        'submittedParameters':{'model':None,'quality':None,'transparent_background':True,'referenced_image_paths':receipt['references']},
        'evidence':{'receipt':rel(receipt_path),'outputHint':receipt['output_hint'],'hostSourcePath':str(source)},
        'visualStatus':'rejected-glow-touches-top; historical-record',
        'rejectionReason':'Glow touched the top edge; redrawn with bounded glow.',
        'rejectionReasonEvidence':'provenance/cast/W/QA.json',
        'reconstructedRecord':{'auditTime':NOW,'basis':['provenance/cast/W/06.receipt.json','provenance/cast/W/QA.json','prompts/cast/W/06.attempt1.txt'],'generationTimesNotInferred':True}})
    if source.exists():
        with Image.open(source) as im:
            d.update(width=im.width,height=im.height,format=im.format,mode=im.mode)
        if sha(source)!=d['sha256']:
            raise RuntimeError('Original W06 host-source SHA differs from recorded rejection SHA')
    save(p,d)
    fixes.append({'record':rel(p),'issue':'Created missing historical W06 single-image record from existing receipt, QA SHA and prompt'})

records={}
for p in sorted(PROV.glob('*/*/*.json')):
    d=load(p)
    if 'file' in d and 'sha256' in d and 'prompt' in d:
        records[p]=d
record_by_sha={d['sha256']:rel(p) for p,d in records.items()}
rows=[]
cleanup_refs=[]
roles=['原有E身份与解剖','原有W身份与解剖','主要画法材质完成度']
for p,d in records.items():
    numbered=re.fullmatch(r'\d{2}',p.stem) is not None
    source=ROOT/d['file']
    prompt=ROOT/d['prompt']
    receipt_path=ROOT/d['evidence']['receipt']
    receipt=load(receipt_path)
    refs=receipt['references']
    if d['submittedParameters']['referenced_image_paths']!=refs:
        errors.append({'record':rel(p),'issue':'submitted reference paths differ from receipt'})
    if len(d['references'])!=len(refs):
        fixes.append({'record':rel(p),'issue':'Truncated fourth-reference metadata from zip with three roles','before':len(d['references']),'after':len(refs)})
    known={r['path']:r for r in d['references']}
    rebuilt=[]
    for i, ref in enumerate(refs):
        rp=Path(ref)
        item=copy.deepcopy(known.get(ref,{'path':ref,'role':roles[i] if i<3 else '本只动作连续性或定点修复参考'}))
        if rp.exists():
            actual=sha(rp)
            if item.get('sha256') and item['sha256']!=actual:
                errors.append({'record':rel(p),'issue':'Reference SHA mismatch','path':ref,'recorded':item['sha256'],'actual':actual})
            else:
                item['sha256']=actual
        elif not item.get('sha256'):
            errors.append({'record':rel(p),'issue':'Reference absent without historical SHA','path':ref})
        if item.get('sha256') in record_by_sha:
            linked=record_by_sha[item['sha256']]
            item['sourceGenerationRecord']=linked
            item['pathRole']='historical-submitted-input; preserve exact path and SHA after source cleanup'
            target=ROOT/linked
            if re.fullmatch(r'\d{2}',target.stem):
                action,direction=target.parts[-3:-1]
                item['retainedRuntimeDerivative']=f'runtime/{action}/{direction}/{target.stem}.png'
                item['derivativeExportRecord']=f'provenance/export/{action}/{direction}/{target.stem}.json'
            cleanup_refs.append({'record':rel(p),'inputPath':ref,'inputSHA256':item['sha256'],'sourceGenerationRecord':linked,'rejectedInput':not bool(re.fullmatch(r'\d{2}',target.stem))})
        rebuilt.append(item)
    d['references']=rebuilt
    source_ok=source.exists() and sha(source)==d['sha256']
    if not source_ok:
        errors.append({'record':rel(p),'issue':'Generation source missing or SHA mismatch','path':str(source)})
    if not prompt.exists():
        errors.append({'record':rel(p),'issue':'Prompt missing'})
    if d.get('actualModel') is not None or d.get('actualQuality') is not None:
        errors.append({'record':rel(p),'issue':'Actual model/quality must remain undisclosed null'})
    if d['submittedParameters'].get('model') is not None or d['submittedParameters'].get('quality') is not None:
        errors.append({'record':rel(p),'issue':'Unsupported submitted model/quality selectors'})
    if d['configSnapshot']['model']!='gpt-image-2.5-sunburst' or d['configSnapshot']['quality']!='max':
        errors.append({'record':rel(p),'issue':'Unexpected configured batch target'})
    d['auditEvidence']={'auditedAt':NOW,'promptSHA256':sha(prompt),'receiptSHA256':sha(receipt_path),
        'referenceCount':len(refs),'sourceSHA256Verified':source_ok,'timesPreservedFromExistingEvidence':True,
        'receiptStartTime':receipt.get('startedAt'),'receiptCompletionTime':receipt.get('completedAt'),
        'timeCaveat':receipt.get('startedAtReason'),'actualModelAndQualityUndisclosed':True}
    if numbered:
        action,direction=p.parts[-3:-1]
        d['runtimeDerivative']=f'runtime/{action}/{direction}/{p.stem}.png'
        d['exportRecord']=f'provenance/export/{action}/{direction}/{p.stem}.json'
        d['generationSourceIsHistoricalAfterExport']=True
    else:
        base=re.match(r'\d{2}',p.stem).group()
        d['replacedByGenerationRecord']=f'provenance/{p.parts[-3]}/{p.parts[-2]}/{base}.json'
        d['historicalOnly']=True
    save(p,d)
    rows.append({'record':rel(p),'current':numbered,'file':d['file'],'sha256':d['sha256'],
        'prompt':d['prompt'],'receipt':d['evidence']['receipt'],'referenceCount':len(refs),
        'sourceSHA256Verified':source_ok,'timeCaveat':receipt.get('startedAtReason')})

report={'schemaVersion':1,'auditedAt':NOW,'scope':'Only this character; text records and ingest script changed; no images changed or removed, no build run',
    'currentRecords':sum(r['current'] for r in rows),'historicalRecords':sum(not r['current'] for r in rows),
    'currentUniqueSHA256':len({r['sha256'] for r in rows if r['current']}),
    'allGenerationSourcesVerified':all(r['sourceSHA256Verified'] for r in rows),'issuesFixed':fixes,'errors':errors,
    'timeEvidenceLimitations':[r for r in rows if r['timeCaveat']],
    'actualModel':None,'actualQuality':None,
    'cleanupHandoff':{'sourceImagesNotDeletedByAudit':True,'instructions':'After root verifies all 68 runtime exports, keep generation and export records, prompt and receipt text. Historical submitted paths/SHA remain verbatim. Sources outside this task are evidence only and are outside this write scope; shared identity/style references must remain.',
        'withinScopeGenerationSources':[r['file'] for r in rows if not Path(r['file']).is_absolute()],
        'outsideScopeHistoricalSources':[r['file'] for r in rows if Path(r['file']).is_absolute()],
        'inputReferencesToGenerationSources':cleanup_refs},'records':rows}
save(PROV/'audit-final.json',report)
print(json.dumps({k:report[k] for k in ('currentRecords','historicalRecords','currentUniqueSHA256','allGenerationSourcesVerified','errors')},ensure_ascii=False))
print('repairs',len(fixes),'source input links',len(cleanup_refs))
