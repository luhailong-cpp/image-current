import sys
sys.dont_write_bytecode=True
import json,importlib.util
from pathlib import Path
z=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('prod',z/'production.py');prod=importlib.util.module_from_spec(spec);spec.loader.exec_module(prod)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
ledger=read(z/'current-tile-ledger.json');c=ledger['counts'];p=read(z/'progress.json')
pending=[e['tile'] for e in ledger['tiles'] if e['coverage']=='full' and e['internalQa']!='passed']
report={'updatedAtUtc':prod.now(),'targetUnique4kCoordinates':49,'native16Complete4kCandidateCoordinates':c['fullCoverageCoordinates'],'saved4096CandidateCoordinates':c['candidate4096Coordinates'],'internalCheckPassedCoordinates':c['internalPassedCoordinates'],'stillMissingNativeCoordinates':49-c['fullCoverageCoordinates'],'existingCompleteArtPendingRepairOrCheckCoordinates':len(pending),'pendingRepairOrCheckTiles':pending,'exportedArtCoordinates':c['artExportCoordinates'],'nativeCoreSlotsReady':c['nativeSlots'],'nativeCoreSlotsMissing':49*16-c['nativeSlots'],'countingPolicy':'One coordinate counted once. Unavailable global outer neighbors do not reduce this zone native-completion count.'}
orphans=[q.name for q in (z/'native').glob('*.png') if not Path(str(q)+'.generation.json').exists()]
receiptsMissingImage=[q.name for q in (z/'native').glob('*.receipt.json') if not q.with_name(q.name.replace('.receipt.json','.png')).exists()]
report['savedNativeOutputsMissingGenerationRecord']=orphans;report['receiptsMissingSavedImage']=receiptsMissingImage
p.update({'status':'art_production_in_progress','currentTile':'r11_c05','currentPatch':'p04_01','nextStep':'Generate last native core slot; assemble and inspect internal joins, then continue r11c04.','currentScopeSummary':report,'remainingNativeCoreSlots':report['nativeCoreSlotsMissing'],'completeArtPendingRepairOrCheckCount':len(pending),'scopeOuterEdgesExcludedFromMissingCount':True})
prod.write(z/'progress.json',p);prod.write(z/'current-scope-summary.json',report)
print(json.dumps(report))

