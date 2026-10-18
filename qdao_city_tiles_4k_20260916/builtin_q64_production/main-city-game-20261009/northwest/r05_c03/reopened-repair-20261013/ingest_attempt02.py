from pathlib import Path
from PIL import Image
import json,hashlib,shutil
B=Path(__file__).resolve().parent;D=B/'attempt-02';sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
host=Path(r'C:/Users/luyua/.codex/generated_images/01a13608-efaf-7310-8b30-7b4f9396f5ed/exec-afd92c1d-675b-40f9-b290-ff3b2fdf229a.png');out=D/'native.png';assert not out.exists();shutil.copyfile(host,out);assert sha(host)==sha(out)
src=Image.open(out).convert('RGB');base=Image.open(B/'edit-target.png').convert('RGB');assert src.size==(1254,1254)
(D/'generation.json').write_text(json.dumps({'native':str(out),'sha256':sha(out),'host':str(host),'hostByteIdentical':True,'size':list(src.size),'worldBox':[9613,19226,10867,20480],'actualModel':None,'actualQuality':None,'entry':'image_gen__imagegen','adopted':False},indent=2))
roi=[280,310,1010,1254];trial=base.copy();trial.paste(src.crop(roi),roi[:2]);trial.save(D/'roi-trial.png')
for n,b in [('left-gold',[230,285,340,710]),('right-gold',[940,425,1080,970]),('left-tiles',[230,690,340,1254]),('right-tiles',[940,780,1080,1254]),('top',[250,280,1040,340]),('south',[250,1184,1040,1254])]:trial.crop(b).save(D/(n+'.png'))
print({'sha256':sha(out),'roi':roi})

