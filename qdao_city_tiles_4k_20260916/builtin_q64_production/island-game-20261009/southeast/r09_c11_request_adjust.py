from workflow import ROOT,read,write
from pathlib import Path
p=ROOT/'prompts'/'r09_c11_p23_v03.request.json'
r=read(p);r['references']=[r['references'][0]]+r['references'][-3:];write(p,r)
