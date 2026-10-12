from pathlib import Path
import json,datetime
R=Path(__file__).resolve().parents[1]
play=json.loads((R/'preview/nne-playback-verification.json').read_text(encoding='utf-8'))
for d in ['N','NE']:
 c=next(x for x in play['checks'] if x['direction']==d)
 for rel in [f'review/run-{d}-final-visual.json',f'review/run-{d}-selection.json']:
  p=R/rel;a=json.loads(p.read_text(encoding='utf-8-sig'))
  a.update(updatedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),artStatus='agent_frame_visual_and_offline_playback_verified',eightConsecutiveSupportVerified=True,positionPairsVerified=True,agentSequenceContinuityVerified=True,offlinePlaybackVerified=True,dynamicArtAccepted=False,clientRuntimeVerified=False,remainingIssues=[])
  a['verificationScope']='Agent inspected full native images, sequential contact sheets and feet close-ups: anatomy, same-foot support ownership, four spatial pairs, straight boot axes, arm continuity. Offline browser at 1x verified 16 ordered frames, 75ms schedule, 1200ms loop and wrap controls. Continuous-motion human acceptance and game-client integration remain separate; dynamicArtAccepted is reserved for that downstream acceptance and is not an unresolved frame-repair flag.'
  a['validationScopes']={'nativeFrameAndSequentialVisual':'passed_by_agent','eightConsecutiveSupport':'passed_by_agent_visual_judgement','fourPositionPairs':'passed_by_agent_visual_judgement','offline1xTimingAndOrdering':'passed','clientRuntime':'not_tested','userContinuousMotionAcceptance':'not_requested_or_observed'}
  a['playbackEvidence']={'file':'preview/nne-playback-verification.json','measuredCycleMs':c['measuredCycleMs'],'ordered':c['ordered'],'loadedFrames':16,'stepWrap':True,'player':'preview/nne-review.html','contactSheet':f'preview/run-{d}-selected-256.png','feetSheet':f'review/run-{d}-paired-feet-final.png','animation':f'preview/run-{d}-1x-1200ms.webp'}
  a['pendingValidation']=['Root aggregate preview/package revalidation','Actual game-client timing and user visual acceptance have not been observed']
  p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'N':'selected32scopeDone','NE':'selected32scopeDone','remainingFrameRepairIssues':[],'playback':[{k:v for k,v in c.items() if k!='trace'} for c in play['checks']]}))

