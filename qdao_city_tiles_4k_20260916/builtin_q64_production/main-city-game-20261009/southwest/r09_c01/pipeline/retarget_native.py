from pathlib import Path
import sys,json,hashlib,shutil
q=Path(sys.argv[1]); target=Path(sys.argv[2]); content=Path(sys.argv[3])
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
d=json.loads(q.read_text(encoding='utf-8-sig'))
backup=q.with_name(q.name.replace('.request.json','.pre-native-edit.request.json'));assert not backup.exists();shutil.copy2(q,backup)
prompt=content.read_text(encoding='utf-8-sig'); f=q.with_name(q.name.replace('.request.json','.native-edit-prompt.txt'));assert not f.exists();f.write_text(prompt,encoding='utf-8')
d.update(prompt=prompt,promptFile=str(f),promptSha256=h(f),nativeEditTarget=True)
d['referenced_image_paths'][0]=str(target)
d['references'][0]={'file':str(target),'sha256':h(target),'role':'exact previous native output, narrow corrective edit target'}
q.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(str(q))
