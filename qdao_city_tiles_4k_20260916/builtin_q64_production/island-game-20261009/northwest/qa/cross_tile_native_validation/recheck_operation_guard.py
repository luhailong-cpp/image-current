"""Focused recheck of the operation-cycle guard added after the main suite."""
import json, sys
from pathlib import Path
import numpy as np
Z=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(Z))
import apply_native_tile_repair as r
import cross_tile_native_repair as c
report_path=Path(__file__).with_name("validation.json")
report=r.read_json(report_path); root=Path(report["fixtureDirectory"])
r.ZONE=root; r.NATIVE=root/"native"
def oracle(pixels,record,path):
    assert record.get("syntheticTestOnly") is True
    index=record["fixtureIndex"]; y,x=np.indices((4096,4096),dtype=np.uint16)
    assert np.array_equal(pixels[:,:,0],(x+17*index)%251)
    assert np.array_equal(pixels[:,:,1],(y+31*index)%253)
    assert np.array_equal(pixels[:,:,2],(x//19+y//23+43*index)%255)
    return {"tileId":record["tileId"],"tileOrigin":r.tile_origin(record["tileId"]),
      "fullNativeCoverage":True,"verifiedPixelCount":4096**2,"originalRawSourceCount":0,
      "rootAssembly":r.file_info(path),"rootProvenance":{"syntheticTestOnly":True},
      "originalCellContributions":[],"priorRepairCount":0,"syntheticTestOnly":True}
r.validate_assembly=oracle
operation=root/"out/four.cross-native-operation.json"
try: c.validate_operation(operation,{operation})
except ValueError as error:
    assert "Cyclic" in str(error)
else: raise AssertionError("Operation-record cycle guard failed")
single=root/"out/single_followup.png"
_,proof=r.validate_base(single,single.with_suffix(".native-repair.json"))
assert proof["priorRepairCount"]==2 and proof["crossTileRepairReferenceAvailability"][-1]["fullReferenceAvailability"]
report["checks"]["operation_record_cycle_guard"]={"pass":True}
report["checks"]["new_guard_single_repair_chain_replay"]={"pass":True}
report["checkCount"]=len(report["checks"])
report["validatedModules"]=[r.file_info(Z/"cross_tile_native_repair.py"),r.file_info(Z/"apply_native_tile_repair.py")]
report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"status":"passed","checkCount":report["checkCount"],"report":str(report_path)}))
