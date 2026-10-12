from pathlib import Path
import json,hashlib
Z=Path(__file__).resolve().parent
p=Z/'west-current-selection-20261012.json';d=json.loads(p.read_text(encoding='utf-8-sig'))
q=d['partialTiles'][0];assert q['tileId']=='r05_c02'
q.update({'selectedNativeStems':[],'rejectedNativeStems':['r05_c02_s01_01_a01'],'unusedPreparedGuides':['r05_c02_s01_02_a01','r05_c02_s02_01_a01'],'rejectionReason':'The warm bronze cauldron left flank was incorrectly interpreted as a straight orange wall; retain original, do not propagate. a02 uses correct giant convex bronze cauldron identity.','inflightStem':'r05_c02_s01_01_a02','status':'first_cauldron_patch_targeted_redraw_inflight','northAnchor':d['currentTile']['candidate'],'rightAnchor':{'path':str(Z/'tiles/connected-r04-r05-cross-v3/r05_c03_cross-jar-base-v1_4096.png'),'sha256':'f2cb254ff1688236c8249609fc69391042e4d8d41696ac2340f6669f1adfbad6'}})
d['currentTile']['status']='owner_33_and5_extra_PASS_strict_native_replay_PASS_root21_PASS_awaiting_independent12_horizontal'
p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf8')

