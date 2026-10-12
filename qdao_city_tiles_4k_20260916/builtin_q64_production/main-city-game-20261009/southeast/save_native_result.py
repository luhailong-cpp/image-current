"""Record a truthful builtin result, ingest without resizing, update resume."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib,subprocess,sys,os,uuid
from PIL import Image

Z=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,o):
    p=Path(p);temp=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp')
    temp.write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8');os.replace(temp,p)
parser=argparse.ArgumentParser();parser.add_argument('tile');parser.add_argument('version');parser.add_argument('source');args=parser.parse_args()
source=Path(args.source)
with Image.open(source) as im:
    size=list(im.size);assert im.format=='PNG' and size==[1254,1254]
now=datetime.now(timezone.utc).isoformat()
receipt=Z/args.tile/'records'/(args.version+'.receipt.json')
assert not receipt.exists()
write(receipt,{'status':'succeeded_pending_native_seam_review','tool':'image_gen.imagegen','generatedAt':now,
 'originalOutput':str(source),'outputSha256':sha(source),'actualSize':size,'actualModel':None,'actualQuality':None,
 'resizedAfterGeneration':False,'finalArtUpscaled':False,'evidence':'Builtin tool returned this PNG path in output_hint. Actual dimensions measured from the saved original.'})
cmd=[sys.executable,str(Z/'production_workflow.py'),'ingest',args.tile,args.version,str(source),str(receipt)]
result=subprocess.run(cmd,text=True,capture_output=True,check=True)
ingested=json.loads(result.stdout)
resume_path=Z/'production-resume-20261012.json';resume=read(resume_path)
new={'savedAtUtc':now,**ingested,'tool':'image_gen.imagegen','actualSize':size,'originalOutput':str(source),'receipt':str(receipt),'receiptSha256':sha(receipt)}
if not resume.get('firstNewOutput'):resume['firstNewOutput']=new
resume.setdefault('savedNewNativeOutputs',[]).append(new)
resume.update(updatedAtUtc=now,status='builtin_new_output_saved_and_native_production_continuing',generationStopped=False,
 currentRootCoordinate=args.tile+'/'+(ingested['nextPatch'] or 'assembly'),networkStatus='builtin_imagegen_succeeded_after_resume',
 gitOperationsPerformed=False,sourceDeletionPerformed=False)
write(resume_path,resume)
print(json.dumps(new))
