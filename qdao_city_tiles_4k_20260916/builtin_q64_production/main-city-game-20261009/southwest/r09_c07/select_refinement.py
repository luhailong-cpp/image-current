import sys,json,hashlib,shutil,re
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
sys.dont_write_bytecode=True
SW=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(SW))
import native_pipeline as n
tile,pid,version,request,receipt,source=sys.argv[1:]
tr,tc=n.tile_numbers(tile);assert 9<=tr<=16 and 7<=tc<=8
assert re.fullmatch(r'[A-Za-z0-9_-]+',version)
row,col=map(int,[pid[1:3],pid[4:6]])
p=n.Pipeline(tile);t=SW/tile
oldpath,_=p.selected_record(tile,row,col);base=json.loads(oldpath.read_text(encoding='utf-8-sig'))
req=json.loads(Path(request).read_text(encoding='utf-8-sig'));rc=json.loads(Path(receipt).read_text(encoding='utf-8-sig'))
assert rc['status']=='returned_image' and Path(rc['sourceOutputPath']).resolve()==Path(source).resolve()
def sha(v):return hashlib.sha256(Path(v).read_bytes()).hexdigest()
dest=t/'refinement'/'versions'/version/f'{pid}.png';assert not dest.exists()
dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
with Image.open(dest) as im:
 assert im.size==(1254,1254) and im.format=='PNG' and im.mode in ('RGB','RGBA')
 assert im.mode!='RGBA' or im.getextrema()[3]==(255,255)
 meta={key:str(value)[:4000] for key,value in im.info.items()};mode=im.mode
record=base.copy()
record.update(file=str(dest),sha256=sha(dest),generatedAt=datetime.now(timezone.utc).isoformat(),mode=mode,
 evidence={'toolReceipt':str(Path(receipt)),'toolReceiptSha256':sha(receipt),'pngMetadata':meta},
 prompt=req['promptFile'],promptSha256=req['promptSha256'],request=str(Path(request)),requestSha256=sha(request),
 references=req['references'],neighborSources=req.get('neighborSources',[]),cornerTreatment=req.get('cornerTreatment'),
 sourceOutputPath=str(Path(source)),sourceOutputSha256=sha(source),actualModel=None,actualQuality=None,formalAccepted=False,
 visualStatus='selected_refinement_pending_QA',priorGenerationRecord=str(oldpath),priorGenerationRecordSha256=sha(oldpath))
recordpath=dest.with_name(dest.name+'.generation.json');recordpath.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
p.native_record(tile,row,col,(recordpath,None))
selection=t/'refinement/selection.json';sel=json.loads(selection.read_text()) if selection.exists() else {}
if selection.exists():shutil.copy2(selection,dest.parent/f'{pid}.selection-before.json')
sel[pid]=recordpath.relative_to(t).as_posix();selection.write_text(json.dumps(sel,ensure_ascii=False,indent=2),encoding='utf-8')
p2=n.Pipeline(tile);p2.native_record(tile,row,col,p2.selected_record(tile,row,col))
print(json.dumps({'status':'selected_refinement_pending_QA','file':str(dest),'sha256':sha(dest),'selection':str(selection),'formalAccepted':False}))
