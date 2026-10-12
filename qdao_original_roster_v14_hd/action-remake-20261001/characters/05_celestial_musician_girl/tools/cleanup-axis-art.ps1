param([switch]$Apply)
$ErrorActionPreference = 'Stop'
$taskRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$expectedRoot = 'D:\work\image\qdao_original_roster_v14_hd\action-remake-20261001\characters\05_celestial_musician_girl'
if ($taskRoot -ne $expectedRoot) { throw 'Unexpected task root' }
$evidenceRoot = Join-Path $taskRoot 'provenance/foot-axis-20261004'
function Read-Json($relativePath) { Get-Content -LiteralPath (Join-Path $taskRoot $relativePath) -Raw -Encoding utf8 | ConvertFrom-Json }
function Hash-File($path) { (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() }
$closeout = Read-Json 'provenance/foot-axis-20261004/closeout.json'
$promotion = Read-Json 'provenance/foot-axis-20261004/promotion.json'
$browser = Read-Json 'provenance/foot-axis-20261004/browser-check.json'
$validation = Read-Json 'provenance/final-validation.json'
$selection = @(Read-Json 'final-selection.json')
if (-not $browser.passed -or $closeout.finalSelectionSha256 -ne (Hash-File (Join-Path $taskRoot 'final-selection.json')) -or $browser.finalSelectionSha256 -ne $closeout.finalSelectionSha256) { throw 'Current final references must be verified first' }
if ($promotion.status -ne 'complete' -or $promotion.finalSelectionSha256 -ne $closeout.finalSelectionSha256 -or $closeout.status -ne 'offline_artwork_and_browser_complete_client_pending' -or $closeout.mandatoryCorrectionsRemaining.Count -ne 0) { throw 'Promotion and closeout must be complete before cleanup' }
if ($selection.Count -ne 196 -or $validation.finalFrames -ne 196 -or -not $validation.activePreviewReferencesComplete) { throw 'Final audit incomplete' }
$retained = @{}
foreach ($frame in $selection) {
    $absolute = (Resolve-Path -LiteralPath (Join-Path $taskRoot $frame.file)).Path
    if ((Hash-File $absolute) -ne $frame.sha256) { throw "Final SHA mismatch: $absolute" }
    $checkedFrame = @($validation.checks | Where-Object { $_.file -eq $frame.file -and $_.sha256 -eq $frame.sha256 -and $_.pass })
    if ($checkedFrame.Count -ne 1) { throw "Latest final audit does not cover this frame: $absolute" }
    $retained[$absolute] = $frame.sha256
}
$proofPath = (Resolve-Path -LiteralPath (Join-Path $taskRoot 'preview/delivery-proof.png')).Path
$retained[$proofPath] = Hash-File $proofPath
$extensions = @('.png','.jpg','.jpeg','.webp','.gif')
$records = @()
foreach ($item in (Get-ChildItem -LiteralPath $taskRoot -Recurse -File)) {
    if ($item.Extension.ToLowerInvariant() -notin $extensions) { continue }
    $absolute = (Resolve-Path -LiteralPath $item.FullName).Path
    if ($retained.ContainsKey($absolute)) { continue }
    if (-not $absolute.StartsWith($taskRoot+'\',[StringComparison]::OrdinalIgnoreCase) -or $absolute.StartsWith((Join-Path $taskRoot 'final')+'\',[StringComparison]::OrdinalIgnoreCase)) { throw "Unsafe cleanup target: $absolute" }
    $records += [ordered]@{ file=$absolute.Substring($taskRoot.Length+1).Replace('\','/'); absolutePath=$absolute; sha256=(Hash-File $absolute); bytes=$item.Length }
}
$receiptPath = Join-Path $evidenceRoot 'cleanup.json'
if ((Test-Path -LiteralPath $receiptPath) -and ((Get-Content -LiteralPath $receiptPath -Raw -Encoding utf8 | ConvertFrom-Json).status -eq 'complete')) { throw 'Cleanup already completed' }
$receipt = [ordered]@{ status='planned'; inventoriedAt=(Get-Date).ToUniversalTime().ToString('o'); scopeRoot=$taskRoot; finalSelectionSha256=$closeout.finalSelectionSha256; finalReferencesVerified=$true; files=$records; plannedImageRemovals=$records.Count; retainedImages=197; imageBackupsCreated=$false; textProvenanceRetained=$true }
$receipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $receiptPath -Encoding utf8
if (-not $Apply) { [ordered]@{ planned=$records.Count; retained=197 } | ConvertTo-Json; return }
foreach ($record in $records) {
    if ((Hash-File $record.absolutePath) -ne $record.sha256) { throw 'Candidate changed after inventory' }
    Remove-Item -LiteralPath $record.absolutePath
}
foreach ($path in $retained.Keys) { if ((Hash-File $path) -ne $retained[$path]) { throw 'Retained image changed' } }
$remaining = @(Get-ChildItem -LiteralPath $taskRoot -Recurse -File | Where-Object { $_.Extension.ToLowerInvariant() -in $extensions })
if ($remaining.Count -ne 197) { throw 'Unexpected retained image count' }
$receipt.status='complete'; $receipt.completedAt=(Get-Date).ToUniversalTime().ToString('o')
$receipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $receiptPath -Encoding utf8
[ordered]@{ removed=$records.Count; retained=$remaining.Count; finalImages=196; textProvenanceRetained=$true } | ConvertTo-Json
