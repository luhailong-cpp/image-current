from pathlib import Path
from PIL import Image
import json,hashlib,shutil
B=Path(__file__).resolve().parent;D=B/'attempt-01';sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
host=Path(r'C:/Users/luyua/.codex/generated_images/01a13608-efaf-7310-8b30-7b4f9396f5ed/exec-92b796d0-b140-4542-9a81-932d9a05c87e.png');out=D/'native.png';assert not out.exists();shutil.copyfile(host,out);assert sha(host)==sha(out)
src=Image.open(out).convert('RGB');base=Image.open(B/'edit-target.png').convert('RGB');assert src.size==(1254,1254)
(D/'generation.json').write_text(json.dumps({'native':str(out),'sha256':sha(out),'host':str(host),'hostByteIdentical':True,'size':list(src.size),'worldBox':[9613,19226,10867,20480],'actualModel':None,'actualQuality':None,'entry':'image_gen__imagegen','adopted':False},indent=2))
roi=[350,300,950,1254];trial=base.copy();trial.paste(src.crop(roi),roi[:2]);trial.save(D/'roi-trial.png')
for n,b in [('left-gold',[300,300,420,725]),('right-gold',[875,400,1020,920]),('left-tiles',[300,690,420,1254]),('right-tiles',[875,800,1020,1254]),('top',[320,260,980,340])]:trial.crop(b).save(D/(n+'.png'))
print({'sha256':sha(out),'roi':roi})

