from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import production_v2 as p
T=Path(__file__).resolve().parent
Q=T/'qa/r05_c03-candidate-hard-80982c249bee'
M=T/'candidate/r05_c03-candidate-hard-80982c249bee.assembly.json'
a=p.read(M); epath=Q/'external-east-20261012/index.json'; e=p.read(epath)
def ref(f):return {'file':str(f),'sha256':p.sha(f)}
assert p.sha(e['neighbor']['file'])==e['neighbor']['sha256']
findings={
'east-segment01':'Green decorative panel and pale paving remain continuous across the shared seam.',
'east-segment02':'Paving curb and red firecracker fragments remain uncut at the tile join.',
'east-segment03':'Paving grout lines and blossom edge connect without a broken geometry seam.',
'east-segment04':'Blossom canopy, branch silhouettes, shadows and paving continue across the join.',
'east-junction-y1024':'Irregular stone joints meet continuously at the cross-grid junction.',
'east-junction-y2048':'Paving grout and fragment placement remain continuous.',
'east-junction-y3072':'Angled paving edge, blossom leaves and shadow have no junction cutoff.'}
for q in e['entries']:
 assert p.sha(q['file'])==q['sha256']
 q.update({'actuallyViewed':True,'verdict':'passed','findings':findings[q['name']]})
e.update({'createdAtUtc':p.now(),'status':'passed','blockingCount':0,'actuallyViewed':True,'seamSegments':4,'junctions':3,'reviewedSide':'east','neighborTile':'r05_c04','formalAccepted':False})
report=Q/'external-east-20261012/review.json';p.write_json(report,e,replace=False)
ir=Q/'review-internal-20261012.json'; proof=Q/'native-pixel-proof-20261012.json'
acceptance={'schemaVersion':1,'createdAtUtc':p.now(),'tile':'r05_c03','candidate':a['output'],'internalQA':{'status':'passed','actuallyViewed':True,'seamSegments':24,'junctions':9,'evidence':[ref(ir)]},'externalQA':{'status':'pending','actuallyViewed':True,'reviewedSides':['east'],'passedSides':['east'],'pendingSides':['north','south','west'],'worldBoundarySides':[],'evidence':ref(report)},'formalAccepted':False,'actualModel':None,'actualQuality':None,'runtimeIntegration':False,'capacity5000Validated':False}
p.write_json(T/'qa/acceptance.json',acceptance,replace=False)
summary={'schemaVersion':1,'createdAtUtc':p.now(),'tile':'r05_c03','candidate':a['output'],'assemblyManifest':ref(M),'fixedGridSourceCount':16,'totalNativeSourceCount':16,'internalQA':acceptance['internalQA'],'externalQA':acceptance['externalQA'],'pixelProof':ref(proof),'evidence':{'internal':ref(ir),'external':ref(report)},'status':'internal_and_available_east_boundary_passed','blockingCount':0,'formalAccepted':False,'wholeZoneComplete':False,'actualModel':None,'actualQuality':None,'route':'builtin_image_gen','nativeResampling':False,'remainingIssues':['Unfinished north, south and west neighboring tiles remain outside this milestone.']}
p.write_json(T/'delivery-summary-20261012.json',summary,replace=False)
print(summary['status'])

