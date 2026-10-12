"""Read-only audit of current private inventories; writes only the assigned review JSON.

Run with the existing Python/Pillow runtime. No image is changed or deleted.
Raw receipts, captured host paths and inferred recovery are separate evidence grades.
Cleanup candidates are conservative suggestions requiring root review and a fresh run.
"""
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime, timezone
import base64, hashlib, io, json, re, subprocess
from PIL import Image, ImageOps
from inventory_sources import current_slots, ORDER

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'reviews/full-source-chain-audit.json'
INVENTORIES = ORDER
IMAGE_EXT = {'.png', '.gif', '.jpg', '.jpeg', '.webp'}
observed = {}

def digest(data): return hashlib.sha256(data).hexdigest()
def resolve(value, base=ROOT):
    p = Path(str(value).replace('\\', '/'))
    return (p if p.is_absolute() else base/p).resolve()
def label(p):
    p = p.resolve()
    return p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p)
def read_bytes(p):
    p = p.resolve(); data = p.read_bytes(); observed.setdefault(str(p), digest(data))
    return data
def read_json(p): return json.loads(read_bytes(p).decode('utf-8-sig'))
def file_sha(p): return digest(read_bytes(p))
def image_info(p):
    data = read_bytes(p)
    with Image.open(io.BytesIO(data)) as im:
        im.load(); alpha = im.getchannel('A').getextrema() if im.mode == 'RGBA' else None
        meta = {'path':label(p), 'sha256':digest(data), 'size':list(im.size),
                'mode':im.mode, 'format':im.format, 'alphaExtrema':alpha}
        return meta, im.copy()
def field(obj, path):
    cur = obj
    for key in path.split('.'):
        if not isinstance(cur, dict) or key not in cur:return None
        cur = cur[key]
    return cur
def model_evidence(obj):
    config = obj.get('configSnapshot', {})
    params = obj.get('submittedParameters', {})
    return {'configuredTarget':{'model':config.get('model'), 'quality':config.get('quality')},
            'submitted':{k:{'present':k in params, 'value':params.get(k)} for k in ['model','quality']},
            'actual':{k:{'present':k in obj, 'value':obj.get(k)} for k in ['actualModel','actualQuality']},
            'unverifiedReason':obj.get('unverifiedReason')}
def png_paths_from_hint(text):
    if not isinstance(text,str):return []
    found = re.findall(r'\bas\s+([A-Za-z]:[\\/][^\r\n]+?\.png)\b', text)
    if not found:found = re.findall(r'[A-Za-z]:[\\/][^\s"<>]+?\.png', text)
    return found
def receipt_sources(rec, record_path):
    raw = []; captured = []; receipts = []; missing = []
    def add(dest, val, origin):
        if isinstance(val,str) and val.lower().endswith('.png'):
            p = resolve(val)
            if not any(x['path']==str(p) for x in dest):dest.append({'path':str(p), 'origin':origin})
    for k in ['evidence.hostOutput','evidence.sourcePath','evidence.toolResult.sourcePath']:
        add(captured,field(rec,k),k)
    for k in ['native.sourceFile','evidence.importSourcePath']:
        v=field(rec,k)
        if isinstance(v,str) and 'generated_images' in v:add(captured,v,k)
    for k in ['evidence.toolResult.output_hint','evidence.output_hint']:
        for value in png_paths_from_hint(field(rec,k)):add(raw,value,k)
    explicit=field(rec,'evidence.receipt')
    paths=[]
    if explicit:paths.append(resolve(explicit))
    sibling=record_path.with_name(record_path.name.replace('.generation.json','.receipt.json') if record_path.name.endswith('.generation.json') else record_path.stem+'.receipt.json')
    if sibling.exists() and sibling not in paths:paths.append(sibling)
    for p in paths:
        if not p.exists():missing.append(label(p));continue
        doc=read_json(p); receipts.append({'file':label(p),'sha256':observed[str(p.resolve())]})
        hints=png_paths_from_hint(doc.get('output_hint'))
        for v in hints:add(raw,v,label(p)+':output_hint')
        # A receipt path without retained output_hint is captured metadata, not raw text.
        for k in ['nativePath','sourcePath','hostOutput']:
            add(raw if hints else captured,doc.get(k),label(p)+':'+k)
    return raw,captured,receipts,missing
def canon(im):return im.convert('RGBA').convert('RGBa')
def pixel_hash(im):
    return digest(str(im.size).encode()+b'\0'+canon(im).tobytes())

def verify_system_drawing(jobs):
    """Recreate the observed hit exporter in memory, without saving any PNG."""
    if not jobs:return {}
    encoded=base64.b64encode(json.dumps(jobs).encode('utf-8')).decode('ascii')
    script=r'''
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Drawing
$jobs=[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('__JOBS__')) | ConvertFrom-Json
function PixelHash($bmp) {
 $rect=[Drawing.Rectangle]::new(0,0,$bmp.Width,$bmp.Height)
 $bits=$bmp.LockBits($rect,[Drawing.Imaging.ImageLockMode]::ReadOnly,[Drawing.Imaging.PixelFormat]::Format32bppArgb)
 try {
  $bytes=[byte[]]::new([Math]::Abs($bits.Stride)*$bmp.Height)
  [Runtime.InteropServices.Marshal]::Copy($bits.Scan0,$bytes,0,$bytes.Length)
  $hasher=[Security.Cryptography.SHA256]::Create()
  try { return ([BitConverter]::ToString($hasher.ComputeHash($bytes))).Replace('-','').ToLowerInvariant() } finally {$hasher.Dispose()}
 } finally {$bmp.UnlockBits($bits)}
}
$results=@()
foreach($job in $jobs) {
 $native=$null;$output=$null;$g=$null;$actual=$null
 try {
  $native=[Drawing.Bitmap]::new($job.native)
  $output=[Drawing.Bitmap]::new(1024,1024,[Drawing.Imaging.PixelFormat]::Format32bppArgb)
  $g=[Drawing.Graphics]::FromImage($output)
  $g.CompositingMode=[Drawing.Drawing2D.CompositingMode]::SourceCopy
  $g.CompositingQuality=[Drawing.Drawing2D.CompositingQuality]::HighQuality
  $g.InterpolationMode=[Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
  $g.PixelOffsetMode=[Drawing.Drawing2D.PixelOffsetMode]::HighQuality
  $g.Clear([Drawing.Color]::Transparent)
  $g.DrawImage($native,[Drawing.Rectangle]::new(0,0,1024,1024),0,0,$native.Width,$native.Height,[Drawing.GraphicsUnit]::Pixel)
  $actual=[Drawing.Bitmap]::new($job.formal)
  $expectedHash=PixelHash $output;$actualHash=PixelHash $actual
  $results+=@{slot=$job.slot;expectedPixelSha256=$expectedHash;actualPixelSha256=$actualHash;match=($expectedHash -eq $actualHash)}
 } catch {$results+=@{slot=$job.slot;error=$_.Exception.Message;match=$null}}
 finally {foreach($obj in @($g,$output,$actual,$native)){if($null -ne $obj){$obj.Dispose()}}}
}
ConvertTo-Json -InputObject $results -Depth 8 -Compress
'''.replace('__JOBS__',encoded)
    result=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',script],capture_output=True,text=True,timeout=180)
    if result.returncode:raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return {v['slot']:v for v in json.loads(result.stdout.lstrip('\ufeff'))}

started=datetime.now(timezone.utc).isoformat()
slots=[]; inventory_snapshots=[]; problems=[]; evidence_gaps=[]
for name in INVENTORIES:
    if not (ROOT/name).exists():continue
    try:
        doc=read_json(ROOT/name)
        inventory_snapshots.append({'file':name,'sha256':observed[str((ROOT/name).resolve())],'frames':len(doc['frames'])})
    except Exception as exc:problems.append({'inventory':name,'code':'inventory_unreadable','detail':str(exc)})
slots=current_slots(ROOT)

expected={(a,d,n) for a,ds,count in [('hit',['E','W'],6),('attack',['E','W'],12),('cast',['E','W'],16),('run',['N','NE','E','SE','S','SW','W','NW'],16)] for d in ds for n in range(1,count+1)}
actual_keys=[(f.get('action'),f.get('direction'),f.get('frame')) for _,f in slots]
duplicate_slots=[list(k) for k,c in Counter(actual_keys).items() if c>1]
missing_slots=[list(k) for k in sorted(expected-set(actual_keys))]
unexpected_slots=[list(k) for k in sorted(set(actual_keys)-expected)]
if duplicate_slots or missing_slots or unexpected_slots:problems.append({'code':'slot_coverage','duplicates':duplicate_slots,'missing':missing_slots,'unexpected':unexpected_slots})

drawing_jobs=[]
for inv,f in slots:
    if inv!='inventory-hit.json':continue
    rec=read_json(resolve(f.get('source_record') or f['native_evidence']))
    if 'lanczos' in json.dumps(rec.get('export',{})).lower():continue
    drawing_jobs.append({'slot':f"{f['action']}/{f['direction']}/{f['frame']:02}",'native':str(resolve(rec['file'])),'formal':str(resolve(f['path']))})
try:
    drawing_results=verify_system_drawing(drawing_jobs)
    drawing_exporter_sha=file_sha(ROOT/'tools/hit_production_save.ps1')
except Exception as exc:
    drawing_results={j['slot']:{'match':None,'error':str(exc)} for j in drawing_jobs}
    drawing_exporter_sha=None

frames=[]; full_pixels=defaultdict(list); mirrored_pixels={}; file_hashes=defaultdict(list); native_hashes=defaultdict(list)
current_records={}; current_paths=set(); current_natives=set(); protected_reasons=defaultdict(set)
for inv,f in sorted(slots,key=lambda x:(str(x[1].get('action')),str(x[1].get('direction')),x[1].get('frame',0))):
    slot=f"{f.get('action')}/{f.get('direction')}/{f.get('frame'):02}"
    row={'slot':slot,'inventory':inv,'formalFile':f.get('path'),'checks':{},'problems':[],'evidenceGaps':[]}
    def check(name,value,detail=None):
        row['checks'][name]=value
        if value is False:row['problems'].append({'code':name,'detail':detail})
    try:
        p=resolve(f['path']);current_paths.add(p);protected_reasons[p].add('current_formal_slot')
        check('formalInsideCharacter',p.is_relative_to(ROOT))
        if not p.is_relative_to(ROOT):raise ValueError('formal path outside character')
        meta,im=image_info(p);row['formal']=meta
        check('formalFormat',meta['size']==[1024,1024] and meta['mode']=='RGBA' and meta['format']=='PNG',meta)
        check('trueAlpha',meta['alphaExtrema']==(0,255),meta['alphaExtrema'])
        check('inventoryShaMatchesActual',meta['sha256']==f.get('sha256'))
        file_hashes[meta['sha256']].append(slot)
        full_pixels[pixel_hash(im)].append(slot)
        mirrored_pixels[slot]=pixel_hash(ImageOps.mirror(im))
        rec_name=f.get('source_record') or f.get('native_evidence')
        check('inventoryRecordAliasesAgree',not f.get('source_record') or not f.get('native_evidence') or resolve(f['source_record'])==resolve(f['native_evidence']))
        recp=resolve(rec_name);check('recordInsideCharacter',recp.is_relative_to(ROOT))
        if not recp.is_relative_to(ROOT):raise ValueError('record outside character')
        rec=read_json(recp);current_records[recp]=(slot,rec);row['record']={'file':label(recp),'sha256':observed[str(recp)]}
        row['record']['generationTimeEvidence']={k:rec[k] for k in ['submittedAt','startedAt','generationStartedAt','generatedAt','endedAt','generatedAtEvidence','generatedAtMeaning','registeredAt'] if k in rec}
        row['modelQuality']=model_evidence(rec)
        exp=rec.get('export',{})
        check('recordExportShaMatchesActual',exp.get('sha256')==meta['sha256'])
        check('recordExportPathMatchesSlot',bool(exp.get('file')) and resolve(exp['file'])==p)
        export_size=exp.get('size') or [exp.get('width'),exp.get('height')]
        check('recordExportDimensionsMatchActual',export_size==meta['size'])
        native=rec.get('native') if isinstance(rec.get('native'),dict) else {}
        npath=native.get('file') or native.get('sourceFile') or rec.get('file')
        nsha=native.get('sha256') or rec.get('sha256')
        np=resolve(npath);current_natives.add(np);protected_reasons[np].add('current_native_source_and_pending_global_registration')
        nm,nim=image_info(np);row['native']=nm
        native_hashes[nm['sha256']].append(slot)
        claimed_dims=[native.get('width'),native.get('height')] if native else ([rec.get('nativeDimensions',{}).get('width'),rec.get('nativeDimensions',{}).get('height')] if rec.get('nativeDimensions') else [rec.get('width'),rec.get('height')])
        row['native']['recordDimensions']=claimed_dims
        check('nativeShaMatchesRecord',nm['sha256']==nsha)
        check('nativeDimensionsMatchRecord',nm['size']==claimed_dims)
        check('nativeDimensionsMatchInventory',nm['size']==f.get('native_size'))
        check('nativeAtLeast1024',min(nm['size'])>=1024 and nm['mode']=='RGBA')
        if slot in drawing_results:
            result=drawing_results.get(slot,{'match':None,'error':'no System.Drawing check result'})
            row['exportReconstruction']={'method':'System.Drawing HighQualityBicubic SourceCopy HighQuality pixel offset, whole-canvas1024, in-memory BGRA pixel comparison','exporterFile':'tools/hit_production_save.ps1','exporterSha256':drawing_exporter_sha,**result}
            check('nativeWholeCanvasDownsampleMatchesFormalPixels',result.get('match') is True,result)
        else:
            export_pixels=nim.resize((1024,1024),Image.Resampling.LANCZOS)
            row['exportReconstruction']={'method':'Pillow whole-canvas LANCZOS1024, in-memory RGBA pixel comparison'}
            check('nativeWholeCanvasDownsampleMatchesFormalPixels',export_pixels.tobytes()==im.tobytes(),'Independent Pillow whole-canvas LANCZOS reconstruction, no file written.')
        side_paths=[p.with_suffix('.png.generation.json'),p.with_suffix('.generation.json')]
        side_paths=list(dict.fromkeys(q for q in side_paths if q.exists()))
        row['sidecars']=[]
        if not side_paths:row['evidenceGaps'].append({'code':'no_adjacent_sidecar','detail':'No sidecar inferred or created; inventory→record.export is separately checked.'})
        for sp in side_paths:
            sc=read_json(sp);entry={'file':label(sp),'sha256':observed[str(sp)]};row['sidecars'].append(entry)
            check('sidecarShaMatchesActual:'+sp.name,sc.get('sha256')==meta['sha256'])
            sr=sc.get('generationRecord') or field(sc,'derivedFrom.generationRecord')
            check('sidecarRecordMatchesInventory:'+sp.name,bool(sr) and resolve(sr)==recp)
            sd=field(sc,'derivedFrom.sha256')
            check('sidecarNativeShaMatchesActual:'+sp.name,sd==nm['sha256'])
            entry['modelQuality']=model_evidence(sc)
        raw,captured,receipts,missing_receipts=receipt_sources(rec,recp)
        row['receipts']=receipts;row['hostSources']=[]
        for rp in missing_receipts:row['evidenceGaps'].append({'code':'declared_receipt_missing','file':rp})
        host_values={}
        for src in raw+captured:
            hp=resolve(src['path'])
            if hp in host_values:continue
            entry={'file':str(hp),'origin':src['origin'],'rawReceiptPath':any(x['path']==str(hp) for x in raw),'exists':hp.is_file()}
            if hp.is_file():
                entry['actualSha256']=file_sha(hp);entry['matchesNative']=entry['actualSha256']==nm['sha256']
                if not entry['matchesNative']:row['problems'].append({'code':'host_native_sha_mismatch','detail':entry})
            else:
                entry['matchesNative']=None;row['evidenceGaps'].append({'code':'host_file_missing','file':str(hp)})
            host_values[hp]=entry;row['hostSources'].append(entry)
        verified_hosts=[h for h in host_values.values() if h.get('matchesNative') is True]
        check('atLeastOneActualHostFileMatchesNative',bool(verified_hosts))
        raw_verified=[h for h in verified_hosts if h['rawReceiptPath']]
        recovery=field(rec,'evidence.recovery') or rec.get('recovery')
        row['receiptGrade']='raw_output_hint_and_actual_host_match' if raw_verified else ('inferred_recovery_mapping_actual_host_match' if recovery and verified_hosts else ('captured_host_path_actual_file_match_only' if verified_hosts else 'untraceable_host'))
        row['rawReceiptChainVerified']=bool(raw_verified)
        if not raw_verified:row['evidenceGaps'].append({'code':'raw_receipt_mapping_unconfirmed','detail':recovery or 'Raw output_hint not retained for this current record; captured path and actual file verified independently.'})
        if recovery:row['recoveryEvidence']=recovery
        if rec.get('importRecovery'):row['importRecoveryEvidence']=rec['importRecovery']
        row['recordModelQualityUnconfirmed']=rec.get('actualModel') is None and rec.get('actualQuality') is None
    except Exception as exc:row['problems'].append({'code':'read_or_schema_failure','detail':str(exc)})
    row['fileSourceChainPass']=not row['problems']
    problems.extend({'slot':slot,**e} for e in row['problems'])
    evidence_gaps.extend({'slot':slot,**e} for e in row['evidenceGaps'])
    frames.append(row)

pixel_duplicates=[s for s in full_pixels.values() if len(s)>1]
byte_duplicates=[s for s in file_hashes.values() if len(s)>1]
native_duplicates=[s for s in native_hashes.values() if len(s)>1]
mirror_pairs=set()
for slot,mh in mirrored_pixels.items():
    for other in full_pixels.get(mh,[]):
        if other!=slot:mirror_pairs.add(tuple(sorted((slot,other))))

# Cleanup is deliberately conservative. Only known rejected/superseded originals
# with a current, valid replacement are candidates. Unknown images remain held.
all_images=sorted(p.resolve() for p in ROOT.rglob('*') if p.is_file() and p.suffix.lower() in IMAGE_EXT)
for p in all_images:
    rel=p.relative_to(ROOT)
    if rel.parts[0] in ('frames','previews','preview'):protected_reasons[p].add('formal_or_preview_tree')
    if p.suffix.lower()=='.gif' or any(k in p.stem.lower() for k in ['contact','sheet','feet','crop','compare','qa','review']):protected_reasons[p].add('preview_or_review_visual_retained')

def image_refs(obj):
    if isinstance(obj,dict):
        for v in obj.values():yield from image_refs(v)
    elif isinstance(obj,list):
        for v in obj:yield from image_refs(v)
    elif isinstance(obj,str):
        if '\n' not in obj and len(obj)<1200 and Path(obj.replace('\\','/')).suffix.lower() in IMAGE_EXT:
            yield obj

# HTML and current preview data can reference non-standard review image names.
for hp in list(ROOT.rglob('*.html'))+list(ROOT.rglob('*.md'))+list(ROOT.rglob('preview-data.json')):
    try:
        text=hp.read_text(encoding='utf-8-sig')
        refs=list(image_refs(json.loads(text))) if hp.suffix=='.json' else re.findall(r'["\'(`]([^"\'<>\r\n)`]+\.(?:png|gif|webp|jpe?g))["\')`]',text,re.I)
        for ref in refs:
            for base in [hp.parent,ROOT]:
                p=resolve(ref,base)
                if p.is_relative_to(ROOT) and p.is_file():protected_reasons[p].add('current_html_or_preview_data_reference')
    except Exception:pass

current_by_slot={f['slot']:f for f in frames}
candidates_by_path=defaultdict(list); record_scan_errors=[]
for rp in sorted((ROOT/'records').glob('*.json')):
    if rp in current_records or rp.name.endswith(('.receipt.json','.submitted.json')):continue
    try:
        doc=read_json(rp)
        if not isinstance(doc,dict) or doc.get('tool')!='image_gen.imagegen':continue
        native=doc.get('native') if isinstance(doc.get('native'),dict) else {}
        paths=[]
        for value in [native.get('file'),native.get('sourceFile'),doc.get('file')]+doc.get('outputFiles',[]):
            if isinstance(value,str) and Path(value).suffix.lower() in IMAGE_EXT:
                p=resolve(value)
                if p.is_relative_to(ROOT) and p.is_file():paths.append(p)
        slot=doc.get('slot') or doc.get('requested_slot')
        if not slot and all(k in doc for k in ('action','direction','frame')):slot=f"{doc['action']}/{doc['direction']}/{int(doc['frame']):02}"
        if not slot and field(doc,'export.file'):
            parts=Path(str(field(doc,'export.file')).replace('\\','/')).parts
            if len(parts)==4 and parts[0]=='frames':slot='/'.join(parts[1:3])+'/'+Path(parts[3]).stem
        current=current_by_slot.get(slot)
        status=str(doc.get('status','')).lower();qa=str(field(doc,'visualQA.status') or '').lower()
        rejected=any(x in status or x in qa for x in ('reject','superseded'))
        replaced=bool(current and current['fileSourceChainPass'] and field(doc,'export.sha256') and field(doc,'export.sha256')!=current.get('formal',{}).get('sha256'))
        eligible=bool(current and current['fileSourceChainPass'] and (rejected or replaced))
        for p in dict.fromkeys(paths):
            if eligible:candidates_by_path[p].append({'sourceRecord':label(rp),'slot':slot,'status':doc.get('status'),'reason':'explicit_rejection_or_supersession' if rejected else 'export_replaced_by_current_inventory','currentReplacement':current['formalFile'],'currentReplacementSha256':current['formal']['sha256']})
            else:protected_reasons[p].add('possible_only_work_in_progress_or_no_verified_replacement')
    except Exception as exc:record_scan_errors.append({'file':label(rp),'error':str(exc)})

cleanup=[]; held=[]
for p in all_images:
    if p in candidates_by_path and not protected_reasons[p]:
        cleanup.append({'file':label(p),'sha256':file_sha(p),'bytes':p.stat().st_size,'evidence':candidates_by_path[p],'deletionAuthorized':False})
    elif p not in current_paths:
        held.append({'file':label(p),'reasons':sorted(protected_reasons[p]) or ['unclassified_image_preserved_not_a_cleanup_candidate']})

changed=[]
for name,before in observed.items():
    p=Path(name)
    try:after=digest(p.read_bytes())
    except Exception as exc:after='unreadable:'+str(exc)
    if before!=after:changed.append({'file':label(p),'beforeSha256':before,'afterSha256':after})

report={'schema':1,'character':'02_fire_talisman_boy','startedAtUtc':started,'finishedAtUtc':datetime.now(timezone.utc).isoformat(),
 'scope':'five current private inventories; no image mutation, no Git action, only this JSON output',
 'inputInventories':inventory_snapshots,'expectedSlots':196,'actualInventoryEntries':len(slots),'missingSlots':missing_slots,'duplicateSlots':duplicate_slots,'unexpectedSlots':unexpected_slots,
 'summary':{'fileSourceChainPassCount':sum(f['fileSourceChainPass'] for f in frames),'rawReceiptChainVerifiedCount':sum(f.get('rawReceiptChainVerified',False) for f in frames),'adjacentSidecarPresentCount':sum(bool(f.get('sidecars')) for f in frames),'actualModelAndQualityUnconfirmedCount':sum(f.get('recordModelQualityUnconfirmed',False) for f in frames),'problemCount':len(problems),'evidenceGapCount':len(evidence_gaps),'snapshotStable':not changed,'cleanupCandidateCount':len(cleanup),'cleanupCandidateBytes':sum(p['bytes'] for p in cleanup)},
 'receiptEvidenceGrades':dict(Counter(f.get('receiptGrade','not_reached') for f in frames)),
 'pass':not problems and not changed and len(slots)==196 and not pixel_duplicates and not mirror_pairs and not native_duplicates,
 'rawReceiptMappingComplete':len(frames)==196 and all(f.get('rawReceiptChainVerified',False) for f in frames),
 'adjacentSidecarsComplete':len(frames)==196 and all(f.get('sidecars') for f in frames),
 'passMeaning':'Actual file/record/source integrity only. Does not mean every raw receipt was retained, sidecars all exist, anatomy passes, model/quality confirmed or client integration complete.',
 'frames':frames,'problems':problems,'evidenceGaps':evidence_gaps,'inputsChangedDuringAudit':changed,
 'duplicateDiagnostics':{'method':'Exact complete1024canvas premultiplied RGBA pixels; zero-alpha hidden RGB ignored. Horizontal mirror is evaluated only in memory, no file written. Native SHA reuse across different current slots is also checked. No approximate pose/mirror inference.','byteIdenticalGroups':byte_duplicates,'pixelIdenticalGroups':pixel_duplicates,'horizontalPixelMirrorPairs':[list(x) for x in sorted(mirror_pairs)],'sharedNativeShaGroups':native_duplicates},
 'cleanup':{'mode':'candidate_list_only_no_deletion','requiresRootReviewAndFreshAudit':True,'rules':['Only resolved paths inside02 are considered.','Current formal frames, current native sources, previews, known review visuals and possible unique work in progress are excluded.','Only prior generation images with explicit rejection/supersession or an exported replacement in a currently verified slot are suggested.','Unknown images are retained; text provenance is never listed for deletion.','Do not execute from a stale snapshot; active generation can add references after the scan.'],'candidates':cleanup,'heldNonFormalImages':held,'recordScanErrors':record_scan_errors},
 'limitations':['Host file hashes verify saved bytes; original raw output_hint is separately graded and never reconstructed.','N09 inferred recovery, if still current, remains explicitly distinguishable from a receipt-verified call.','No server-side model/quality claim is inferred from configured target or prompt.','No client is launched and no visual or dynamic approval is issued.']}
OUTPUT.parent.mkdir(parents=True,exist_ok=True)
OUTPUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'output':label(OUTPUT),'pass':report['pass'],'summary':report['summary'],'receiptEvidenceGrades':report['receiptEvidenceGrades'],'problems':problems,'duplicates':report['duplicateDiagnostics'],'changed':changed},ensure_ascii=True))
