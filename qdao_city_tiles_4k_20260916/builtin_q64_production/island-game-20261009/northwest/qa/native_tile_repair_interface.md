# Native repair of an assembled tile

`apply_native_tile_repair.py` is independent of `assemble_tile.py` and never changes it, native art, a mask, selected manifests or progress. It copies pixels from one explicitly supplied 1254-square AI repair into one verified 4096-square candidate using an explicit 0/255 mask. It never chooses or generates that mask, registers/translates artwork, resizes, feathers, recolors or grants visual acceptance.

## CLI

```text
python apply_native_tile_repair.py
  --base <4096 PNG>
  --base-record <base assembly.json or prior native-repair.json>
  --source <original 1254 PNG inside this zone/native>
  --generation-record <source.png.generation.json>
  --input <source input.json>
  --crop-box X0 Y0 X1 Y1
  --mask <explicit 1254 grayscale L PNG, only 0 and 255>
  --output <new-version 4096 PNG inside this zone, outside native>
```

The coordinates are half-open, local to the base tile, and must define a 1254×1254 crop fully inside it. Relative CLI paths resolve against the current working directory. JSON paths resolve against their containing JSON. A nonempty repair selection is required; a mask covering the whole crop is allowed. Zero mask pixels and every pixel outside the crop preserve the base.

Validation modes write no art or record:

- `--validate-base-only`: requires only base and base-record; recomputes all 16,777,216 pixels' original native provenance.
- `--validate-crop-only`: additionally requires input and crop-box; checks the actual editing crop and its source metadata before AI generation. This mode always requires the **entire crop** to equal the current base, even if a mask argument is supplied.
- `--validate-only`: requires the full repair inputs and mask, but no output; computes and verifies the proposed result only in memory. It returns `editTargetCompatibility`, including ancestor identity, application-base identity, the verified chain, and the mask-aware pixel comparison.

Every output is a fresh PNG plus a sibling `.native-repair.json`. Existing versions are refused. The record includes hashes, the explicit mask and selected count/bounds, the raw source generation/prompt/receipt/input evidence, crop/global coordinates, the exact base record and its root assembly provenance. It may be supplied as the next repair's base-record; recursive verification replays each recorded mask back to the original assembly, with cycle/depth checks.

## Input crop proof

The input JSON declares its actual 1–5 references, including the edit target first. All entries need path and SHA-256 and must match the generation record's reference list in order. Repair names need not match a fixed subcell stem.

```json
{
  "tileId": "r03_c03",
  "tileCropBox": [1670, 2220, 2924, 3474],
  "globalBox": [9862, 10412, 11116, 11666],
  "nativeSize": [1254, 1254],
  "editTarget": {
    "path": "...native-crop.png",
    "sha256": "<crop SHA-256>",
    "derivationRecord": {
      "path": "...native-crop.derivation.json",
      "sha256": "<derivation JSON SHA-256>"
    }
  },
  "inputs": [
    {"path": "...native-crop.png", "sha256": "<crop SHA-256>"},
    {"path": "...layout.png", "sha256": "<SHA-256>"},
    {"path": "...detail.png", "sha256": "<SHA-256>"},
    {"path": "...mail.png", "sha256": "<SHA-256>"}
  ]
}
```

The separate derivation JSON must contain:

```json
{
  "derivedFrom": {
    "path": "...base4096.png",
    "sha256": "<base SHA-256>",
    "assemblyRecord": {
      "path": "...base.assembly.json",
      "sha256": "<base record SHA-256>"
    }
  },
  "cropBox": [1670, 2220, 2924, 3474],
  "operation": "native-coordinate crop",
  "resizing": false,
  "registration": false,
  "feathering": false,
  "colorCorrection": false
}
```

For a later repair, `assemblyRecord` normally identifies the immediately preceding `.native-repair.json`; its field name is retained for compatibility, and the tool follows it to the root assembly. The edit target is always decoded and compared pixel-for-pixel with the **entire crop from its recorded generation-time source**, rather than trusting these declarations. `globalBox` must equal the tile origin plus the crop box; tile r03_c03 has origin [8192,8192].

Independent edits may reuse a crop made from an older base only under a strict ancestor rule: that exact image/hash and record/hash must occur in the current base's explicit parent chain; the ancestor's complete native coverage is revalidated; and the edit target must equal the **entire actual ancestor crop**. A different base with identical pixels but absent from the recorded chain is rejected. Generation/input/derivation history is never rewritten to pretend that the edit used the newer base.

For an application with an explicit mask, compare that edit target with the verified current application-base crop at every coordinate. Every `mask == 255` coordinate must still have exactly the same RGB pixel. A single changed selected pixel is rejected. Differences at `mask == 0` are allowed because those coordinates copy the current base unchanged, including already verified later repairs. This does not allow overlapping edits: a visually similar selected pixel is not sufficient. An all-255 mask therefore still requires whole-crop equality. Crop preflight without an application mask remains strict whole-crop equality.

`repairSource` preserves `cropSourceBase`, `applicationBase`, `ancestorCropReuse` and `verifiedBaseRecordChainToCropSource`. Its `applicationCropComparison` records the comparison mode, crop/selection pixel counts, `differentPixelCount`, `differentSelectedPixelCount` (must be zero), `differentUnselectedPixelCount`, `allDifferencesOutsideSelection`, and a hash of the row-major packed difference bitmap. A pixel counts as different if any RGB channel differs. `cropExactlyMatchesRecordedSource` is always true after validation; the legacy `cropExactlyMatchesSourceAndApplicationBase` and coverage assertion `editTargetExactlyEqualsBaseCrop` are truthfully false when permitted mask-zero differences exist. Separate coverage assertions affirm complete ancestor-crop equality, selected-coordinate equality, and confinement of differences outside the mask.

Recursive revalidation of a later output replays these same gates using that output's recorded explicit mask; it does not fall back to whole-crop equality for a valid nonoverlapping ancestor reuse. Final composition independently checks that every mask-zero pixel is copied from the **current application base**, not the ancestor.

## Validation boundaries

Base validation checks the assembly output hash, coverage assertions, manifest snapshot/hash, source-index archive/hash, source coordinates and all contribution counts, every original raw generation/prompt/receipt/hash, and any two-source native composite mask. Each base pixel must equal its source at its recorded coordinate. No seam optimization is rerun.

Repair validation requires a genuine recorded builtin image_gen.imagegen PNG, measured at 1254 square and explicitly unscaled. Model/quality evidence remains exactly what the source generation record reports. It then checks the edit-target derivation and actual reference list. Final output pixels must equal either the unchanged base or the raw repair at the same crop-local coordinate. The record's mask counts and bounding boxes do not imply that the selected boundary is visually good.

`native_tile_repair_validation.json` records actual candidate-v1 and whole-cylinder-crop checks plus in-memory rejection checks. No repaired 4K image or newly chosen mask was written during that validation. The actual AI repair/mask/output run remains a separate root-controlled step.

`native_tile_repair_mask_aware_validation.json` adds actual candidate-v4 plus upper-beam-a02 validation, single-selected-pixel rejection, nonancestor rejection, strict crop-only rejection, current-base mask-zero preservation, and in-memory recursive replay of a permitted ancestor edit. Its companion `native_tile_repair_v4_upper_beam_validate_only.json` is the real CLI `--validate-only` output. These checks do not write a new 4K image or confer visual acceptance.
