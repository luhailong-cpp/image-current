from workflow import *
items=['north1','v11-v02','v21','v31']
for n in items:
 f=ROOT/'qa'/f'r10_c11-helper-{n}.json';d=read(f);d.update({'status':'visual_major_geometry_pass','reviewer':'root','reviewedAt':now(),'scope':'Full 1254 width native-pair hard seam reviewed; candidate core width1024 contained within sample. No blending used.'});write(f,d)
chosen={'11':'v01','21':'v02','31':'v02','41':'v01'}
out={'tile':'r10_c11','helper':'root','selection':chosen,'coreCrop':[115,115,1139,1139],'nativeCount':5,'selectedCount':4,'rejected':[{'file':'native/r10_c11_p21_v01.png','reason':'Lower foreground wrongly rendered horizontal floor instead of vertical courtyard wall face; replaced by v02 before propagation.'}],'reviewedNativePairs':items,'allReviewedMajorGeometryPass':True,'wholeTileAccepted':False,'pending':'Middle-column joins and full candidate review by tile_left','completedAt':now()}
write(ROOT/'qa/r10_c11-root-helper-review.json',out)
for k,v in chosen.items():
 p=ROOT/'native'/f'r10_c11_p{k}_{v}.png';q=Path(str(p)+'.generation.json');d=read(q);d['status']='selected_for_r10c11_candidate_pending_middle_column_joins';write(q,d)
p=ROOT/'native/r10_c11_p21_v01.png.generation.json';d=read(p);d['status']='rejected_replaced_by_v02_wall_face_orientation';write(p,d)
p=ROOT/'progress-helper-r10_c11.json';d=read(p);d.update({'status':'four_assigned_cores_complete','selectedVersions':chosen,'generatedNativeCount':5,'usableNativeCount':4,'nextStep':'tile_left assembles complete r10c11 and reviews remaining joins','updatedAt':now()});write(p,d)
print('Four helper cores and four reviewed native pairs recorded')

