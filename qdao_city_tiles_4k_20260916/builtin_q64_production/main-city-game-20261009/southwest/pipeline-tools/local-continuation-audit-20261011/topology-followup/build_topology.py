from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, hashlib, math
import numpy as np

O=Path(__file__).parent
S=O.parents[2]
F=S.parents[1]/'parallel_20261005/daylight-only-20261009/tianyong/tianyong-spring-natural-stone-v9.png'
SCALE=65536/1254
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
write=lambda p,x:Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
world=lambda p:[round(v*SCALE,2) for v in p]
L=[]
def line(id,kind,pts,note,confidence='high'):
 L.append(dict(id=id,kind=kind,sourcePolyline=pts,worldPolyline=[world(p) for p in pts],confidence=confidence,note=note))

# Human trace of the coarse approved source. These are approximate structural
# guides, not exact pixel masks, inferred high-resolution art, or resampled finals.
line('NW1','border',[[307,866.7],[335,846.7]],'Northwest first oblique boundary; faint clipped segment in p01_01.')
line('NW2','border',[[307,871.8],[340,847.9]],'Northwest upper edge of broad pale border band.')
line('NW3','border',[[307,880.5],[345,853.0]],'Northwest lower edge of broad pale border band.')
line('NW4','border',[[307,884.3],[349.5,853.0]],'Parallel ground-side edge of narrow gray border; do not merge NW3 and NW4.')
line('NE1','border',[[364,853],[400,877]],'Lower boundary of northeast oblique cream band, crosses p01_04.')
line('NE2','border',[[369,853],[400,874]],'Upper boundary of northeast oblique cream band, parallel to NE1.')
line('D1','joint',[[336.5,857.3],[357.8,871.7],[374.8,883.9],[389.5,894.5]],'Long descending paving seam across p01_02/03 and p02_03/04; joins southeast rim.')
line('D2','joint',[[316.9,873.3],[319.5,875.4],[335.9,886.2],[353.7,898.6],[367.6,909.95]],'Second long descending seam; starts across northwest border; stops at southeast rim.')
line('D3','border',[[341.5,897.5],[364.3,912.6],[368.7,916.2]],'Lower edge of diagonal pale stone strip; crosses southeast rim then stops at blue-gray upper edge.')
line('U1','joint',[[320.5,897.5],[335.9,886.2],[357.8,871.7],[374.4,859.92]],'Continuous faint ascending seam. Crosses D2 and D1: both X junctions must remain.','medium')
line('U2','joint',[[353.7,898.6],[374.8,883.9],[384.9,877.9],[394.0,872.5]],'Ascending seam from lower T through p02_03 toward northeast frame; follows slight coarse-source bend.','medium')
line('NEstub','weak_joint',[[382.4,874.0],[384.9,877.9]],'Short faint branch into U2 in p01_04; keep weak, not a new bold grid.','medium')
line('Rtop','border',[[300,897.5],[341.5,897.5]],'Outer horizontal rectangular stone-frame edge.')
line('Rright','border',[[341.5,897.5],[341.5,948]],'Outer vertical rectangular frame; blue diagonal area remains on its east side below the corner.')
line('RinnerTop','border',[[300,901.5],[328.8,901.5]],'Inner horizontal edge.')
line('RinnerRight','border',[[328.8,901.5],[328.8,949]],'Inner vertical edge; approx native x915 in p03_01/p04_01.')
line('RshortV','weak_joint',[[317.8,897.5],[317.8,911.5]],'Short vertical subdivision in inner stone; terminates at short lower horizontal.','medium')
line('RshortH1','weak_joint',[[317.8,908.0],[328.8,908.0]],'Weak cross-joint between short and main vertical.','medium')
line('RshortH2','joint',[[300,911.5],[317.8,911.5]],'Left horizontal subdivision ending at short vertical.')
line('RlowH','joint',[[300,918.5],[328.8,918.5]],'Lower horizontal stone seam; northwest blue-area corner lies below it.')
line('Rdivider1','weak_joint',[[316.5,927.0],[341.5,927.0]],'Sparse horizontal division across pale rectangular bands.','medium')
line('Rdivider2','weak_joint',[[316.5,936.8],[341.5,936.8]],'Next sparse horizontal division; do not add dense small tiles.','medium')
line('Ymain','weak_joint',[[341.5,911.5],[350,911.5],[356.0,907.1]],'Faint Y/T joint: horizontal stem in p03_02; upper branch continues into p03_03 and terminates at D3, not in open stone. Endpoint clarified by wider-source QA.','medium')
line('Ylower','weak_joint',[[350,911.5],[357.8,917.2]],'Lower-right branch of same faint Y/T.','medium')
line('SErim','border',[[341.5,928.3],[364.3,912.6],[367.6,909.95],[389.5,894.5],[400,887.1]],'Ascending outer edge of southeast pale border band. D1 and D2 stop here; D3 crosses it.')
line('BlueUpper','color_edge',[[341.5,934.8],[368.7,916.2],[400,894.0]],'Upper edge of continuous blue-gray band; broad colored region, not a thin paving seam.')
line('BlueLowerVisible','color_edge',[[341.5,947.5],[359.5,935.0]],'Visible lower edge of blue-gray band; roof occludes continuation to the northeast.')
line('BlueWestTop','color_edge',[[300,920.5],[316.5,920.5]],'Top transition into northwest blue-gray rectangular field, approx one source-pixel soft transition.')
line('BlueWestRight','color_edge',[[316.5,920.5],[316.5,949]],'Right transition of blue-gray field; a pale border follows on the east.')

regions=[
 dict(id='northwest-pale-band',kind='cream_border_band',sourcePolygon=[[307,871.8],[340,847.9],[345,853],[307,880.5]],note='Keep broad calm cream band; its two edges are NW2/NW3.'),
 dict(id='northeast-pale-band',kind='cream_border_band',sourcePolygon=[[364,853],[400,877],[400,874],[369,853]],note='Small northeast clipped border strip; approximate occupancy only.'),
 dict(id='west-blue',kind='blue_gray_surface',sourcePolygon=[[300,920.5],[316.5,920.5],[316.5,949],[300,949]],note='Muted blue-gray field; do not convert to stone or pure saturated blue.'),
 dict(id='southeast-blue',kind='blue_gray_surface',sourcePolygon=[[341.5,934.8],[368.7,916.2],[400,894],[400,906.7],[383.5,918.2],[359.5,935],[341.5,947.5]],note='Continuous broad band; lower boundary partly occluded by actual roof.'),
 dict(id='roof-occupancy',kind='roof_not_stone',sourcePolygon=[[358.5,931],[361.5,928.5],[367,930],[381.5,920.5],[382.2,910.5],[386,908.6],[391,913],[397,910],[400,908],[400,950],[368.5,950],[367,939],[361,938],[358.5,935]],note='Conservative semantic footprint only, NOT a contour mask. Gold curved eave/ornament + dark teal tiled roof + red/brown fascia/wall. Original guide governs shape; no paving lines across the roof.')
]
for r in regions:r['worldPolygon']=[world(p) for p in r['sourcePolygon']]

def clip(a,b,box):
 x0,y0,x1,y1=box; dx=b[0]-a[0];dy=b[1]-a[1];t0=0;t1=1
 for p,q in [(-dx,a[0]-x0),(dx,x1-a[0]),(-dy,a[1]-y0),(dy,y1-a[1])]:
  if abs(p)<1e-12:
   if q<0:return None
  else:
   t=q/p
   if p<0:t0=max(t0,t)
   else:t1=min(t1,t)
 if t0>t1:return None
 return [[a[0]+t*dx,a[1]+t*dy] for t in [t0,t1]]

patches=[]
for rr in range(1,5):
 for cc in range(1,5):
  id=f'p{rr:02}_{cc:02}'; d=json.loads((S/f'r12_c05/guides/{id}.layout-only.png.derivation.json').read_text(encoding='utf-8-sig'))
  box=d['layoutSourceBox'];wbox=d['contextWorldBox'];entries=[]
  for l in L:
   for seg,(a,b) in enumerate(zip(l['sourcePolyline'],l['sourcePolyline'][1:])):
    pp=clip(a,b,box)
    if pp and math.dist(*pp)>0.02:
     ww=[world(v) for v in pp]
     entries.append(dict(lineId=l['id'],segment=seg,kind=l['kind'],confidence=l['confidence'],sourceEndpoints=[[round(v,3) for v in p] for p in pp],worldEndpoints=ww,nativeEndpoints=[[round(p[0]-wbox[0]),round(p[1]-wbox[1])] for p in ww]))
  semantic=['calm large light-gray stone; no fine woven pattern']
  if rr>=3 and cc<=2:semantic+=['orthogonal pale rectangular stone frame; sparse subdivisions']
  if (rr==3 and cc>=3) or rr==4:semantic+=['blue-gray surface and cream border occupancy per source']
  if (rr==3 and cc==4) or (rr==4 and cc>=3):semantic+=['gold/teal/red roof object; preserve original silhouette; not paving']
  patches.append(dict(id=id,contextWorldBox=wbox,coreWorldBox=d['coreWorldBox'],sourceBox=box,guideSha256=d['guideSha256'],semantics=semantic,segments=entries))

doc=dict(schema='human-approved-source-topology-guide-v1',status='QA_STRUCTURAL_GUIDE_NOT_FINAL_ART',source=dict(path=str(F),sha256=sha(F),size=[1254,1254]),tile='r12_c05',tileCoreWorldBox=[16384,45056,20480,49152],worldPerSourcePixel=SCALE,uncertainty=dict(sourcePixels=1,nativeWorldPixels=SCALE,note='Approximate manual centerlines; support coherent shared endpoints. No subpixel precision claim. Faint lines stay weak. Guide geometry overrides invented old-native strips.'),lines=L,regions=regions,notPromotedToLines=['Small stochastic tonal patches inside a single broad slab.','Soft shadow gradients along edges.','Hidden continuation of blue band below roof.'],productionRules=['Use approved original macro plus quiet material crop.','Old native with absent or wrong joints is not a hard strip anchor.','One coherent world line is clipped to all affected patches; do not choose independent endpoints.','Inspect actual generated edges and reconcile shared overlap after generation.','Approximate line coordinates do not authorize deleting an observed source line or drawing a new lattice.','Roof polygons are semantic warnings, never automatic edit masks.'],patchEndpointFile='patch-endpoints.json')
write(O/'r12-macro-topology.json',doc)
write(O/'patch-endpoints.json',dict(sourceSha256=sha(F),uncertaintyNativePixels=SCALE,patches=patches))

# Evidence overlay and clean map are explicitly resized QA diagrams.
box=[307,853,400,949]; k=12; margin=65
im=Image.open(F).convert('RGB');base=im.crop(box).resize(((box[2]-box[0])*k,(box[3]-box[1])*k),Image.Resampling.NEAREST)
def xy(p):return (margin+(p[0]-box[0])*k,margin+(p[1]-box[1])*k)
colors={'border':'#de6d16','joint':'#c33162','weak_joint':'#967019','color_edge':'#007aa5'}
for clean,name in [(False,'r12-topology-overlay.png'),(True,'r12-topology-world-map.png')]:
 canvas=Image.new('RGB',(base.width+margin*2,base.height+margin*2+40),'white')
 if not clean:canvas.paste(base,(margin,margin))
 dr=ImageDraw.Draw(canvas)
 for i in range(5):
  x=(16384+i*1024)/SCALE;y=(45056+i*1024)/SCALE
  dr.line([xy((x,box[1])),xy((x,box[3]))],fill='#98a2ad',width=1)
  dr.line([xy((box[0],y)),xy((box[2],y))],fill='#98a2ad',width=1)
  dr.text((xy((x,box[1]))[0]-14,margin-20),str(16384+i*1024),fill='black')
  dr.text((0,xy((box[0],y))[1]-5),str(45056+i*1024),fill='black')
 for l in L:
  for a,b in zip(l['sourcePolyline'],l['sourcePolyline'][1:]):
   seg=clip(a,b,box)
   if seg:dr.line([xy(p) for p in seg],fill=colors[l['kind']],width=2 if l['kind']=='weak_joint' else 3)
  pts=[p for p in l['sourcePolyline'] if box[0]<=p[0]<=box[2] and box[1]<=p[1]<=box[3]]
  if pts:dr.text(xy(pts[len(pts)//2]),l['id'],fill=colors[l['kind']])
 for r in regions:
  if r['id']=='roof-occupancy':
   pts=[xy(p) for p in r['sourcePolygon']];dr.line(pts+[pts[0]],fill='#8931ba',width=3)
 for p in patches:
  cb=p['coreWorldBox'];center=[(cb[0]+120)/SCALE,(cb[1]+100)/SCALE]
  dr.text(xy(center),p['id'],fill='#143260')
 dr.text((margin,12),'QA ONLY / approximate manual topology / source resized NEAREST 12x / NOT FINAL ART',fill='black')
 dr.text((margin,canvas.height-43),'World axes | orange border / magenta joint / ochre faint joint / blue color edge / purple roof occupancy',fill='black')
 dr.text((margin,canvas.height-25),'Source uncertainty +/- 1 px = +/- 52 native-world px. All geometry comes from one approved whole-city source.',fill='black')
 canvas.save(O/name)

write(O/'preview-manifest.json',dict(finalArt=False,source=str(F),sourceSha256=sha(F),files=[dict(path=str(O/n),resized=True,resample='NEAREST',scale=12,sourceCrop=box,purpose='human topology QA overlay, not candidate') for n in ['r12-topology-overlay.png','r12-topology-world-map.png']]))

txt=['r12_c05 — minimum structural guide, not final acceptance','Approximate source +/-1 px = native/world +/-52.26 px. Bold or thin according to kind; no invented fine lattice.','']
for p in patches:
 txt.append(p['id']+' contextWorld='+str(p['contextWorldBox']))
 txt.extend('  '+z['lineId']+' '+z['kind']+' native '+str(z['nativeEndpoints'])+' world '+str(z['worldEndpoints']) for z in p['segments'])
 txt.append('  '+ '; '.join(p['semantics']))
 txt.append('')
(O/'patch-endpoints.txt').write_text('\n'.join(txt),encoding='utf-8')
print(json.dumps({'lines':len(L),'patches':len(patches),'output':str(O),'sourceSha256':sha(F)},ensure_ascii=False))
