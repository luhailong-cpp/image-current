from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, re
ROOT=Path(__file__).resolve().parents[1]
WORKSPACE=Path('D:/work/image')
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def meta(p):
    p=Path(p)
    return {'path':p.as_posix(),'exists':p.exists(),**({'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} if p.is_file() else {})}
index=ROOT/'qa'/'expansion-west-worker-map.json';d=load(index)
selected={t:d[t] for t in d['assignedTiles']}
missing=[{'tile':t,'subrow':r+1,'subcolumn':c+1} for t,m in selected.items() for r,row in enumerate(m) for c,s in enumerate(row) if not s]
selected_stems={s for m in selected.values() for row in m for s in row if s}
native=[];references={};external_tool_sources=[];bad=[]
for rp in sorted((ROOT/'native').glob('*.png.generation.json')):
    stem=rp.name.removesuffix('.png.generation.json')
    if not re.fullmatch(r'r(?:09|10|11|12|13|14)_c0[12]_s\d{2}_\d{2}_v\d{2}',stem):continue
    rec=load(rp);n=meta(ROOT/'native'/(stem+'.png'))
    valid=n.get('sha256')==rec.get('sha256')
    if not valid:bad.append(stem)
    native.append({'stem':stem,'selected':stem in selected_stems,'native':n,'generationRecord':meta(rp),'recordHashMatchesImage':valid,'receipt':meta(ROOT/'receipts'/(stem+'.tool.json'))})
    for ref in rec.get('references',[]):references[ref['path']]=meta(ref['path'])
    sp=rec.get('sourceToolPath')
    if sp:external_tool_sources.append({'stem':stem,'toolOriginal':meta(sp),'workspaceNativeCopy':n,'identicalOriginalAndNative':Path(sp).is_file() and hashlib.sha256(Path(sp).read_bytes()).hexdigest()==n.get('sha256')})
req=ROOT/'prompts'/(d['currentRequest']+'.request.json')
if req.exists():
    for ref in load(req).get('references',[]):references[ref['path']]=meta(ref['path'])
prepared_not_generated=[p.stem.removesuffix('.request') for p in (ROOT/'prompts').glob('r*_c0[12]_s*_v*.request.json') if re.fullmatch(r'r(?:09|10|11|12|13|14)_c0[12]_s\d{2}_\d{2}_v\d{2}',p.stem.removesuffix('.request')) and not (ROOT/'native'/(p.stem.removesuffix('.request')+'.png')).exists()]
out={
'status':'frozen_for_migration','recordedAtUtc':datetime.now(timezone.utc).isoformat(),
'stopConfirmedAtUtc':'2026-10-12T02:48:09Z','lastWorkerMutationBeforeFreezeUtc':d.get('updatedAtUtc'),
'stopReason':'User requested commit/push and move to another computer; parent ordered no new generation, repair or expansion requests.',
'newRequestsForbiddenUntilUserResumes':True,'generationInFlight':False,'unsavedSuccessfulToolResults':False,
'lifecycleEvidence':'Last invoked image_gen returned r10_c02_s03_03_v01; receipt, native copy, generation record and selected map were saved. r10_c02_s04_03_v01 was only prepared/annotated/viewed and was never submitted. No live exec/image generation cell remains.',
'assignedTiles':d['assignedTiles'],'selectedNativeCount':len(selected_stems),'successfulNativeFilesRetained':len(native),'selectedMap':meta(index),'selectedArraySnapshot':selected,
'candidateArtifacts':d['candidateArtifacts'],'nativeInventory':native,'missingCoreCount':len(missing),'missingCores':missing,
'preparedNotSubmitted':prepared_not_generated,'nextResumeRequest':meta(req),
'nextResumeAction':'Re-read and view the existing r10_c02_s04_03_v01 guide and mandatory refs, then submit this saved request exactly once after user resumes. Continue r10_c02 columns 2 and 1; r09_c02 already has 16 native cores but pending local repairs.',
'pendingRepairReview':meta(ROOT/'qa'/'c04-hardseam-west-r09c02-v01-review.json'),
'rootIndependentReview':meta(ROOT/'qa'/'expansion-west-root-r11c03-review.json'),
'workspaceReferences':list(references.values()),
'outsideWorkspaceReferencesRequiredForImageContent':[v for k,v in references.items() if not Path(k).resolve().is_relative_to(WORKSPACE.resolve())],
'outsideWorkspaceToolOriginals':external_tool_sources,
'outsideWorkspaceRuntime':{'python':'C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe','requiredForFutureScripts':['Python','Pillow','NumPy'],'note':'Runtime is environmental, not image content. Reinstall or resolve equivalent runtime on new computer.'},
'migrationNotes':['Preserve all 25 generated native files including 2 rejected initial attempts, all generation records, prompts, guides/derivations, receipts, QA crops, previews, masks and helper scripts.','All external tool originals have byte-identical workspace native copies; preserve tool cache originals separately if migrating the whole raw cache.','Mandatory artwork references are inside D:/work/image but outside southwest; include their actual files in migration.','Do not count r09_c02 candidate as final accepted: internal repairs and remaining external perimeter are pending.','Main map/progress and accepted 4-tile group were not modified by this worker. No Git, upload or deletion performed.'],
'verificationErrors':bad,'childTasks':[]}
dest=ROOT/'qa'/'expansion-west-migration-freeze-20261011.json'
dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'freeze':str(dest),'inFlight':False,'unsavedSuccess':False,'nativeFiles':len(native),'selected':len(selected_stems),'missing':len(missing),'preparedNotSubmitted':prepared_not_generated,'verificationErrors':bad,'externalArtworkReferences':len(out['outsideWorkspaceReferencesRequiredForImageContent']),'toolOriginalsWithIdenticalNativeCopy':sum(x['identicalOriginalAndNative'] for x in external_tool_sources)}))

