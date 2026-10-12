from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json
r=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/07_moon_shadow_assassin_girl')
m=json.loads((r/'manifest.json').read_text(encoding='utf-8'))
edges={}
for f in m['frames']:
 im=Image.open(r/f['path']);a=im.getchannel('A')
 e=sum(v>8 for box in [(0,0,1024,1),(0,1023,1024,1024),(0,1,1,1023),(1023,1,1024,1023)] for v in a.crop(box).getdata())
 if e:edges[f['id']]=e
assert not edges,edges
report={'reviewedAt':datetime.now(timezone.utc).isoformat(),'reviewer':'root with direction-agent source audits','offlineAccepted':True,'scope':'offline artwork; all196 actual frame contact sheets, targeted native inspections, per-direction native agent audits, browser normal/quarter-speed playback samples and step controls','acceptedSHA256':{f['id']:f['sha256'] for f in m['frames']},'reviewedGroups':sorted(set(f['action']+'/'+f['direction'] for f in m['frames'])),'anatomy':'No extra hand/leg/dagger or detached grip observed in selected frames. Broad trousers and perspective naturally occlude far limbs. Targeted phase corrections are preserved in provenance records.','latestRepairs':['run/E02-v3,E10-v2 bearing','run/E11-v2 support/recovery outline separation','run/NW16-v2 loop hand transition','run/NE04-08 and13 support/flight leg continuity','run/S02-v2,04-v2,10-v2,12-v2 bearing/support','run/W14-v2 short flight','run/SE09-v4,10-v2 heel contact and flat weight bearing','run/SW04-v2,12-v2 compact support transition','hit/E02-v2 extra-hand removal,05-v2 guard recovery','attack/E11-v2 head/hand recovery;W03-v3 scarf containment','cast/E04-v2 gathering,09-v4 blade containment,15-v3 wrist; real source09/10 reordered for inward recoil'],'playbackEvidence':{'browser':'Codex in-app browser localhost8767','normalRun':'all8 groups loaded and played at160px; E also256px with480/640/720/800 comparisons','slowAndStep':'browser1/4 speed and individual-frame controls; full static sequences inspected at300px thumbnails and selected1254 originals','combat':'all6 groups normal and1/4 playback at256px','limits':'UI playback and captured frames plus sequential static review; no recorded-video analysis or client execution claimed.'},'timingDecision':{'runCycleMs':720,'E':'64ms each on02,03,10,11; other frames38/39ms;720 total','otherRunDirections':'45ms each,720 total','reason':'Longer cycle makes contact and support readable; E support is retained longer. Pose redrawing completed independently of timing change.','combatUnchanged':True},'alphaBoundaryPixelsAbove8':0,'rootDecision':'review/ground-root-review.json','phaseEvidence':'review/run-phase-review.json','clientIntegration':'not_performed','clientRisks':['Actual world-displacement speed, sliding and shadow/root plane must be checked in client.','SE far/near leg identity remains less explicit than SW because loose trousers overlap; no duplicated limb observed.'],'remainingRequiredRedraws':[]}
(r/'review/final-visual-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('All196 current exports reviewed; no opaque alpha boundary pixels.')

