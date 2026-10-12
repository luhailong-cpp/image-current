# r12_c09 — coastal retaining wall and dock corner

Current candidate: `candidate/r12_c09-internal-ready-4096.png`.

Status: 16 / 16 native positions, 17 native generation results, one rejected p23-v1 replaced by p23-v2. Internal review is ready; formal cross-tile acceptance remains pending. The source selection is `selected-patches.json`.

The 4096-square candidate consists of sixteen unscaled 1024-square core crops from 1254-square native images (115-pixel halo). The low-frequency RGB correction is fully recorded in `processed/colorpass`; the actual maximum channel change is 16. No geometry shift, source resampling, image blur or pixel blending was applied. `candidate/processed-verification.json` verifies exact reconstruction and single coverage.

All 24 internal native seam strips and 9 four-patch crossings were visually reviewed before and after color correction. The north boundary against r11_c09 was checked again after color selection; complete strips and hashes are under `qa/final-north-*`. Formal acceptance of all exterior edges awaits available neighbors and the zone review.

Every AI output uses the built-in image tool. Exact prompts, submitted references and receipts are retained as `p??-v?.prompt.txt`, `.request.json` and `.receipt.json`, with source records in `native`. Actual and submitted model / quality values are null because the host does not expose selectors or return them. New p41–p44 requests use the contract's current `mail-daoist-style.jpg`; 12 older selected outputs preserve their missing historical style PNG reference hashes without rewriting history.

No final map completion or gameplay capacity claim is made.
