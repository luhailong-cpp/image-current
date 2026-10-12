import sys
sys.dont_write_bytecode=True
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
import numpy as np
from PIL import Image
Q=Path(__file__).resolve().parent; Z=Q.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':Path(p).as_posix(),'sha256':sha(p)}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
a=read(Q/'full-tile-r10_c05-assembly.json')
j=read(Q/'joint-r09c05-r10c05-v1-trace.json')
selected=[]
for s in a['sources']:
    assert sha(s['path'])==s['sha256'] and sha(s['record'])==s['recordSha256']
    im=Image.open(s['path']);assert im.size==(1254,1254)
    r=read(s['record']);assert r['actualModel'] is None and r['actualQuality'] is None
    selected.append({'patch':s['patch'],'version':s['version'],**ref(s['path']),'record':ref(s['record'])})
new=[]
for c in range(1,5):
    stem=f'r10_c05_p04_{c:02d}_v1'; p=Z/'native'/(stem+'.png');r=read(str(p)+'.generation.json')
    req=read(Z/'native'/(stem+'.request.json'));rec=read(Z/'native'/(stem+'.receipt.json'))
    assert len(req['references'])==len(r['references'])==4
    for inp in r['references']: assert sha(inp['path'])==inp['sha256']
    assert req['references'][-1]['path'].endswith('mail-daoist-style.jpg')
    assert rec['result']['output_hint'] and Path(r['prompt']).is_file()
    new.append({'stem':stem,**ref(p),'dimensions':[1254,1254],'request':ref(Z/'native'/(stem+'.request.json')),'prompt':ref(r['prompt']),'receipt':ref(Z/'native'/(stem+'.receipt.json')),'record':ref(str(p)+'.generation.json'),'allActualReferencesVerified':True,'actualModel':None,'actualQuality':None})
base=np.array(Image.open(a['context']['path']).convert('RGB'))
low=j['tiles'][1]
current=np.array(Image.open(low['context']['path']).convert('RGB'))
assert np.array_equal(base[230:],current[230:])
assert np.array_equal(current[115:4211,115:4211],np.array(Image.open(low['candidate']['path']).convert('RGB')))
internal=[]
for q in a['qa']:
    assert sha(q['file'])==q['sha256']
    internal.append({'path':q['file'],'sha256':q['sha256'],'viewedAtNativeScale':True,'result':'pass_internal_art_continuity'})
assert len(internal)==39
north=[]
for q in j['qa']:
    assert sha(q['path'])==q['sha256']
    north.append({**q,'viewedAtNativeScale':True,'result':'pass_shared_edge_art_continuity'})
report={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'task':'Resume r10_c05 last row, internal QA and north joint','tile':'r10_c05','newNativeCount':4,'currentNativeCoreCoverage':'16/16','nativeResampled':False,'newNativeSources':new,'selectedSources':selected,'baseAssembly':ref(Q/'full-tile-r10_c05-assembly.json'),'jointTrace':ref(Q/'joint-r09c05-r10c05-v1-trace.json'),'effectiveContext':low['context'],'effectiveCandidate':low['candidate'],'northNeighborEffectiveContext':j['tiles'][0]['context'],'northNeighborEffectiveCandidate':j['tiles'][0]['candidate'],'completeJointContext':j['context'],'internalQa':internal,'northQa':north,'qaStatus':{'internal39Passed':True,'north5Passed':True,'westPendingCurrentStairRebuild':True,'eastAndSouthAdjacentTilesNotYetAvailable':True,'formalWholeTileAccepted':False},'findings':[{'topic':'parasol','severity':'minor_observation','detail':'One continuous golden canopy and one finial, consistent panel seams and support. Compared with the coarse overview-derived guide the contour has roughly 200 native px expansion/offset in places (about 4.4 overview px). It occupies the same stall/tree location and observed upper/right road stays open; no unnecessary full umbrella regeneration. Rabbit ears remain intentionally cropped at bottom/right awaiting adjacent tiles.'},{'topic':'foliage','severity':'minor_observation','detail':'Single continuous osmanthus crown with organic leaf-size variation; no broken branch, hard division, duplicated whole tree or extra trunk.'},{'topic':'pavement','severity':'minor_observation','detail':'Grey paving has irregular slab size and direction inherited from existing patches; shared native joins inspected without gaps or visible straight cuts. No red paving or added blocking props.'},{'topic':'north_post','severity':'resolved','detail':'Canonical hard cut showed a horizontal wood grain/tone band. 230px minimum-error hard overlap with finalrail upper source resolves it; reviewed 5 native edge strips and 1254 post crop. No additional AI image needed.'}],'verification':{'selectedNativeHashesAndDimensionsValid':True,'allFourNewPromptsReceiptsReferencesAndRecordsPresent':True,'actualToolModelQualityUnexposedRecordedNull':True,'afterNorthJoinOnlyFirst230ContextRowsMayDiffer':True,'allBelow230ContextRowsIdenticalTo16SourceBase':True,'effective4096IsExactIntegerCrop':True,'allPixelsNativeSourceSelectedNoResizeNoFeather':True},'nextStep':'Use effective north-joined contexts for c04/c05 2x2 closure; west edge check after stair rebuild. Lower adjacent tile should continue same tree, single parasol pole and two rabbit ears; do not recreate whole umbrella or rabbit here.','scope':'Art and source provenance only; no runtime, engine, capacity or client tests','filesModifiedOutsideSouthwest':False,'exportedToCanonicalTiles':False}
p=Q/'r10_c05-resume-handoff.json';p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'handoff':ref(p),'newNative':4,'currentCoverage':16,'internalQaPassed':39,'northQaPassed':5,'effectiveContext':low['context'],'effectiveCandidate':low['candidate']},ensure_ascii=False))
