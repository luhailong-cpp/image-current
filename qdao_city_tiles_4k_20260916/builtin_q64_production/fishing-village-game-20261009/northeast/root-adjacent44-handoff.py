from r06_c13_extension import *
from PIL import Image
out=Z/'native/root-adjacent44-v1.png'
rec=Path(str(out)+'.generation.json');d=json.loads(rec.read_text(encoding='utf-8'))
assert Image.open(out).size==(1254,1254) and sha(out)==d['sha256']==d['source']['sha256']
for k in ['prompt','receipt','source']:assert sha(d[k]['path'])==d[k]['sha256']
for e in d['references']:assert sha(e['path'])==e['sha256']
qas=[ref(Z/'qa'/f'root-adjacent44-v1-exact_native_{s}_230px.png',s+' full native seam QA') for s in ['left','top','right','bottom']]
h={'createdAtUtc':now(),'patchId':'r06_c12_p44','selectedProposedNative':ref(out,'v1 recommended by root four-edge visual review'),'generationRecord':ref(rec,'source prompt receipt config and native coordinate evidence'),'coordinates':d['coordinates'],'nativeSize':[1254,1254],'actualModel':None,'actualQuality':None,'route':'builtin','allSourceEvidenceHashesVerified':True,'coreCrop':[115,115,1139,1139],'neighborSources':d['nativeEdgeSources'],'qa':qas,'review':{'reviewer':'root','localGeometry':'provisionally passed for v1; right/bottom continuous, left variation occurs at natural stone joint, top local joint variation without silhouette break','wholeTileReview':'pending r06_c12 candidate-v4 assembly with original42/43','v2':'retained unselected; left curb joint broadened and less coherent than v1'},'restoreNeighborBaselines':[ref(Z/'native/r07_c12_northrepair42-v1.png','original mutually continuous native42'),ref(Z/'native/r07_c12_northrepair43-v1.png','original mutually continuous native43')],'doNotSelect':ref(Z/'native/root-adjacent44-v2.png','inferior v2 candidate'),'formalAccepted':False,'selectionModified':False,'progressModified':False,'nativeResamplingPerformed':False,'finalLocalPaintingPerformed':False}
write(Z/'records/root-adjacent44-handoff.json',h)
print(json.dumps({'handoff':str(Z/'records/root-adjacent44-handoff.json'),'source':str(out),'sha256':sha(out),'hashesVerified':True}))
