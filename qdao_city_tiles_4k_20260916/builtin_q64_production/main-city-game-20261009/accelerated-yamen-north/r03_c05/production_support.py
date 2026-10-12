import sys,json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent; ROOT=T.parent
sys.path.insert(0,str(ROOT)); import pipeline as p
def put(path,data):
 path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def local_progress():
 selected=[{'patch':pid,**p.native_info(p.selected(T,pid))} for pid in p.patch_ids() if p.selected(T,pid).is_file()]
 order=[f's{r:02d}_{c:02d}' for r in range(4,0,-1) for c in range(1,5)]; have={x['patch'] for x in selected}
 d={'tile':'r03_c05','selectedCount':len(selected),'selected':selected,'nextCoordinate':next((x for x in order if x not in have),None),'formalAccepted':False,'actualModel':None}
 p.replace_json(T/'worker-progress.json',d); return d
p.update_progress=local_progress
mode=sys.argv[1]
if mode=='prepare':
 pid=sys.argv[2]; ver=sys.argv[3] if len(sys.argv)>3 else 'v1'
 prep=p.prepare('r03_c05',pid,ver,'all'); m=read(prep['manifest'])
 assert m['nativeAnchors'], 'Do not generate without a true native neighbor'
 content=read(ROOT/'qa-planning/r03_c05/content-index.json'); desc=next(x['description'] for x in content['patches'] if x['patch']==pid)
 refs=[prep['guide']]
 anchors=sorted(m['nativeAnchors'],key=lambda a:(a['targetBox'][2]-a['targetBox'][0])*(a['targetBox'][3]-a['targetBox'][1]),reverse=True)
 for a in anchors[:0]:
  if a['file'] not in refs: refs.append(a['file'])
 anchor_text='; '.join(str(a['targetBox'])+' from '+a['tile']+'/'+a['patch'] for a in m['nativeAnchors'])
 prompt=('Create ONE opaque 1254 x 1254 pixel native game-art crop. Edit reference 1, which is a precise continuation guide in a fixed world coordinate system. The crisp strips in it are real finished native artwork; the blurry remainder is positioning-only layout, never final artwork. Paint the remainder freshly at native resolution, crisp and as detailed as the native neighboring references. Keep the SAME crop, scale, camera and projection; do not zoom, frame, rotate or shift.\n'
 'Use case: stylized Chinese Daoist town architectural environment texture. Bright warm daylight, polished hand-painted 3D/chibi game environment, cyan-teal glazed ceramic roof tiles with fine painterly texture, golden painted ridges, reddish brown wood. Match the supplied neighboring native artwork exactly in material, light, size of tile units and edge positions. No people, lettering, icons or invented standalone objects.\n'
 'Patch '+pid+' world halo box '+str(m['worldBoxWithHalo'])+'. Main visible layout: '+desc+'\n'
 'The native anchor rectangles in reference 1 (left,top,right,bottom, exclusive) are '+anchor_text+'. Preserve their actual objects, silhouette, groove endpoints, colors and shading in place. Continue each interrupted form across the native-to-layout boundary smoothly at exactly the same size. Neighbor references 2+ show finished details and are CONTEXT ONLY: do not copy their whole composition into this crop. The soft map regions locate the broad architectural bands and ornaments; reconstruct those at high detail, never preserve blur or pixelation.\n'
 'This is a tightly cropped roof complex: all cyan/teal map areas, including behind golden ridge ornaments, are GLAZED CERAMIC ROOF, never sky, clouds, water or open background. No sky anywhere. Do not duplicate the entire neighboring composition. Follow the specified local silhouette. Native strip edges are NOT physical borders: continue connected tile courses and structural grooves through these positions; never leave a straight rectangular cut between pasted native strip and new artwork. Where the roof curves, connect the tile courses physically and gradually with crisp grooves.\n'
 'Output full bleed exact 1254x1254, no border, labels, grid, watermark or added framing. The 1024 core is [115,115,1139,1139] and 115-pixel halo remains fully rendered. Every side continues the same scene, no vignette, no forced edge closure. Preserve enough precise native anchor geometry for seamless pixel-coordinate assembly.')
 params={'prompt':prompt,'referenced_image_paths':refs,'transparent_background':False}; out=T/'requests'/f'{pid}_{ver}'; out.mkdir(parents=True,exist_ok=True)
 put(out/'parameters.json',params); put(out/'preparation-path.json',{'file':prep['manifest']}); (out/'prompt.txt').write_text(prompt,encoding='utf-8')
 print(json.dumps({'parameters':params,'parametersFile':str(out/'parameters.json'),'preparation':prep['manifest'],'requestDir':str(out)},ensure_ascii=False))
elif mode=='ingest':
 pid,ver,host=sys.argv[2:5]; out=T/'requests'/f'{pid}_{ver}'
 print(json.dumps(p.ingest('r03_c05',pid,host,str(out/'parameters.json'),str(out/'tool-result.json'),ver,read(out/'preparation-path.json')['file']),ensure_ascii=False))
elif mode=='assemble': print(json.dumps(p.assemble('r03_c05','minimum-error'),ensure_ascii=False))
