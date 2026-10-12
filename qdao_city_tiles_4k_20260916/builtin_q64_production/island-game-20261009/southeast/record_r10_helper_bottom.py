from workflow import *
p=ROOT/'qa/r10_c11-root-helper-review.json';d=read(p);d['selection'].update({'42':'v02','43':'v01'});d['nativeCount']=8;d['selectedCount']=6;d['reviewedNativePairs']+=['h41','h42'];d['completedAt']=now();d['rejected'].append({'file':'native/r10_c11_p42_v01.png','reason':'Invented relief motifs and second wall/coping at top, corrected by full native edit v02.'});write(p,d)
for n in ['h41','h42']:
 p=ROOT/'qa'/f'r10_c11-helper-{n}.json';d=read(p);d.update({'status':'visual_major_geometry_pass','reviewer':'root','reviewedAt':now()});write(p,d)
p=ROOT/'progress-helper-r10_c11.json';d=read(p);d.update({'status':'six_assigned_cores_complete','selectedVersions':{'11':'v01','21':'v02','31':'v02','41':'v01','42':'v02','43':'v01'},'generatedNativeCount':8,'usableNativeCount':6,'updatedAt':now()});write(p,d)
for rc,v in [('42','v02'),('43','v01')]:
 p=ROOT/'native'/f'r10_c11_p{rc}_{v}.png.generation.json';d=read(p);d['status']='selected_for_r10c11_candidate_pending_remaining_neighbor_joins';write(p,d)
p=ROOT/'native/r10_c11_p42_v01.png.generation.json';d=read(p);d['status']='rejected_replaced_by_v02_remove_invented_wall_details';write(p,d)
print('Six helper selections and six reviewed native pairs recorded')

