from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import production_v2 as p
T=Path(__file__).resolve().parent
M=T/'candidate/r07_c05-candidate-hard-1672ae5e4698.assembly.json'
a=p.read(M)
bad={
'internal-y2048-segment03':'An isolated diagonal grout stroke ends at crop x115,y~260 at the retained left-anchor boundary; curb/blue paving otherwise connects.',
'internal-y3072-segment01':'Pale upper curb ends against a horizontal cutoff at lower-left near crop y275; anchor transition remains visible.',
'internal-y3072-segment02':'Cream road curb makes an abrupt offset/step near crop x100..155 instead of a continuous join.',
'junction-x2048-y1024':'Pale grout/bevel ends inside the slab near upper-center; neighboring diagonal lattice does not fully join.',
'junction-x2048-y2048':'Unconnected diagonal grout tip near crop x275,y275 at the native anchor edge.'}
entries=[]
for q in a['qa']:
 n=Path(q['file']).stem
 if n.startswith('internal-x'): continue
 assert p.sha(q['file'])==q['sha256']
 entries.append({'name':n,'file':q['file'],'sha256':q['sha256'],'actuallyViewed':True,'verdict':'blocking' if n in bad else 'passed','findings':bad.get(n,'Native crop directly viewed: continuous structural edges and complete stone joints, with material variation contained by stone boundaries.')})
assert len(entries)==21
p.write_json(T/'qa/horizontal-junction-review-1672ae5e4698.json',{'createdAtUtc':p.now(),'tile':'r07_c05','candidate':a['output'],'assemblyManifest':{'file':str(M),'sha256':p.sha(M)},'status':'needs_repair','blockingCount':len(bad),'entries':entries,'formalAccepted':False},replace=False)
print({'viewed':21,'blocking':len(bad)})

