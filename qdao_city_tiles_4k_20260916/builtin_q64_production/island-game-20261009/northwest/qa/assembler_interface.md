# Native tile assembler interface

`assemble_tile.py --manifest <explicit-manifest.json> --output <candidate.png>`

`--manifest` is resolved against the process working directory. Image and generation-record paths inside it are absolute or relative to the manifest's directory. `--output` is absolute or relative to the northwest zone. All generated files must remain inside this zone; the tool refuses to write candidate images into `native/`.

Manifest fields: `schemaVersion: 1`, `tileId: "r03_c03"`, `nativePixels: 1254`, `corePixels: 1024`, `haloPixels: 115`, and `patchMatrix`, exactly four rows of four explicit objects. Every cell requires `path` and exactly one of `generationRecord` (raw input) or `nativeCompositeRecord` (verified mechanical composition); `sha256` is an optional pinned input-file hash. Both record fields take explicit JSON paths. There is no globbing, version inference, latest-file selection, missing-cell fill or guide-image fallback. Raw native filenames must match the tile and cell, for example row 1/column 1 uses `r03_c03_s01_01_aNN.png`.

Each raw source must be an unscaled 1254-square RGB/opaque-RGBA PNG inside this zone's `native/` directory. The recorded source hash, native dimensions, built-in route, unscaled flags and prompt hash are checked; prompt and receipt files must exist. Receipt JSON must confirm the same built-in tool/route; its submitted prompt path is also checked when present. Actual PNG format is measured. A missing source or invalid record fails before any candidate image is written. This gate is shared by standalone raw inputs and both leaves of a composite.

The `nativeCompositeRecord` route permits exactly two original raw sources at identical local/global coordinates, selected by a 1254-square grayscale L PNG mask containing only 0 and 255. Both values must occur. The candidate must remain inside the zone and outside `native/`; it is never represented as a new AI generation. Its record must explicitly declare schema 1, `isAiGeneration: false`, `rawNative: false`, and false registration, resizing, feathering, colorCorrection and pixelSynthesis flags. The record pins the candidate, mask, both originals and both generation JSON hashes. Both original filenames must match the same manifest cell. Each exact-attempt `guides/<raw-stem>.input.json` must exist and declare the calculated global native/core boxes; no neighboring or latest attempt is substituted. The record's `coordinateSystem.sameGlobalNativeBox` and `nativeSize` must agree. The assembler then compares every candidate RGB pixel with the mask-selected raw source at the same x/y. A nested composite, third source, mismatched frame, nonbinary mask, changed pixel or conflicting raw/composite entry fails.

For a manifest saved directly in the zone, the existing row 3/column 1 composite can be declared as follows (this is a cell example, not an approved 16-cell selection):

```json
{
  "path": "qa/s03_01_native_composite_a01_base_a04_beam/candidate.png",
  "nativeCompositeRecord": "qa/s03_01_native_composite_a01_base_a04_beam/native_composite_record.json",
  "sha256": "1d9b57fee7f27ffe56c58b8f4f92b419fd1a81f8970a12816a54b26ecebbfb62"
}
```

Assembly uses minimum-error hard boundaries through 230-pixel overlaps: four 4326×1254 rows, then one 4326×4326 padded tile, then crop `[115,115,4211,4211)` to 4096×4096. No registration, final-art scaling, feathering, color correction or generated pixels are used. Every padded and final pixel is compared with its recorded source coordinate.

Outputs are the requested candidate PNG, a sibling `.assembly.json`, and `qa/assembly_<output-stem>/`. QA contains 12 final left/right seam segments, 12 final top/bottom seam segments, nine 480-square intersections, a clearly named 1024-pixel preview, an index with all crop boxes/hashes, and compressed NumPy source-index planes. Each plane stores one source ID per pixel; the assembly record supplies exact source-coordinate rules, contributions, bounding boxes and every seam path. The preview alone is downsampled and is forbidden as game art.

For composite cells, the assembly record includes the verified nested original sources, generation/prompt/receipt/coordinate-input hashes, original-native contribution counts and bounds in both padded and final coordinates. The NumPy archive also preserves `composite_source_NN_native_mask` arrays. An exact original-source position is determined by the 16-cell ownership plane plus that cell's native-coordinate mask sample; bounding boxes alone never imply ownership. An original repair source may contribute zero pixels if a later seam excludes it, and this is recorded as zero with null bounds. Existing candidate, assembly-record or QA-directory versions cause failure rather than overwrite; new files use exclusive creation.

All results remain candidates. Full native coverage and low numerical seam error do not grant visual or external-edge acceptance. The assembler never changes `progress.json`, input images, generation records or another zone.

Implementation-stage validation is recorded in `assembler_geometry_validation.json`: actual first-column and bottom-row dimensions and seven distinct native sources were measured; one-dimensional coverage and the 4096 crop were checked. No 16-input manifest was selected and no 4K candidate was assembled during that validation. The explicit 16-input manifest must come from the root before assembly.

Composite support validation is recorded in `assembler_composite_validation/validation.json`: 22 checks cover the actual 1,535,171-pixel a01 base plus 37,345-pixel a04 repair, the same seven existing raw inputs, malformed/reclassified inputs, wrong hashes/global coordinates, a third/recursive source, an in-memory changed pixel, a nonbinary mask, prompt/receipt failures, nested contribution positions before/after cropping, and a repair entirely removed by a later seam. Fault injection never edits the raw files. No full assembly or new art file was made by these checks. `s03_02a03_beam_check/visual_review.json` is a separate local beam-geometry review, not a formal tile acceptance.
