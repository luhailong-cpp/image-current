# Independent repaired-core review

Result: pass for repaired row2-column2 core and its eight inspected joins only. No entire-tile acceptance is asserted.

All native images and evidence crops listed below were actually viewed at original pixels. The eight proposal crops exactly match current candidate v05; the candidate ROI [1024,1024,2048,2048] exactly matches source ROI [115,115,1139,1139]. Boxes use exclusive right and bottom coordinates.

## Eight crop verdicts

| Crop | Candidate box | Verdict | Observation |
|---|---|---|---|
| v-r2-c1 | [896, 1024, 1152, 2048] | Pass in scope | Across candidate x=1024, all diagonal grout crossings remain continuous in position, width, and color. Mosaic and stone shading do not show a rectangular material cut. |
| v-r2-c2 | [1920, 1024, 2176, 2048] | Pass in scope | Across candidate x=2048, diagonal grout and gold junctions remain continuous. The pale mosaic material carries across the seam with no exposed stub or fragment. |
| h-r1-c2 | [1024, 896, 2048, 1152] | Pass in scope | Across candidate y=1024, diagonal grout, mosaic tile fields, and both vertical corridor borders carry through without a visible cut. No separate gold fragment is visible. |
| h-r2-c2 | [1024, 1920, 2048, 2176] | Pass in scope | Across candidate y=2048, the diagonal linking gold junctions near (1069,1999) and (1146,2079) remains continuous; the vertical corridor is also continuous. Both gold nodes are attached compact caps, not detached fragments. |
| j-r1-c1 | [864, 864, 1184, 1184] | Pass in scope | The crossing of candidate x=1024 and y=1024 has continuous diagonal grout and material. The gold nodes away from the seam center are attached; crop-border terminations are not treated as defects. |
| j-r2-c1 | [864, 1888, 1184, 2208] | Pass in scope | The crossing of candidate x=1024 and y=2048 has no visible four-corner splice. Gold caps near (1069,1999) and (1146,2079) are attached to continuous diagonal grout, with no isolated orphan. |
| j-r1-c2 | [1888, 864, 2208, 1184] | Pass in scope | The crossing of candidate x=2048 and y=1024 has continuous pale stone and grout. The gold node near (2158,1028) connects through to the corridor border near x=2181. |
| j-r2-c2 | [1888, 1888, 2208, 2208] | Pass in scope | The crossing of candidate x=2048 and y=2048 has continuous mosaic material and diagonal grout. The lower-right node near (2172,2150) connects to the corridor border near x=2181; no cut or detached point is visible. |

## Small gold junction diagnosis

Repaired-core gold cap: source approximately (160,1090), candidate approximately (1069,1999). Full1254 source and `repaired-core-gold-node-native-140x130.png` show an attached junction cap, with no separate gold fragment or concrete broken grout.

Old v-r3-c1 concern: candidate (1146,2079), source approximately (237,146). Both narrow baseline images were actually viewed. Their right boundary is x=1152, only 6 pixels beyond the concern coordinate; the outgoing arms are cropped there. Raw native crop [896,2048,1216,2304] in `old-gold-point-current-candidate-native-320x256.png`, together with full1254 `s03_02_resume01.png` and `old-gold-point-source-native-124x124.png`, shows an attached compact cap and continuous outgoing grout. The previous reject claim is not supported by this wider context. No concrete cut spur or detached orphan is visible at that coordinate.

The remaining 4096 candidate and other tile edges were not reviewed in this task. No candidate, selections, or progress files were changed. See `independent-review.json` for absolute evidence paths and individual records.
