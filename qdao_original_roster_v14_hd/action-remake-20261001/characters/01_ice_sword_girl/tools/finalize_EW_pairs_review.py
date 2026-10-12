from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc).isoformat()
technical=read(R/'review/run-EW-pairs-technical.json')
playback=read(R/'review/run-EW-position-playback.json')
assert technical['pass'] and playback['technicalPlaybackPassed']
directions={}
for d in ['E','W']:
 p=R/f'review/run-{d}-selection.json';s=read(p)
 s.update({'reviewedAt':now,'artStatus':'paired_support_static_verified_offline_timing_verified','eightConsecutiveSupportVerified':True,'positionPairsVerified':True,'staticEightContinuousSupportObserved':True,'footAxisVerified':True,'armOwnershipVerified':True,'offlinePlaybackTechnicalVerified':True,'dynamicArtAccepted':False,'remainingIssues':[],
 'verificationLimits':['逐张原生图与128/256整画布连续帧表已检查；浏览器真实1倍循环验证了加载、帧序和时长。动态美术主观顺滑度没有以播放器计时结果代替验收。','素材预览没有客户端位移或地面碰撞；clientIntegrated/clientRuntimeVerified保持false。'],
 'visualEvidence':{'nativeImagesInspected':True,'sheets':[f'preview/run-{d}-selected-128.png',f'preview/run-{d}-selected-256.png'],'timingReport':'review/run-EW-position-playback.json','technicalReport':'review/run-EW-pairs-technical.json','player':'review/run-EW-position-player.html','loopPreviews':[f'preview/run-{d}-paired-1x-128.webp',f'preview/run-{d}-paired-1x-256.webp']}})
 s['observedSupport']={'right':list(range(1,9)) if d=='E' else list(range(9,17)),'left':list(range(9,17)) if d=='E' else list(range(1,9)),'bothAir':[],'simultaneousFullSole':[]}
 s['observedPositionPairs']=[{'frames':[i,i+1],'supportFoot':('right' if d=='E' else 'left') if i<9 else ('left' if d=='E' else 'right'),'observedPosition':['front_landing','body_approaches_foot','body_passes_foot','rear_push_contact'][((i-1)//2)%4],'twoDistinctNativeImages':s['frames'][i-1]['sha256']!=s['frames'][i]['sha256']} for i in range(1,17,2)]
 for f in s['frames']:
  rp=R/f['generationRecord'];rec=read(rp)
  rec['visualReview']={'status':'static_frame_and_sequence_verified','reviewedAt':now,'selection':p.relative_to(R).as_posix(),'actualContact':f['actualContact'],'footAxesFollowTravel':True,'anatomicalRightSwordLeftTalisman':True,'dynamicArtAccepted':False,'clientRuntimeVerified':False}
  write(rp,rec)
 write(p,s);directions[d]={'selectedCount':16,'selectedNativePaths':[f['sourcePath'] for f in s['frames']],'observedSupport':s['observedSupport'],'positionPairs':s['observedPositionPairs'],'remainingKnownStaticDefects':[],'eightConsecutiveSupportVerified':True,'positionPairsVerified':True,'dynamicArtAccepted':False,'selection':p.relative_to(R).as_posix()}
old=read(R/'review/recovery-EW.json');initial=old.get('initialAudit',old)
result={'schemaVersion':2,'initialAudit':initial,'inspectedAt':now,'characterId':'01_ice_sword_girl','scope':'E/W run native production, selected candidates, static visual sequence and offline browser timing. No other direction, combat, root manifest or client files changed.','latestTiming':{'frames':16,'frameMs':75,'cycleMs':1200},'latestStaticRequirementPassed':True,'unresolvedRepairSlots':0,'newSelectedNativeCount':24,'directions':directions,'technicalReport':'review/run-EW-pairs-technical.json','offlinePlaybackReport':'review/run-EW-position-playback.json','knownStaticDefects':[],'dynamicArtAccepted':False,'clientRuntimeVerified':False,'verificationLimit':'Offline browser timing and individual frame visual review do not establish subjective full-motion acceptance or client integration.','rejectedExamples':{'E':['drafts/run/E/06-v2.png: both boots grounded','drafts/run/E/07-v2.png: wrong early support transfer','drafts/run/E/07-v3.png: support valid but opposite swing shin folded back, superseded by07-v4'],'W':['drafts/run/W/04-v4.png: upperbody pose copied from pose reference','drafts/run/W/05-v3.png: arm drift and both boots grounded','drafts/run/W/06-v4.png: arm drift and both boots grounded','drafts/run/W/12-v3.png: support boot moved behind body too early','drafts/run/W/14-v3.png: opposite swing foot folded back between forward poses']},'NWReadOnlyAudit':{'selectedSnapshot':'07-v5/08-v5','findings':'No clear both-air, toe-splay or sword/talisman ownership error in the inspected16-frame sheet. Left support01–08 front-to-rear progression was less readable than right09–16, especially05/06 to07/08. Reported to root for repair.','unselected07v7':'Grounded shin/boot shifts to image-right behind raised sole, visually reads as far RIGHT support; near LEFT support continuity is no longer reliably readable. Do not accept as left-support07. Root informed; no NW files altered.'}}
write(R/'review/recovery-EW.json',result)
print(json.dumps({'directions':['E','W'],'newSelectedNativeCount':24,'staticPairsVerified':True,'offlineTimingVerified':True,'knownStaticDefects':0,'dynamicArtAccepted':False,'clientRuntimeVerified':False}))
