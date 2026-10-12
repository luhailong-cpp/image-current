"""Refresh factual production counts without granting visual acceptance."""
from pathlib import Path
from datetime import datetime,timezone
import json
z=Path(__file__).resolve().parent
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
p=read(z/'progress.json')
tiles=[]
for t in sorted(z.glob('r??_c??')):
    generated_records=list(t.rglob('*.png.generation.json'))
    native=[g for g in generated_records if Path(str(g)[:-16]).exists()]
    selection=t/'selected-patches.json'
    if not selection.exists() and t.name=='r10_c09': selection=z/'selected-patches.json'
    selected_data=read(selection) if selection.exists() else {}
    selected=selected_data.get('patches',{})
    tp=read(t/'progress.json') if (t/'progress.json').exists() else {}
    candidate=selected_data.get('candidate')
    if isinstance(candidate,dict): candidate=candidate.get('file')
    candidates=[Path(candidate)] if candidate else []
    candidates+=list(t.glob('*candidate-4096.png'))+list((t/'candidate').glob('*4096.png'))
    assembled=len(selected)==16 and any(f.exists() for f in candidates)
    internal=selected_data.get('internalReady',False)
    tiles.append({'tile':t.name,'generatedNativeCount':len(native),'selectedPatchPositions':len(selected),'targetPatchPositions':16,'selectedManifest':str(selection) if selection.exists() else None,'status':selected_data.get('status',tp.get('status','native_candidates_in_progress')),'assembled4kCandidate':assembled,'internalReady':internal,'formalAccepted':False})
p.update(updatedAt=datetime.now(timezone.utc).isoformat(),generatedNativeCount=sum(t['generatedNativeCount'] for t in tiles),selectedNativePositions=sum(t['selectedPatchPositions'] for t in tiles),activeTiles=tiles,status='native_generation_and_seam_QA_in_progress',currentTile='r10_c08',currentPatch=None,nextStep='Root: finish r10_c08 internal QA and neighboring seams; workers: extend south columns09/10; complete all49 southeast tiles and formal external-seam review')
p.pop('usableNativeCount',None)
for e in p.get('actualErrors',[]):
    pid=e.get('patch')
    replacement={'p12-v2':'p12-v3','p14-v1':'p14-v3','p14-v2':'p14-v3','p22-v1':'p22-v2','p23-v1':'p23-v2','p24-v1':'p24-v2','p34-v1':'p34-v2','p44-v1':'p44-v3'}.get(pid)
    e['tile']='r10_c09'
    if replacement: e['resolution']='Replaced by '+replacement+'; first tile internal QA now passed, external missing neighbors pending'
p['complete4kCount']=0
p['formalAcceptedCount']=0
p['assembled4kCandidateCount']=sum(t['assembled4kCandidate'] for t in tiles)
p['internallyReviewed4kCount']=sum(t['internalReady'] for t in tiles)
p['target4kCount']=49
p['newImageGenerationAllowed']=True
p['runtimeWorkRequested']=False
p.pop('inFlightStatus',None)
gate_path=z.parent.parent/'capacity-layout-gate-20261010.json'
if gate_path.exists():
    gate=read(gate_path)
    if gate.get('holdGenerationAtNewCoordinates'):
        p.update(status='capacity_gate_active_existing_art_QA_only',newImageGenerationAllowed=False,gate=str(gate_path),nextStep='Wait for main-chat layout/scale gate release and missing mandatory style/config source resolution; meanwhile only existing-art QA and mechanical assembly')
        p['inFlightStatus']='none'
        p['currentTile']=None
p['tilesWithoutComplete4kCandidate']=49-p['assembled4kCandidateCount']
p['missingSelectedPatchPositions']=49*16-p['selectedNativePositions']
index=[]
for row in range(8,15):
    for col in range(8,15):
        name=f'r{row:02d}_c{col:02d}'
        active=next((a for a in tiles if a['tile']==name),None)
        index.append({'tile':name,'row':row,'column':col,'coreBox':[(col-1)*4096,(row-1)*4096,col*4096,row*4096],'status':active['status'] if active else 'not_generated','generatedNativeCount':active['generatedNativeCount'] if active else 0,'selectedPatchPositions':active['selectedPatchPositions'] if active else 0,'formalAccepted':False})
(z/'production-index.json').write_text(json.dumps({'zone':'southeast','target4kCount':49,'tilePixels':[4096,4096],'tiles':index,'all49Complete':False,'updatedAt':p['updatedAt']},ensure_ascii=False,indent=2),encoding='utf-8')
(z/'progress.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'generatedNativeCount':p['generatedNativeCount'],'selectedNativePositions':p['selectedNativePositions'],'tiles':tiles,'complete4kCount':0,'formalAcceptedCount':0},ensure_ascii=False,indent=2))

