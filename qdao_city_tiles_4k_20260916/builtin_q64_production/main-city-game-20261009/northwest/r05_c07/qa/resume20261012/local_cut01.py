import json,math,importlib.util,hashlib
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image
tile=Path(__file__).resolve().parents[2];zone=tile.parent
def mod(name):
 spec=importlib.util.spec_from_file_location(name,zone/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
p=mod('production_v2');a=mod('assemble_native')
basepath=tile/'candidate'/'r05_c07-candidate-hard-1e8b8d67a15d.assembly.json';base=json.loads(basepath.read_text())
assert p.sha(Path(base['output']['file']))==base['output']['sha256']
out=np.array(Image.open(base['output']['file']).convert('RGB'));initial=out.copy();source_map=np.zeros((4096,4096),dtype=np.uint8)
sources={}
for source in base['nativeSources']:
 pid=source['id'];ref=p.validate_native(p.selected_path(tile,pid),tile,pid);assert ref['sha256']==source['sha256']
 sources[pid]=np.array(Image.open(source['file']).convert('RGB'));r=source['row']-1;c=source['column']-1
 source_map[r*1024:(r+1)*1024,c*1024:(c+1)*1024]=r*4+c+1
 assert np.array_equal(out[r*1024:(r+1)*1024,c*1024:(c+1)*1024],sources[pid][115:1139,115:1139])
recipe={'blue':{'source':'s01_03','tileBox':[2048,1024,2427,1069],'reason':'Move binary cut from middle of one blue stone to its real horizontal grout'},'grout':{'source':'s02_04','xRange':[3100,3320],'cutYFormula':'1024 - round(60 * exp(-((x-3200)/60)**2))','bottomY':1024,'reason':'Recover intact diagonal grout from native top halo before broken upper-source endpoint'}}
# Native same-coordinate blue grout cut.
out[1024:1069,2048:2427]=sources['s01_03'][1139:1184,115:494];source_map[1024:1069,2048:2427]=3
# Smoothly varying BINARY source choice, no interpolated or blended pixels.
for x in range(3100,3320):
 y=1024-round(60*math.exp(-((x-3200)/60)**2))
 out[y:1024,x]=sources['s02_04'][y-909:115,x-2957];source_map[y:1024,x]=8
# Prove every output pixel equals a selected native sample at the same world position.
for source in base['nativeSources']:
 pid=source['id'];sid=(source['row']-1)*4+source['column'];ys,xs=np.where(source_map==sid)
 ox=(source['column']-1)*1024-115;oy=(source['row']-1)*1024-115
 assert np.all((xs-ox>=0)&(xs-ox<1254)&(ys-oy>=0)&(ys-oy<1254))
 assert np.array_equal(out[ys,xs],sources[pid][ys-oy,xs-ox])
sig=hashlib.sha256(json.dumps({'base':base['output']['sha256'],'recipe':recipe},sort_keys=True).encode()).hexdigest()[:12]
name='r05_c07-candidate-localcut-'+sig;target=tile/'candidate'/(name+'.png');assert not target.exists()
output=a.save_png(Image.fromarray(out),target)
mapref=a.save_png(Image.fromarray(source_map),tile/'candidate'/(name+'.source-map.png'))
qa=a.write_qa(Image.fromarray(out),output,tile/'qa'/name)
base.update({'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'candidate_pending_review','method':'hard cores with two localized binary native halo cuts','output':output,'qa':qa,'script':{'file':str(Path(__file__)),'sha256':p.sha(Path(__file__))},'sourceMap':mapref,'localNativeCuts':recipe,'binarySourceProvenanceValidatedEveryPixel':True,'changedPixelCount':int(np.count_nonzero(np.any(out!=initial,axis=2))),'derivedFromHardCandidate':{'file':str(basepath),'sha256':p.sha(basepath)},'visualQA':{'status':'pending','nativeSeamSegments':24,'junctions':9,'actuallyViewed':False}})
a.write_json(tile/'candidate'/(name+'.assembly.json'),base)
a.write_json(tile/'candidate'/(name+'.png.derivation.json'),{'operation':'Two localized binary native source selections at same coordinates; every pixel proven from current native1254; no resize/blend/warp/color changes','output':output,'sourceMap':mapref,'recipe':recipe,'nativeSources':base['nativeSources'],'sourceResampled':False,'formalAccepted':False})
print(json.dumps({'output':output,'qa':str(tile/'qa'/name),'changedPixelCount':base['changedPixelCount'],'everyPixelNativeVerified':True}))

