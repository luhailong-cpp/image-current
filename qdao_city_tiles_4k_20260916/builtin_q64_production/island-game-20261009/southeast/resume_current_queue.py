from pathlib import Path
import subprocess,json
from workflow import ROOT,read,write,sha,now
ack=read(ROOT/'resume-ack-20261010.json')
ack.update(latestResumeAtUtc=now(),latestAuthorization='User requests continuing actual art; runtime work is out of scope; preserve current queue.',previousUserAGENTSApply=False,newArtworkGenerationAllowed=True,priorSuccessfulOutputCheck={'nativeFiles':len(list((ROOT/'native').glob('*.png'))),'rootMissingToGenerate':['r11_c12_p33','r11_c12_p34','r11_c12_p41','r11_c12_p42','r11_c12_p43','r11_c12_p44']},currentQueueOnly=True)
write(ROOT/'resume-ack-20261010.json',ack)
jobs=[]
for pid in ['r11_c12_p34','r11_c12_p41']:
 assert not (ROOT/'native'/f'{pid}_v01.png').exists()
 old=(ROOT/'prompts'/f'{pid}_v01.prompt.txt').read_text(encoding='utf-8')
 desc=old.split('LOCAL CONTENT AND GEOMETRY: ',1)[1].split('\n\nKeep clear crisp',1)[0]
 r=subprocess.run([__import__('sys').executable,str(ROOT/'request.py'),pid,'v02',desc],capture_output=True,text=True,check=True)
 req=json.loads(r.stdout)
 for p in req['referenced_image_paths']:assert Path(p).exists()
 jobs.append({'pid':pid,'version':'v02','request':req})
print(json.dumps(jobs))
