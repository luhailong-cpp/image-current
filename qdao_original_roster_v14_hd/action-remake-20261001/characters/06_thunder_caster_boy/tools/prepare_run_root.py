"""Save independent generation specifications for root-owned SE/S run slots."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[3]
identity=str(REPO/'q_daoist_character_pack_4096/06_thunder_caster_boy_transparent_4096.png')
style=str(REPO/'designs/jubaozhai-ui/02-characters.png')
phases=[
 'RIGHT foot first contact: right foot reaches forward and down, heel lands at y92%, left leg trails back with heel raised at y83%. LEFT plaque arm forward, RIGHT scepter arm backward. Body leans forward 10 degrees. Medium stride, not a giant leap.',
 'RIGHT foot weight acceptance: planted right sole at y92%, right knee starts bending, pelvis lowers 1%; left heel lifts behind and begins coming through. LEFT plaque forearm moves a little closer to torso, RIGHT scepter forearm begins forward return.',
 'RIGHT mid-support: right foot beneath pelvis with knee compressed and sole on y92%; left knee passes forward under hips, left boot lifted at y85%. Pelvis at lowest point y68%. Both arms pass close to sides, elbows bent, opposite to legs.',
 'RIGHT toe-off: right leg moves behind and pushes using toe at y92%, heel raised; LEFT knee leads forward bent, boot at y84%. Pelvis rises to y65%. RIGHT scepter arm swings forward, LEFT plaque arm swings backward.',
 'First flight: both feet off ground. LEFT knee leads bent with boot y86%, RIGHT heel folds behind at y81%. RIGHT scepter arm forward, LEFT plaque arm backward. Pelvis y64%. Short running flight, no jump pose.',
 'Descending first flight: LEFT knee advances and begins straightening, left boot at y88%, RIGHT heel remains tucked behind at y82%. RIGHT scepter arm approaches forward extreme, LEFT plaque forearm back. Pelvis y65%. Both feet still off ground.',
 'LEFT approaching contact: LEFT lower leg extends moderately down-forward with boot y90%, RIGHT foot behind remains raised y84%. RIGHT scepter arm forward, LEFT plaque arm back; torso moderate forward lean. No grounded foot yet.',
 'LEFT pre-contact: LEFT heel just above y92% at y91%, toes lightly up, RIGHT thigh begins swinging from behind. RIGHT scepter arm begins reversing from forward extreme, LEFT plaque arm begins forward return. Pelvis y66%.',
 'LEFT foot first contact: LEFT heel lands forward on y92%, RIGHT leg trails back with heel at y83%. RIGHT scepter arm forward, LEFT plaque arm backward. Medium stride. Same camera and scale as right contact, not mirrored props.',
 'LEFT weight acceptance: planted left sole at y92%, left knee starts bending, pelvis lowers1%; RIGHT heel lifts behind and begins coming through. RIGHT scepter forearm returns toward torso, LEFT plaque forearm starts forward swing.',
 'LEFT mid-support: LEFT foot beneath pelvis with knee compressed, sole y92%; RIGHT knee passes forward under hips with boot y85%. Pelvis low at y68%. Both arms close to sides in their continuous counter-swing.',
 'LEFT toe-off: LEFT leg behind pushes using toe at y92%, heel raised; RIGHT knee leads forward bent with boot y84%. Pelvis rises to y65%. LEFT plaque arm swings forward, RIGHT scepter arm swings backward.',
 'Second flight: BOTH boots airborne. RIGHT knee leads forward bent with boot y86%, LEFT heel folds behind at y81%. LEFT plaque arm forward, RIGHT scepter arm backward. Pelvis y64%. Short running flight with clear limb separation.',
 'Descending second flight: RIGHT knee advances and begins extending, right boot y88%, LEFT heel tucked behind at y82%. LEFT plaque arm approaches forward extreme, RIGHT scepter forearm back. Pelvis y65%. Both feet off ground.',
 'RIGHT approaching contact: RIGHT lower leg extends down-forward with boot y90%, LEFT foot behind raised y84%. LEFT plaque arm forward, RIGHT scepter arm back. Moderate lean. Neither foot grounded yet.',
 'RIGHT pre-contact returning toward frame00: RIGHT heel just above ground at y91%, toes slightly up, LEFT thigh begins swinging from behind. LEFT plaque arm begins reversing from forward extreme, RIGHT scepter arm starts forward return. Pelvis y66%.'
]
for direction in ['SE','S']:
 refs=[{'path':identity,'role':'authoritative identity'}, {'path':str(REPO/f'qdao_original_roster_v14_hd/recovery-20260921/06-final/runtime/idle/{direction}.png'),'role':f'authoritative {direction} camera/scale'}, {'path':style,'role':'approved painted style'}]
 camera=('SOUTHEAST, three-quarter FRONT view looking diagonally down-right, both eyes visible. RIGHT anatomical limbs on viewer-left, LEFT limbs on viewer-right. Motion goes diagonally toward lower-right; forward arm/foot moves toward camera/right. Do not turn into full side profile.' if direction=='SE' else 'SOUTH, FRONT view looking directly at viewer, symmetric camera, two eyes equally visible. RIGHT anatomical limbs on viewer-left, LEFT limbs on viewer-right. Motion directly toward camera. Forward foot looks slightly larger from mild foreshortening; trailing boot partially behind but visible. Do not rotate camera into diagonal view.')
 for frame,phase in enumerate(phases):
  stem=f'run_{direction}_{frame:02d}_v1'
  if (ROOT/f'runtime/run/{direction}/{frame:02d}.png').exists(): continue
  prompt=f'''Use case: stylized-concept. ONE independent production game animation sprite, {direction} RUN frame {frame:02d}/16. Reference1 identity; reference2 exact direction, scale and framing; reference3 approved painted finish.\nCamera: {camera}\nPose: {phase}\nKeep character proportions and canvas scale exactly like reference2. Hair plus ponytail occupies y13%-48%, face chin near y48%; belt/pelvis center x50% y66% with only stated vertical bob. Fixed invisible ground y92%. Anatomical right/left never swap. Right hand always holds pointed short gold taiji thunder scepter, left hand always holds rectangular gold taiji plaque. True shoulder and elbow counter-swing, natural correct grip and thumbs. Two hands/two legs/two boots only, no spare hand near waist. Medium short stocky legs, GOLD trimmed black boots with WHITE cross-wrapped shins, navy baggy lightning trousers, ivory/gold embroidered robe and navy lining. Rounded cute young face, amber eyes, layered brown short hair/high little ponytail, gold ribbons/turquoise beads. Cloth and ribbons trail with moderate inertia, do not obscure feet or hands. Clean refined painted shading and material richness like reference3, preserve identity of ref1, do not imitate UI. Single full character on genuine transparent alpha, native square at least1024. No shadow, floor, lightning, particles, motion trails, label, grid, text, or extra person. Do not crop or enlarge head. Distinct real anatomical pose, no mirrored body, no duplicated silhouette. Target GPT Image2.5Sunburst/max; host-managed parameters.\n'''
  (ROOT/'prompts'/f'{stem}.txt').write_text(prompt,encoding='utf-8')
  (ROOT/'records'/f'{stem}_references.json').write_text(json.dumps(refs,ensure_ascii=False,indent=2),encoding='utf-8')
print('Saved prompts and actual-reference lists for missing SE/S slots.')
