from native_work import *
ident='r03_c10_cross_native_material_repair'
ip=ZONE/'qa'/f'{ident}-inspection/inspection.json'
q=read(ip); recpath=ZONE/'native'/f'{ident}.png.generation.json';rec=read(recpath)
assert sha(q['source'])==q['sha256']==rec['sha256']
assert sha(q['base'])==q['baseSha256']
assert len(q['inspectionImages'])==9
for e in q['inspectionImages']:
 assert sha(e['file'])==e['sha256']
 e.update(status='passed_visual_100pct',reviewer='root',evidence='Visually inspected at 1:1 before crash; unchanged image hash verified on recovery.')
q.update(status='passed_native_overlay_boundary1to1',reviewedAtUtc=now(),finding='Continuous stone slabs and leaf shadows; prior straight material scar removed. Center, four edges and four corners passed native-scale inspection.')
write(ip,q)
op=ZONE/'qa'/f'{ident}.overlay.json'
assert not op.exists()
o={k:q[k] for k in ('id','source','sha256','coreCrop','tileLocalPaste','operation')}
o.update(review=q['status'],geometry='passed',coreWorldBox=rec['coreWorldBox'],nativeWorldBox=rec['nativeWorldBox'],inspection=ip.as_posix(),reviewedAtUtc=now(),formalAccepted=False)
write(op,o)
rec.update(status='usable_native_repair_overlay',internalSeams='passed_native_overlay_boundary1to1',externalSeams='not applicable: overlay interior only',review=op.as_posix());write(recpath,rec)
sp=ZONE/'selection-r03_c10.json';s=read(sp)
if ident not in s['overlays']:s['overlays'].append(ident)
s.update(updatedAtUtc=now(),internalReview='overlay_passed_pending_reassembled_tile_QA');write(sp,s)
print(json.dumps({'acceptedOverlay':ident,'sha256':rec['sha256']}))
