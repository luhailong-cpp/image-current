from native_work import *
ident='r05_c14_cross_floor_tone_repair'; qpath=ZONE/'qa'/f'{ident}.overlay.json'; q=read(qpath); q.update(review='passed_native_full_and_four_perimeters',reviewedAtUtc=now(),finding='Faint rectangular floor-tone artifact removed; exact native crop perimeter joins inspected at1:1 including external left tile. Stone-joint geometry preserved.'); write(qpath,q)
gp=ZONE/'native'/f'{ident}.png.generation.json'; g=read(gp); g.update(status='usable_internal_reviewed',internalSeams='passed_four_overlay_perimeters',reviewNote=q['finding'],reviewedAtUtc=now()); write(gp,g)
sp=ZONE/'selection-r05_c14.json'; s=read(sp); assert ident not in s['overlays']; s['overlays'].append(ident); write(sp,s)

