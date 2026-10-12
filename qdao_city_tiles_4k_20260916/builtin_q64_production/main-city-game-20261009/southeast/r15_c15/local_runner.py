"""Tile-local orchestration; no image generation or shared writes."""
from pathlib import Path
import sys,json,hashlib,datetime,importlib.util
from PIL import Image
T=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('production_workflow',T.parent/'production_workflow.py')
w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def dump(p,v): w.atomic_json(p,v)
if not w.CONFIG.exists():
    source=T.parent/'r15_c14/records/config-carried-snapshot-20261012.json'
    snapshot=T/'records/config-carried-snapshot-20261013.json'
    if not snapshot.exists():
        snapshot.write_bytes(source.read_bytes())
        dump(T/'records/config-snapshot-origin-20261013.json',{'status':'historical_preference_snapshot_only_not_backend_claim','missingPath':str(w.CONFIG),'source':str(source),'sourceSha256':w.sha(source),'snapshotSha256':w.sha(snapshot),'actualModel':None,'actualQuality':None,'recordedAt':now()})
    w.CONFIG=snapshot
command=sys.argv[1]
if command=='prepare': result=w.prepare(T.name,sys.argv[2],sys.argv[3] if len(sys.argv)>3 else None)
elif command=='ingest':
    version,source=sys.argv[2],Path(sys.argv[3]).resolve()
    assert Image.open(source).format=='PNG' and Image.open(source).size==(1254,1254)
    receipt=T/'records'/(version+'.receipt.json')
    assert not receipt.exists()
    dump(receipt,{'tool':'image_gen.imagegen','route':'builtin','status':'succeeded_pending_visual_qa','generatedAt':now(),'originalOutputPath':str(source),'sourceSha256':w.sha(source),'actualSize':[1254,1254],'actualModel':None,'actualQuality':None,'resizedAfterGeneration':False,'finalArtUpscaled':False})
    result=w.ingest(T.name,version,str(source),str(receipt))
    path=T/'production-resume-20261013.json'
    record=json.loads(path.read_text()) if path.exists() else {'tile':T.name,'startedAt':now(),'firstNewOutput':{'source':str(source),'sha256':w.sha(source),'version':version},'actualModel':None,'actualQuality':None,'formalAccepted':False}
    record.update({'status':'native_generation_in_progress','lastNativeIngestedAt':now(),'nativeGenerationCalls':len(list((T/'records').glob('*.receipt.json'))),'activeNativeCount':len(json.loads((T/'active-native-map.json').read_text())),'inFlightImageGenCount':0})
    dump(path,record)
elif command=='assemble':result=w.assemble(T.name)
else:raise ValueError(command)
print(json.dumps(result,ensure_ascii=False,indent=2))
