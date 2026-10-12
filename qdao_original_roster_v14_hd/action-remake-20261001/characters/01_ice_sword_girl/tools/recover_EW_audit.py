from pathlib import Path
import json,hashlib,re
from datetime import datetime,timezone
from PIL import Image,ImageDraw
r=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/01_ice_sword_girl")
plan=json.loads((r/'review/run-EW-position-pairs-plan.json').read_text(encoding='utf-8-sig'))
reasons={
'E':{4:'右支撑已经移到骨盆后方且足跟抬起，提前进入后蹬；应为身体靠近支撑脚的第2张。',5:'右脚是后蹬前掌姿态，过早；应保持近骨盆下方全掌承重。',6:'双足离地；应右脚在骨盆略后持续支撑。',7:'双足离地；应右后脚前掌仍接地。',8:'已换成远左脚接触，支撑脚提前切换；应保持右脚后蹬接触。',11:'左脚已在骨盆后、右腿通过；应左支撑仍位于前/近中，身体接近脚。',12:'左后跟明显抬起，进入后蹬过早；应左脚全掌承重、身体靠近。',13:'左腿向后伸且足跟抬起；应为身体刚经过左支撑的全掌阶段。',14:'双足离地；应左脚在身体略后保持支撑。',15:'双足离地；应左后脚前掌仍接地。',16:'右脚前摆下落、左脚后折离地；应左脚后蹬保持接触，到下圈01才换右脚。'},
'W':{3:'近左脚形态为承重，但相邻帧鞋底高度突变，且未形成新两帧位置序列；需局部腿脚连续性修正。不能仅以固定Y判错。',4:'左脚已在身后、足跟抬起，提前后蹬；应身体靠近左支撑脚。',5:'左支撑已向后伸且仅前掌低位；应身体刚经过左脚并保留全掌。',6:'双足离地；应近左脚在身后持续承重。',7:'已换为远右脚前落地，近左脚离地；应近左脚后蹬仍接触。',8:'远右脚承重且近左脚离地；应保持近左脚支撑，换脚要到09。',10:'远右支撑已移至身体后方、足跟抬起；应同09为前落地第二张。',11:'远右脚已进入后蹬；应身体仍靠近右脚、全掌承重。',12:'远右足跟高抬，后蹬过早；应右脚全掌支撑。',13:'右支撑在身后且足跟抬起；应身体刚经过右脚并保留全掌。',14:'双足离地；应右脚在身体略后持续接地。',15:'双足离地；应右后脚前掌接地。',16:'已提前转为近左脚接触；应右脚后蹬保持接触，左脚留待下圈01。'}}
out={'schemaVersion':1,'inspectedAt':datetime.now(timezone.utc).isoformat(),'characterId':'01_ice_sword_girl','scope':'E/W native recovery and static visual audit only; no candidate or selection mutations','latestPlan':'review/run-EW-position-pairs-plan.json','latestTiming':{'frames':16,'frameMs':75,'cycleMs':1200},'latestRequirementPassed':False,'recoveredNewNativeCount':0,'unresolvedRepairSlots':24,'newSuccessfulReceiptsAfterPlan':[],'evidence':{'existingSheets':['preview/current-contact-sheet.png','preview/run-W-selected-256.png'],'nativeAdditionalInspection':['drafts/run/E/03-v4.png','drafts/run/E/04-v5.png','drafts/run/W/03-v1.png'],'warning':'The existing E contact sheet labels E03-v3/E04-v2, so current E03-v4/E04-v5 were independently inspected full canvas. No rendered fixed ground line was used as proof of contact.'},'directions':{}}
for d in ['E','W']:
 sel=json.loads((r/f'review/run-{d}-selection.json').read_text(encoding='utf-8-sig'))
 audit=[]; native=[]
 for frame in sel['frames']:
  p=r/frame['sourcePath'];rec=json.loads((r/frame['generationRecord']).read_text(encoding='utf-8-sig'))
  n=frame['frame']; versions=[]
  for q in sorted((r/f'drafts/run/{d}').glob(f'{n:02}-v*.png')):
   rp=Path(str(q)+'.generation.json'); rr=json.loads(rp.read_text(encoding='utf-8-sig')) if rp.exists() else {}
   receipt=rr.get('evidence',{}).get('receipt')
   versions.append({'path':q.relative_to(r).as_posix(),'recordExists':rp.exists(),'receipt':receipt,'receiptExists':bool(receipt and (r/receipt).exists()),'generatedAt':rr.get('generatedAt'),'sha256':hashlib.sha256(q.read_bytes()).hexdigest()})
  native+=versions
  audit.append({'frame':n,'selected':frame['sourcePath'],'selectedSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'selectedRecordHashMatches':frame['sha256']==hashlib.sha256(p.read_bytes()).hexdigest(),'selectedNativeSize':list(Image.open(p).size),'versions':versions,'latestPairTarget':plan['positionPairs'][(n-1)//2],'newRepairReturned':False if n in reasons[d] else None,'status':'needs_native_local_leg_repair' if n in reasons[d] else 'preserve_pending_whole_sequence_review','reason':reasons[d].get(n,'Existing planted pose can be retained as anchor; full sequence and transitions still require review.'),'observedContact':frame['actualContact']})
 sheet=Image.new('RGBA',(4*320,4*350),(194,209,216,255)); draw=ImageDraw.Draw(sheet)
 for i,f in enumerate(sel['frames']):
  p=r/f['sourcePath'];im=Image.open(p).convert('RGBA');im.thumbnail((320,320),Image.Resampling.LANCZOS)
  x=i%4*320;y=i//4*350;sheet.alpha_composite(im,(x,y+25))
  draw.text((x+4,y+4),f"{d}{f['frame']:02} {p.stem} 75ms",fill=(0,0,0,255))
 sheet.save(r/f'review/recovery-{d}-selected.png')
 contacts={'E':{'right':[1,2,3,4,5],'left':[8,9,10,11,12,13],'bothAir':[6,7,14,15,16]},'W':{'left':[1,2,3,4,5,16],'right':[7,8,9,10,11,12,13],'bothAir':[6,14,15]}}[d]
 out['directions'][d]={'selectedCount':16,'nativeVersionCount':len(native),'newSuccessfulOutputsAfterPlan':0,'repairFrameNumbers':plan['repairSlots'][d],'preserveFrameNumbers':plan['reuseAfterActualInspection'][d],'currentVisualSupportHypotheses':contacts,'continuousEightSupportPassed':False,'fourPositionsTwoDistinctPosesPassed':False,'footAxisNote':'Selected side-view toes generally follow travel direction; main failure is support continuity/position timing. Do not convert foot orientation by mirror, rotation, or pixel warp. Ground contact is a visual hypothesis, not client collision evidence.','armNote':'E near anatomical RIGHT hand sword, far LEFT talisman; W near LEFT talisman, far RIGHT sword. Current corrected shoulder-sleeve-elbow-hand chains should remain unchanged in local lower-limb edits.','frames':audit}
(r/'review/recovery-EW.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'report':str(r/'review/recovery-EW.json'),'latestRepairOutputsRecovered':0,'pending':24,'nativeCounts':{d:out['directions'][d]['nativeVersionCount'] for d in ['E','W']}}))

