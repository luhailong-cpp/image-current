from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1]; project=R.parents[3]
save=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base=json.loads((R/'staging/run-grounding-20261004/run-SE/14-v1.request.json').read_text(encoding='utf-8-sig'))
for n in [13,14,15,16]:
    version=1 if n==13 else 2
    p=R/f'staging/run-grounding-20261004/run-SE/{n:02}-v{version}.request.json'
    assert not p.exists()
    refs=[R/f'frames/run/SE/{n:02}.png',R/'staging/run-grounding-20261004/run-SE/12-v1.png',
          R/'frames/run/SE/11.png',R.parent/'09_bamboo_archer_girl/runtime/run/SE/14.png',
          Path('D:/work/image/designs/jubaozhai-ui/02-characters.png')]
    roles=['edit_target_original_formal','same_character_prior_underbody_support_B_hip_connection',
           'same_character_prior_support_B_hip_identity','bamboo_heading_only_not_phase','approved_style']
    stage={13:'first rear-propulsion pose, heel just rising',14:'second rear-propulsion pose, heel moderately raised',
           15:'first final-forefoot pose, heel higher and ankle extended',16:'last toe-pad contact before opposite foot lands, heel highest'}[n]
    prompt=f'''Use case: precise-object-edit. Edit image1 into one finished transparent chibi sprite, run SE frame{n:02}, native1254x1254 RGBA. Image1 is the exact target with locked head/body/arms; image2 is the immediately prior UNDER-BODY support pose, image3 the prior support pose identifying the SAME anatomical support leg B; image4 only defines SE boot heading, image5 the painted art style.
    Redraw the lower-body LEG CONNECTION AND SUPPORT PHASE, not just a boot angle. This is the {stage}. In images2 and3, B is the leg connected to the SCREEN-RIGHT hip opening below the belt and ending in the large front boot. Keep that SAME hip-to-thigh-to-knee chain as the support. Now extend B BACK BEHIND the pelvis along the opposite of SE travel, placing its forefoot/toe pad down with weight flowing through a straighter calf. The calf must no longer be folded up in recovery. B recedes from its right hip toward the rear screen-left support toe; its thigh passes BEHIND the opposite airborne leg. The other anatomical leg A begins at the SCREEN-LEFT hip, bends/swings FORWARD toward lower-right, overlapping IN FRONT of B; its toe is lifted, sole visible, and not touching ground. Clearly redraw the pants seams, crotch separation and knee overlaps so the former large front support leg in images2/3 is recognizably the leg now pushing behind. Do NOT simply lower image1's original small rear boot, which belongs to the wrong hip. Do NOT keep the existing leg assignment; redraw the two hip connections coherently while preserving the intended stride silhouette. Exactly two anatomically connected legs.
    Both boots' horizontal heel-to-toe directions follow SE, never splayed outward. Ground is implied only: no line, shadow, platform, scene, labels or marks. Depth perspective: rear support toe may be higher on-screen than the airborne near boot, so do not mechanically align both feet on one horizontal pixel line. Keep image1's unique phase and framing; do not copy the prior anchor's pose. Preserve image1's exact head size, face, hairstyle, torso, scarf, arms, hands with both crescent daggers, costume colors/materials and whole-canvas camera registration. No mirror, sprite translation, cropping or scaling; preserve full extremities and clean transparent edges. Change only below the belt as required for this precise coherent leg redraw.'''
    req={'configurationTarget':base['configurationTarget'],'submittedParameters':{'prompt':prompt,'transparent_background':True,'referenced_image_paths':[str(x) for x in refs]},
         'referenceRoles':roles,'references':[{'path':str(x),'sha256':sha(x),'role':r} for x,r in zip(refs,roles)],
         'requestedAt':datetime.now(timezone.utc).isoformat(),'revisionReason':'Full trouser-chain review found premature switch risk in old13-16; retain original B hip as continuous support.'}
    req['editSource']=req['references'][0];save(p,req)
print('Prepared SE13-v1 and SE14/15/16-v2; original formal sources and actual refs frozen.')
