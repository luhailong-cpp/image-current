"""Prepare exact native conditioning only; no generation or synthetic repair.

All writes remain inside this task directory. Source art and manifests are read
only. No resizing, interpolation, blending, feathering, color operation or drawn
geometry is performed. The provisional p14 is explicitly labeled throughout.
"""
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path

from PIL import Image

OUT = Path(__file__).resolve().parent
BASE = OUT.parent.parent
AUTHORITY = Path("D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json")
HELPER = BASE / "review_external_seams.py"
P14 = BASE / "r12_c08/processed/joint-edge-color-v1/p14-joint-edge-color.png"
RAIL = BASE / "r12_c08/repairs/r12c08-rail-joint-v4-edge-color.png"
RAIL_RECORD = BASE / "r12_c08/qa/rail-v4-local-adoption.json"
RAIL_FRAME = [32150, 44941, 33404, 46195]
RAIL_BOX = [32470, 45066, 32800, 45491]
GUIDE_BOX = [32150, 45250, 33404, 46504]
STEM = "r12c08-wall-rock-conditioned-v1"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write(path, data):
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


spec = importlib.util.spec_from_file_location("external_source_helper", HELPER)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
sources = helper.Sources()
canonical = sources.tile("r12_c08")
assert len(canonical["selection"]["patches"]) == 15
assert "p14" not in canonical["selection"]["patches"]
canonical["selection"]["patches"]["p14"] = str(P14)

art, pieces, missing = sources.extract(GUIDE_BOX)
assert not missing, missing
assert art.size == (1254, 1254)
for piece in pieces:
    if (piece["tile"], piece["patch"]) == ("r12_c08", "p14"):
        piece["selectionStatus"] = "explicit unselected provisional override; canonical p14 remains missing"
    else:
        piece["selectionStatus"] = "current canonical selection"

rail_record = read(RAIL_RECORD)
assert rail_record["joint"] == str(RAIL)
assert rail_record["sha256"] == sha(RAIL)
assert rail_record["adoptionBox"] == RAIL_BOX
assert rail_record["p14Sha256"] == sha(P14)
rail_intersection = [max(GUIDE_BOX[0], RAIL_BOX[0]), max(GUIDE_BOX[1], RAIL_BOX[1]),
                     min(GUIDE_BOX[2], RAIL_BOX[2]), min(GUIDE_BOX[3], RAIL_BOX[3])]
rail_crop = [rail_intersection[0] - RAIL_FRAME[0], rail_intersection[1] - RAIL_FRAME[1],
             rail_intersection[2] - RAIL_FRAME[0], rail_intersection[3] - RAIL_FRAME[1]]
rail_destination = [rail_intersection[0] - GUIDE_BOX[0], rail_intersection[1] - GUIDE_BOX[1]]
with Image.open(RAIL) as rail:
    assert rail.size == (1254, 1254)
    rail_piece = rail.convert("RGB").crop(rail_crop)
    art.paste(rail_piece, rail_destination)
assert art.crop((rail_destination[0], rail_destination[1],
                 rail_destination[0] + rail_piece.width,
                 rail_destination[1] + rail_piece.height)).tobytes() == rail_piece.tobytes()

guide = OUT / (STEM + "-guide-native1254.png")
assert not guide.exists(), "Never overwrite an existing versioned guide"
art.save(guide)

native_target = OUT / (STEM + "-p14-provisional-native1254.png")
assert not native_target.exists()
native_target.write_bytes(P14.read_bytes())
assert sha(native_target) == sha(P14)

regions = [
    {"id": "G4", "worldBox": [32600, 45530, 32768, 46080],
     "guideBox": [450, 280, 618, 830],
     "editPurpose": "Repair left p14 masonry courses, crevice plants and rock edges to match fixed c09 right core at x32768."},
    {"id": "G5", "worldBox": [32580, 45920, 32768, 46080],
     "guideBox": [430, 670, 618, 830],
     "editPurpose": "Repair upper p14 rock silhouettes to match fixed p24 below y46080; lower source is immutable."}
]
prompt = """Use case: precise-object-edit
Asset type: native fishing-village isometric map seam repair; opaque 1254x1254 frame.
Primary request: Edit only the two small adjoining masonry and foreground rock discontinuities in Image 1. This is a native same-scale edit, not a new scene. Image 1 is the exact assembled current native pixels and the sole geometry authority. Image 2 is the full provisional p14 tile for context only; do not borrow its incorrect right or lower halo geometry.
Image 1 frame: world [32150,45250,33404,46504], one source pixel per output pixel. The vertical join at local x618 is world x32768. The horizontal join at local y830 is world y46080.
G4 masonry: Work only LEFT of x618, within local x450..617,y280..829. Repair the gray/cyan coping-block front face bottom edges and the next lower wall course so their courses, gaps, top faces, perspective and silhouettes meet the existing fixed right side at x618. Retain the same block scale and wall slope. Make the stone crevice plants and small foreground boulders cross the join naturally without truncated shapes. Use the RIGHT of x618 as fixed edge conditions; do not move or replace the right blocks.
G5 rock: Work only ABOVE y830, within local x430..617,y670..829. Connect the foreground boulder outlines and plant gaps to the exact existing rocks below y830 without rectangular cuts. Retain rock mass, natural gray stone and the current painterly surface. Use the BELOW y830 as fixed edge conditions; do not move or replace those rocks.
Invariants: All pixels outside these two stated edit rectangles must stay visually unchanged. In particular keep every pixel x618..1253 and y830..1253 unchanged, the top 280 pixels unchanged, the current paving, existing wood rails and post unchanged. The approved stepped timber connector and rail geometry at local x320..649,y0..240 are locked. Do not touch any wood, add a rail or post, change daylight, shift perspective, alter scale, crop or resize. Keep every distant rock and plant in place. No global recolor, blur, haze, seam feathering, texture replacement or stylization pass.
Style: Crisp rounded painterly Q-style Daoist game art under clear daylight; preserve the first image's stone material, edges and colors. Opaque complete frame. No text, guides, labels, borders, characters, UI or watermark.
Output: Exactly the same framing and native pixel scale as Image 1, 1254x1254. Repair both G4 and G5 together as one local continuous wall-and-rock edit.
"""
prompt_path = OUT / (STEM + ".prompt.txt")
prompt_path.write_text(prompt, encoding="utf-8")
request = {
    "schemaVersion": 1, "preparedAtUtc": datetime.now(timezone.utc).isoformat(),
    "status": "prepared_only_not_submitted", "generationSubmitted": False,
    "builtinOnly": True, "paidApiAllowed": False,
    "authority": {"file": str(AUTHORITY), "sha256": sha(AUTHORITY)},
    "toolInput": {"prompt": prompt, "referenced_image_paths": [str(guide), str(native_target)],
                  "transparent_background": False},
    "referenceRoles": ["edit target: exact current native core assembly with explicit p14 provisional override and approved rail rectangle", "context only: unselected p14 provisional full native tile; right and lower halo are not boundary authorities"],
    "globalBox": GUIDE_BOX, "expectedDimensions": [1254, 1254],
    "editRegions": regions, "protectedRailBoxGlobal": RAIL_BOX,
    "outputPolicy": "Save generated raw output under this versioned stem with generation receipt. Reject changed scale or framing; never resize it. Root owner must review output and exact native adoption boundaries before selection.",
    "subagentGenerationPermission": "No generation call by preparing agent until root later authorizes built-in generation.",
    "formalAccepted": False, "promotedToSelected": False
}
request_path = OUT / (STEM + ".request.json")
write(request_path, request)

evidence = []
for ident, box in [
    ("G4-wall-before-native", [32600,45530,32940,46080]),
    ("G5-rock-before-native", [32580,45920,32800,46240]),
    ("G4-G5-cross-before-native", [32480,45760,33056,46400])
]:
    crop = art.crop((box[0]-GUIDE_BOX[0],box[1]-GUIDE_BOX[1],
                     box[2]-GUIDE_BOX[0],box[3]-GUIDE_BOX[1]))
    path = OUT / (ident + "-v1.png")
    assert not path.exists()
    crop.save(path)
    evidence.append({"file":str(path),"sha256":sha(path),"globalBox":box,
                     "dimensions":list(crop.size),"operation":"exact mechanical guide crop; no resizing"})

manifest = {
    "schemaVersion": 1, "preparedAtUtc": datetime.now(timezone.utc).isoformat(),
    "task": "r12_c08 p14 G4/G5 targeted native conditioning", "status": "prepared_not_generated",
    "guide": {"file":str(guide),"sha256":sha(guide),"globalBox":GUIDE_BOX,
              "dimensions":[1254,1254],"pixelScale":"1:1 native pixels"},
    "sourcePieces":pieces,
    "protectedRailOverlay": {"file":str(RAIL),"sha256":sha(RAIL),"sourceFrameWorld":RAIL_FRAME,
                             "approvedBoxWorld":RAIL_BOX,"guideIntersectionWorld":rail_intersection,
                             "sourceCrop":rail_crop,"destination":rail_destination,
                             "pixelReplayVerified":True,"record":str(RAIL_RECORD),"recordSha256":sha(RAIL_RECORD)},
    "copiedP14Context": {"file":str(native_target),"sha256":sha(native_target),"source":str(P14),
                        "status":"unselected provisional; p14 remains absent from canonical selection"},
    "protectedBoundaryContext": {"eastWorldX":32768,"eastGuideX":618,
                                  "southWorldY":46080,"southGuideY":830,
                                  "southContextPixels":424,
                                  "authority":"selected current native cores, never p14 stale halos"},
    "editRegions":regions,"nativeBeforeEvidence":evidence,
    "request":str(request_path),"requestSha256":sha(request_path),
    "prompt":str(prompt_path),"promptSha256":sha(prompt_path),
    "sourceHelper":str(HELPER),"sourceHelperSha256":sha(HELPER),
    "canonicalManifests": [{"file":str(BASE/t/"selected-patches.json"),
                            "sha256":sha(BASE/t/"selected-patches.json")}
                           for t in ["r12_c08","r12_c09"]],
    "historicalFreeze": {"file":str(BASE/"migration-freeze-20261011.json"),
                         "sha256":sha(BASE/"migration-freeze-20261011.json"),
                         "meaning":"historical captured checkpoint; superseded production hold, kept read only"},
    "operation":"Exact native core crop/paste assembly, exact approved local rail overlay, byte-identical p14 context copy; no art generation or synthetic repair",
    "resamplingApplied":False,"pixelBlendingApplied":False,"colorProcessingApplied":False,
    "sourceArtModified":False,"canonicalSelectionModified":False,"historicalAuditsModified":False,
    "generationSubmitted":False,"formalAccepted":False,"promotedToSelected":False,
    "reviewPlan":["View guide and native before crops.",
                  "After built-in generation, verify opaque exact 1254x1254 and native framing.",
                  "Inspect raw G4/G5 geometry at 100%; right/south context must match original framing.",
                  "Mechanically adopt only approved left/upper edit rectangles into a versioned p14 provisional native candidate, leaving every other pixel exact.",
                  "Render full p14 core seams against selected p13, p24, r11_c08 p44 and r12_c09 p11, including x32768/y46080 cross.",
                  "Have owner independently review all native joins and only then consider canonical p14 selection."]
}
manifest_path = OUT / (STEM + ".coordinates-provenance.json")
write(manifest_path, manifest)
print(json.dumps({"guide":str(guide),"request":str(request_path),"provenance":str(manifest_path),
                  "evidence":[r["file"] for r in evidence],"generationSubmitted":False}))
