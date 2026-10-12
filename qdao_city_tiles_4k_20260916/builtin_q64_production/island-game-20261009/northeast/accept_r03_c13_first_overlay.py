from native_work import *
ident='r03_c13_cross_02_03_repair'
p=ZONE/'qa'/f'{ident}.overlay.json';q=read(p);q.update(review='passed_internal_geometry_color_and_four_perimeters',reviewedAtUtc=now(),reviewers=['root','contract_review'],notes='Native red lower arm rebuilt with gold end and suspension ring; post color band removed; all four exact overlay edges pass.');write(p,q)
p=ZONE/'native'/f'{ident}.png.generation.json';q=read(p);q.update(status='usable_native_overlay',internalSeams='all four overlay perimeter edges passed',reviewedAtUtc=now());write(p,q)
p=ZONE/'selection-r03_c13.json';s=read(p);s['overlays']=[ident];write(p,s)
for pid in ['r03_c13_p02_03','r03_c13_p02_04','r03_c13_p03_03','r03_c13_p03_04']:
 p=ZONE/'native'/f'{pid}.png.generation.json';q=read(p);q.update(status='usable_native_with_required_overlay',requiredOverlay=ident);write(p,q)
p=ZONE/'native'/'r03_c13_p02_02.png.generation.json';q=read(p);q.update(status='superseded',supersededBy='r03_c13_p02_02_v2',reason='native foliage rectangular cut repaired in v2; historical actual reference retained');write(p,q)
for a,b in [('r03_c13_p02_04','r03_c13_p03_04'),('r03_c13_p03_03','r03_c13_p03_04')]:
 p=ZONE/'qa'/f'{a}__{b}.json';q=read(p);q.update(status='passed_only_with_required_native_overlay',requiredOverlay=ident,reviewedAtUtc=now(),notes='Original isolated core join had upper-corner red beam rectangle; final use requires validated native overlay.');write(p,q)

