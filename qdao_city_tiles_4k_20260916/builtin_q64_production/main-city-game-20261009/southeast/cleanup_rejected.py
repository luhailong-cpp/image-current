from pathlib import Path
import json,hashlib,datetime
B=Path(__file__).resolve().parent;T=B/'r13_c13';N=T/'native'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
active=read(T/'active-native-map.json');protected=set()
for name in active.values():
    rec=read(N/f'{name}.png.generation.json')
    protected.add((N/f'{name}.png').resolve())
    for ref in rec['references']:protected.add(Path(ref['path']).resolve())
removed=[];root=B.resolve()
for id in ['p01_02','p02_01','p02_02','p03_01']:
    target=(N/f'{id}.png').resolve();assert target.is_relative_to(root) and target not in protected
    recpath=N/f'{id}.png.generation.json';rec=read(recpath);assert rec['status'].startswith('rejected_')
    assert sha(target)==rec['sha256']
    item={'file':str(target),'sha256':sha(target),'bytes':target.stat().st_size,'reason':rec['status'],'generationRecordRetained':str(recpath)}
    target.unlink();removed.append(item)
    rec['imageDisposition']='deleted_rejected_image_text_provenance_retained';rec['deletedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat();write(recpath,rec)
write(B/'cleanup-record.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'only four unreferenced rejected PNGs inside owned southeast directory','removed':removed,'otherScopeFilesDeleted':False,'currentInProgressSourcesRetained':'16 active core patches, two actual reference sources used by current generation records, six native repair outputs and exact replay inputs; formal export not yet accepted'})
pr=read(B/'progress.json');pr['rejectedImageFilesDeleted']=len(removed);pr['nativePatchImageFilesPresent']=len(list(N.glob('*.png')));write(B/'progress.json',pr)
print(json.dumps({'rejectedImagesDeleted':len(removed),'currentNativePatchImages':pr['nativePatchImageFilesPresent'],'generationTextRecordsRetained':True}))

