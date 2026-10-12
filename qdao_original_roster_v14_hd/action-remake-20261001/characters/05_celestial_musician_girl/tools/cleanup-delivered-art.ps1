$ErrorActionPreference = 'Stop'
$taskRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$expectedRoot = 'D:\work\image\qdao_original_roster_v14_hd\action-remake-20261001\characters\05_celestial_musician_girl'
if ($taskRoot -ne $expectedRoot) { throw 'Unexpected cleanup workspace' }
$finalRoot = (Resolve-Path -LiteralPath (Join-Path $taskRoot 'final')).Path
$finalCheck = Get-Content -Raw -LiteralPath (Join-Path $taskRoot 'provenance/final-validation.json') | ConvertFrom-Json
$taskStatus = Get-Content -Raw -LiteralPath (Join-Path $taskRoot 'STATUS.json') | ConvertFrom-Json
if ($finalCheck.finalFrames -ne 196 -or -not $finalCheck.activePreviewReferencesComplete -or $taskStatus.finalVisualPassed -ne 196) { throw 'Delivery must pass before cleanup' }
$previewRoot = (Resolve-Path -LiteralPath (Join-Path $taskRoot 'preview')).Path
$keepPreview = @('index.html','manifest.json','timing-grounding-final.html','timing-grounding-final-data.json','delivery-proof.jpg')
$imageExtensions = @('.png','.jpg','.jpeg','.webp','.gif')
$removeFiles = @(Get-ChildItem -LiteralPath $taskRoot -File -Recurse | Where-Object {
    ($_.Extension.ToLowerInvariant() -in $imageExtensions -and -not $_.FullName.StartsWith($finalRoot + '\', [StringComparison]::OrdinalIgnoreCase) -and $_.Name -ne 'delivery-proof.jpg') -or
    ($_.DirectoryName -eq $previewRoot -and $_.Name -notin $keepPreview)
})
$removalRecords = @()
foreach ($item in $removeFiles) {
    $checked = (Resolve-Path -LiteralPath $item.FullName).Path
    if (-not $checked.StartsWith($taskRoot + '\', [StringComparison]::OrdinalIgnoreCase) -or $checked.StartsWith($finalRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw "Unsafe cleanup target: $checked" }
    $removalRecords += [ordered]@{ file=$checked.Substring($taskRoot.Length+1).Replace('\','/'); sha256=(Get-FileHash -LiteralPath $checked -Algorithm SHA256).Hash.ToLowerInvariant(); bytes=$item.Length }
}
# Save text evidence first. Delete only verified individual files; no recursive directory removal.
$receipt = [ordered]@{ status='planned_after_formal_verification'; dateUtc=(Get-Date).ToUniversalTime().ToString('o'); policy='Only final game PNGs and delivery support files retained; text provenance preserved'; workspace=$taskRoot; removedFiles=$removalRecords }
$receiptPath = Join-Path $taskRoot 'provenance/cleanup-final-delivery.json'
$receipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $receiptPath -Encoding utf8
foreach ($item in $removeFiles) { Remove-Item -LiteralPath $item.FullName -Force }
foreach ($pair in @(@('candidate-selection.json','native-selection-at-export.json'),@('selected-files.json','native-selected-files-at-export.json'),@('registered-selection.json','registered-selection-at-export.json'))) {
    $sourceFile = Join-Path $taskRoot $pair[0]
    $destFile = Join-Path (Join-Path $taskRoot 'provenance') $pair[1]
    if (Test-Path -LiteralPath $sourceFile) {
        if (Test-Path -LiteralPath $destFile) { throw "Archive metadata destination already exists: $destFile" }
        Move-Item -LiteralPath $sourceFile -Destination $destFile
    }
}
$receipt.status = 'completed'
$receipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $receiptPath -Encoding utf8
[ordered]@{ removedFiles=$removeFiles.Count; formalPngs=(Get-ChildItem -LiteralPath $finalRoot -Recurse -File -Filter '*.png').Count; textProvenanceRetained=$true } | ConvertTo-Json
