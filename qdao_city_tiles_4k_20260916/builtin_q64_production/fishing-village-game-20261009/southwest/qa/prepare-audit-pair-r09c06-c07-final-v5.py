import sys
sys.dont_write_bytecode=True
from pathlib import Path
p=Path(__file__).resolve().parent
s=(p/'audit-pair-r09c06-c07-final-v4.py').read_text()
s=s.replace("pre='pair-r09c06-c07-final-v4'","pre='pair-r09c06-c07-final-v5'")
s=s.replace("('north-halo',[3866,0,4556,300])","('south-native',[3650,3072,4904,4326]),('north-halo',[3866,0,4556,300])")
s=s.replace("'repairedFindings':[","'priorAudit':ref(Q/'pair-r09c06-c07-final-v4-visual-audit.json'),'repairedFindings':[{'id':'south-floor-corner','result':'second dangling grout branch at the core south edge removed, leaving a continuous natural two-way corner in the halo'},")
s=s.replace("'rejectedTrials':[","'rejectedTrials':[{'prefix':'pair-r09c06-c07-final-v4','reason':'core review passed, extended south halo inspection exposed second dangling grout; v5 repairs it'},")
(p/'audit-pair-r09c06-c07-final-v5.py').write_text(s)

