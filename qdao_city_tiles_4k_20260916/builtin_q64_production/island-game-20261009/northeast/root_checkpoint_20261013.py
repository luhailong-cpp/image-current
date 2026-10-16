from native_work import *
import sys
ident=sys.argv[1];state=sys.argv[2]
s=read(ZONE/'selection-r03_c09.json')
p=ZONE/'qa/root-r03c09-checkpoint-20261013.json'
write(p,{'worker':'root','tileId':'r03_c09','currentId':ident,'state':state,'recordedAtUtc':now(),'selectedCoreIds':s['cores'],'selectedCoreCount':sum(bool(v) for row in s['cores'] for v in row),'pendingCandidate':'r03_c09_p01_02: right grout discontinuity, original unselected; v2 repair in progress' if ident=='r03_c09_p01_02_v2' else None,'actualModel':None,'route':'builtin','formalAccepted':False,'next':'Complete current core and fast neighbor joins, then continue right-to-left columns; full49 review after 16 cores.','recovery':'If exec cell lost, inspect newest generated_images source and receipt/native metadata before retrying; no duplicate generation.','sharedGitMutation':False})
print(json.dumps({'id':ident,'state':state,'selected':sum(bool(v) for row in s['cores'] for v in row)}))

