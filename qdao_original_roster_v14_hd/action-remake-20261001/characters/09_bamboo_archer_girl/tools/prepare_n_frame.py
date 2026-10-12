import json,sys,hashlib
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
f=int(sys.argv[1]);phase=(f-1)%8
leg="RIGHT" if f<=8 else "LEFT";other="LEFT" if f<=8 else "RIGHT"
phases=[
f"{leg} foot makes fresh forward contact ahead in the travel direction (away from camera), {other} leg trails behind toward camera with heel raised. Torso leans into run.",
f"{leg} support knee compresses and pelvis lowers slightly, {other} knee starts recovering, trailing boot lifts. Real weight supported on {leg}.",
f"{leg} support passes under pelvis; {other} knee swings forward away from camera. Boots overlap briefly in depth but remain separate limbs. Empty arm passes through mid swing.",
f"{leg} supporting ankle extends into toe-off, heel high, {other} knee leads forward. A strong real push launches the body; both shoulder and elbow articulate.",
f"Early airborne phase: BOTH boots clearly above virtual ground. {leg} trailing knee folds and the boot sole is visible toward camera; {other} knee leads into next stride. Pelvis rises 15 normalized pixels.",
f"Flight apex: BOTH feet off ground, {other} leg reaches forward away from camera, {leg} folds behind showing some sole; pelvis is 20 normalized pixels high. Not a standing pose.",
f"Late flight: {other} leg begins extending down toward its upcoming contact, {leg} continues recovering behind. Pelvis descends, both feet still briefly clear.",
f"Pre-contact: {other} boot is about to meet ground ahead away from camera, {leg} knee flexes behind. Prepare seamless transition into next opposite-leg contact; pelvis only 3 normalized pixels raised."
]
prompt=f"""Use case: identity-preserve. Produce ONE unique native 1024x1024 or larger square RGBA animation frame run/N/{f:02d} of a 16-frame two-step running cycle. Image1 exact bamboo archer girl identity and north-facing camera; image2 approved primary painting style. Keep the same brown high ponytail, bamboo leaf gold jade hair ornament, ivory jade green gold embroidered short robe, white shorts, white green gold short boots and jewelry. Bright clean rounded chibi hand-painted finish. Full body in frame.
NORTH means moving directly AWAY from camera, seen from BACK exactly as image1; NO face or eye visible, NO turning head to side. Anatomical LEFT equals screen LEFT and always holds the ENTIRE long bamboo bow in one real grip; anatomical RIGHT equals screen RIGHT, empty hand counter-swings with running. Quiver permanently on RIGHT shoulder at screen RIGHT. Retain this asymmetric identity.
Pose phase {phase+1}/8: {phases[phase]}
Left and right legs must ALTERNATE real hip/knee/ankle movement in foreshortening. Arms swing in opposition to corresponding legs: when LEFT leg is forward, LEFT bow arm swings backward toward camera, RIGHT empty arm forward away from camera; reverse when RIGHT leg leads. Bow follows left shoulder/elbow and grip without switching hands; do not lock arms in idle. Sleeve/cuff must connect each hand to the correct shoulder. Keep complete long bow and string; no arrow in hands.
Body lean forward away from camera about 10 degrees, short chibi limbs same as reference, flowing ponytail follows inertia without obscuring all arms. Fixed orthographic rear camera, fixed body/head size and frame scale, normalized ground y940/1024 and root x512/1024. Allow true anatomical vertical bounce per phase, do not put airborne boots onto ground. No lateral stage movement. Same costume design/material and lighting every frame.
Genuinely transparent background, clean transparent margins around hair/bow/boots, no floor or shadow, no particles or trails, no text/grid/sheet, no extra arms, legs, weapons. Independently DRAW this precise phase, not a warped, mirrored or interpolated existing frame."""
refs=["D:/work/image/qdao_original_roster_v14_hd/recovery-20260921/09-delivery-preview/final/runtime/idle/N.png","D:/work/image/designs/jubaozhai-ui/02-characters.png"]
if f>=4 and (ROOT/"runtime/run/N/03.png").exists():
 refs.append(str(ROOT/"runtime/run/N/03.png"))
 prompt += "\nImage3 is the established running character scale and rear camera reference. Keep EXACT head width/height, hair silhouette size, body proportions, ivory/green palette and complete bow design from image3, independently drawing the new required limb pose. This is not a new character illustration. Animate shoulder/elbow substantially rather than freezing the reference hands."
arm_first=[
"LEFT bow arm forward away from viewer, RIGHT empty elbow and fist BACK toward viewer at hip height.",
"LEFT bow arm starts retracting toward waist; RIGHT empty arm begins advancing from behind hip.",
"Both elbows pass mid swing, bow grip near left waist, empty right fist moving forward away from viewer.",
"LEFT bow shoulder swings BACK toward viewer, elbow bends with grip low near left hip. RIGHT empty arm reaches FORWARD away from viewer and is foreshortened.",
"LEFT bow arm back toward viewer and lower than chest; RIGHT empty arm forward away from viewer. Keep shoulder/elbow rotation clear.",
"LEFT bow arm at back swing endpoint near left hip, RIGHT empty arm at forward endpoint (higher and foreshortened).",
"LEFT bow arm remains back but starts smooth reversal, RIGHT empty hand starts retracting from forward swing.",
"LEFT bow hand behind the torso near left hip, RIGHT empty arm forward away from viewer preparing left foot contact."
]
arm_second=[
"LEFT bow arm BACK toward viewer with bent elbow and grip near left hip; RIGHT empty arm FORWARD away from viewer, foreshortened high near right waist.",
"LEFT bow elbow begins swinging forward from the hip, RIGHT empty elbow starts swinging back toward viewer.",
"Both elbows cross mid swing near the torso; LEFT bow arm advancing away, RIGHT empty arm retracting toward viewer.",
"LEFT bow arm FORWARD away from viewer with grip near left lower ribs; RIGHT empty elbow bent BACK toward viewer and fist low beside hip.",
"LEFT bow arm forward away from viewer and slightly higher, RIGHT empty arm back toward viewer at hip height.",
"LEFT bow arm at forward swing endpoint, RIGHT empty arm at backward endpoint; smooth reversal begins.",
"LEFT bow arm starts retracting from forward swing, RIGHT empty hand starts advancing from the hip.",
"LEFT bow arm forward away from viewer, RIGHT empty fist back toward viewer at hip, matching the initial opposite-leg contact phase."
]
prompt += "\nCRITICAL coordination of arm and leg: "+(arm_first if f<=8 else arm_second)[phase]+" The empty hand and bow hand must visibly change shoulder and elbow positions through the cycle. Do not just change the boots under frozen idle arms."
args={"prompt":prompt,"referenced_image_paths":refs,"transparent_background":True}
out=ROOT/"provenance/run-N"/f"run-N-{f:02d}.request.json";out.parent.mkdir(exist_ok=True)
i=1
while out.exists():i+=1;out=ROOT/"provenance/run-N"/f"run-N-{f:02d}.a{i:02d}.request.json"
request={"slot":f"run-N-{f:02d}","requestedAt":datetime.now(timezone.utc).isoformat(),"configSnapshot":json.loads((ROOT.parents[3]/"config/image-generation.json").read_text(encoding="utf-8-sig")),"submittedParameters":{"model":None,"quality":None,**args},"referenceMetadata":[{"path":p,"sha256":hashlib.sha256(Path(p).read_bytes()).hexdigest(),"role":"identity_and_camera" if j==0 else "approved_primary_style"} for j,p in enumerate(refs)],"phase":phases[phase]}
out.write_text(json.dumps(request,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"request":str(out),"args":args},ensure_ascii=False))

