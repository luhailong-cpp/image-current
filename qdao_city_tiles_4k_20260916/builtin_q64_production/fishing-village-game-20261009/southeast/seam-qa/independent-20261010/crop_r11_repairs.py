import sys,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE=HERE.parent.parent
sys.path.insert(0,str(BASE))
from review_external_seams import Sources,write_evidence
folder=HERE/'r11_c10-adoption-final'
folder.mkdir(exist_ok=True)
sources=Sources();out=[]
for name,(x0,y0,x1,y1) in {'G1':[37546,43885,38441,44515],'Q1':[37521,43043,38301,43723]}.items():
 for edge,b in {'top':[x0-96,y0-96,x1+96,y0+96],'bottom':[x0-96,y1-96,x1+96,y1+96],'left':[x0-96,y0-96,x0+96,y1+96],'right':[x1-96,y0-96,x1+96,y1+96]}.items():
  out.append(write_evidence(sources,folder,name+'-'+edge,b,{'adoptionGlobal':[x0,y0,x1,y1],'edge':edge}))
(folder/'manifest.json').write_text(json.dumps({'results':out},indent=2)+'\n')
print(str(folder))
