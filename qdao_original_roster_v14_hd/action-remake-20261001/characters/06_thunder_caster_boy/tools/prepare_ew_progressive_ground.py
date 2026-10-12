from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
identity='D:/work/image/q_daoist_character_pack_4096/06_thunder_caster_boy_transparent_4096.png'
style='D:/work/image/designs/jubaozhai-ui/02-characters.png'
for d in ['E','W']:
 front='screen right' if d=='E' else 'screen left'
 back='screen left' if d=='E' else 'screen right'
 near='right' if d=='E' else 'left'
 for i in [2,3,4,5,6,7,10,11,12,13,14,15]:
  support='right' if i<8 else 'left';swing='left' if i<8 else 'right';n=i%8
  rec=json.loads((R/f'runtime/run/{d}/{i:02}.png.generation.json').read_text(encoding='utf-8-sig'))
  src=R/rec['derivedFrom'][0]['file']
  pos={2:'front-side early weight bearing: the support ankle is about half a boot length AHEAD of the hip, support knee softly flexed; support heel and forefoot fully flat. The swing foot is folded behind but its knee is starting to pass forward',3:'front-side later weight bearing: the support ankle is about one quarter boot length AHEAD of the hip, support knee bends a little deeper; support heel and forefoot fully flat. The swing knee passes alongside the support knee with foot still airborne',4:'body passing directly over support: the support ankle is vertically UNDER the hip and supports the weight through a naturally flexed knee; heel and forefoot both flat. The other thigh/knee swings forward and the other boot stays raised',5:'body just passed support: the support ankle is one quarter boot length BEHIND the hip; sole remains flat and knee starts to extend. The other knee is clearly forward and its boot remains airborne',6:'rear-side push begins: the support ankle is half a boot length BEHIND the hip; forefoot presses on ground and heel rises slightly, natural ankle flexion, no sideways roll. The other shin unfolds toward the upcoming forward landing, still airborne',7:'rear-side final push: the support ankle is three quarters boot length BEHIND the hip; forefoot and toe stay in contact while the heel is visibly raised, supporting a forward push. The other leg reaches forward with knee slightly bent and its heel remains just above ground, ready for the next frame landing'}[n]
  prompt=f'''Use case: precise-object-edit. One transparent RGBA sprite, Thunder Caster Boy running {d}, frame {i:02}. Edit Image 1 into the required lower-body pose, while precisely retaining its face, hair, head placement and scale, upper torso, shoulder-elbow-hand counter-swing, right-hand gold lightning scepter, left-hand rectangular gold taiji plaque, costume details, canvas margins and camera.
This is the {support.upper()}-leg support half of a continuous run. The anatomical {support} leg MUST remain the grounded support leg, and the anatomical {swing} leg MUST be the airborne recovery leg. Near-side leg from this camera is anatomical {near}; keep the appropriate front/back occlusion and trace both legs separately from the hips. Redraw the necessary thighs, knees, shins and boots as a coherent NEW pose; do not slide or warp the existing cutout.
Exact required stance: {pos}. Forward is {front}; behind is {back}. Both boot toes and knees stay in the forward travel plane toward {front}, with no outward splay, no frontal toes in this side view. The horizontal virtual ground is at approximately 94 percent of the ORIGINAL native canvas height, consistent with Image 2's planted sole. Do not stretch the white shin wrap to reach it. Natural short chibi legs with knee and ankle flexion, weight clearly above the grounded chain. Do not draw a ground line or shadow.
Image 1 is the composition and identity master, its current legs need this pose correction. Image 2 is this boy's same-direction initial landing and proportion reference only; do not copy its pose or arm arrangement. Image 3 is authoritative identity only. Image 4 is approved painted style only. Image 5 is the user-approved archer's same-direction foot axis reference only; do not copy her character or pose.
Keep the single full figure, genuine transparency, gold ivory navy clothing, turquoise details and black/gold boots. No new objects, effects, text, floor, duplicated limb, zoom, recentering, whole-image movement or camera change.'''
  stem=f'run_{d}_{i:02}_progress_v1'
  refs=[{'path':str(src).replace('\\','/'),'role':'exact frame edit target; retain camera and upper-body counter-swing'}, {'path':str(R/'work'/json.loads((R/f'runtime/run/{d}/{0 if i<8 else 8:02}.png.generation.json').read_text(encoding='utf-8-sig'))['derivedFrom'][0]['file'].split('/')[-1]).replace('\\','/'),'role':'same-character same-direction support ground and proportion reference only'}, {'path':identity,'role':'authoritative identity only'},{'path':style,'role':'approved painted finish'},{'path':f'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/09_bamboo_archer_girl/runtime/run/{d}/09.png','role':'user-approved same-direction foot axis only'}]
  (R/'prompts'/f'{stem}.txt').write_text(prompt,encoding='utf-8')
  (R/'records'/f'{stem}_references.json').write_text(json.dumps(refs,ensure_ascii=False,indent=2),encoding='utf-8')
batch=[]
for p in sorted((R/'prompts').glob('run_[EW]_??_progress_v1.txt')):
 batch.append({'stem':p.stem,'prompt':p.read_text(encoding='utf-8'),'references':json.loads((R/'records'/f'{p.stem}_references.json').read_text(encoding='utf-8'))})
(R/'records/run_ew_progress_batch.json').write_text(json.dumps(batch,ensure_ascii=False),encoding='utf-8')
print('Prepared 24 independent native edit prompts; no generation/export implied.')
