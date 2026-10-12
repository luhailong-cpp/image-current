# Explicit native patch guide preparation

Entry point: `prepare_zone_patch.py` in the northwest zone. Use the bundled Python runtime at `C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`.

```text
prepare_zone_patch.py --tile-row 3 --tile-col 4 --subrow 1 --subcol 1 --attempt a01 --left r03_c03_s01_04_a03
```

Targets: `--tile-row` and `--tile-col` are 1..7; `--subrow` and `--subcol` are 1..4. `--attempt` is explicit `aNN` or a longer numeric version. Optional `--left`, `--right`, `--top`, `--bottom` each accept a complete native stem including its attempt. No version or neighbor is automatically selected. Optional `--output-dir` is relative to the zone or an absolute directory inside it; default is `guides/`.

The tool checks each explicit source's global core origin, including cross-tile neighbors, then verifies its measured dimensions, generation hash/unscaled record and recorded native/core coordinates. It resolves the source zone from the shared ownership contract. An exact attempt input record is preferred; an exact unversioned patch-slot coordinate record may corroborate a historical version. If both are absent, the selected source's own hash-verified generation record may supply explicit globalBox and coreBox (the original seed uses this format). It never substitutes another image attempt or infers missing coordinates. Missing coordinate evidence or wrong adjacency fails clearly.

Outputs: versioned `.layout-with-native.png`, matching `.png.derivation.json`, `.input.json` and `.references.json`. With two or more neighbors, a versioned `.native-reference-contact.png` plus derivation record is also written. Existing output files are refused using preflight checks and exclusive file creation. Native files and progress are never written.

There are at most five image inputs, in this order: guide, sole layout, detail style, mail style, neighbor reference. One neighbor uses its original native image directly. Multiple neighbors are packed horizontally at their original 1254-square dimensions with no blank cells, labels or resampling; panel order is left, right, top, bottom, omitting unspecified sides. All source hashes, dimensions and panel coordinates remain in the metadata.

The guide resamples only the locked overview for layout, then pastes exact 230-pixel neighbor overlaps. When native strips overlap at a corner, later direction order wins guide pixels without blending. Both full native originals remain in input 5; corner differences are recorded and remain visually unverified. No low numerical difference grants seam acceptance.

For negative map-edge halo coordinates, overview edge pixels are repeated before layout sampling, avoiding a black frame. Out-of-canvas halo amounts are recorded and never enter the formal core. This is layout-only processing, never final-art generation.

`imageGenReferencedImagePaths` in `.input.json` supplies the ordered paths to attach. Either `.input.json` or `.references.json` can be passed to the existing `workflow.py ingest --refs`; ingest is separate and is not invoked by this tool.

Validation: `prepare_zone_patch_validation/validation.json` records eight passes: all four cross-4K directions, a two-neighbor five-input contact, left/top edge extension, existing-version rejection, and wrong-neighbor rejection. Actual neighbor and contact pixels were compared exactly. The edge guide, cross-left guide and two-neighbor guide were also viewed. No generation or formal game output was created.
