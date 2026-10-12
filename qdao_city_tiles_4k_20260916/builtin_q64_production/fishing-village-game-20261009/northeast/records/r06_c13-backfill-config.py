from pathlib import Path
import json,hashlib,datetime
B=Path(__file__).resolve().parent.parent
C=Path('D:/work/image/config/image-generation.json');snapshot=json.loads(C.read_text(encoding='utf-8-sig'));now=datetime.datetime.now(datetime.timezone.utc).isoformat();changed=[]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
for p in sorted((B/'native').glob('r06_c13*.png.generation.json')):
 d=json.loads(p.read_text(encoding='utf-8'))
 if 'configSnapshot' in d:continue
 old=sha(p);d.update({'configSnapshot':snapshot,'configSource':{'path':str(C),'sha256':sha(C),'role':'configured target only, not actual submitted selector'},'configSnapshotCaptureStage':'retrospective_metadata_backfill_after_generation; prior exact bytes not separately snapshotted','configSnapshotRecordedAtUtc':now})
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');changed.append({'file':str(p),'oldSha256':old,'newSha256':sha(p)})
(B/'records/r06_c13-config-backfill-log.json').write_text(json.dumps({'recordedAtUtc':now,'scope':'only this task new r06_c13 generated records','reason':'add recovered config target evidence, not actual model/quality','changes':changed},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'updated':len(changed)}))
