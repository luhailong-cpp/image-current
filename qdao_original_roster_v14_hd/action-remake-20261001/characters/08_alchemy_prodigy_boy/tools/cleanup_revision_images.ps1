param([switch]$PlanOnly)
$ErrorActionPreference = 'Stop'
$taskRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$expectedRoot = 'D:\work\image\qdao_original_roster_v14_hd\action-remake-20261001\characters\08_alchemy_prodigy_boy'
if ($taskRoot -ne $expectedRoot) { throw 'Unexpected cleanup root' }
$scopeNames = @('generation/grounding-20261003', 'generation/bamboo-reference-20261003', 'provenance/grounding-20261003', 'provenance/bamboo-reference-20261003')
$scopes = @($scopeNames | ForEach-Object { [IO.Path]::GetFullPath((Join-Path $taskRoot $_)) })
$recordDir = Join-Path $taskRoot 'provenance/bamboo-reference-20261003'
$manifest = Get-Content -LiteralPath (Join-Path $taskRoot 'manifest.json') -Raw | ConvertFrom-Json
if ($manifest.frames.Count -ne 196) { throw 'Runtime incomplete' }
if ($manifest.groundingRevision.replacedFrames -ne 34 -or $manifest.deliveryStatus -ne 'grounding_revision_exported_and_previewed') { throw 'Final revision not closed; do not delete in-progress sources' }
foreach ($frame in $manifest.frames) {
    $runtimePath = [IO.Path]::GetFullPath((Join-Path $taskRoot $frame.file))
    if (-not $runtimePath.StartsWith((Join-Path $taskRoot 'runtime\'), [StringComparison]::OrdinalIgnoreCase)) { throw 'Runtime path escaped scope' }
    if ((Get-FileHash -LiteralPath $runtimePath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $frame.sha256) { throw 'Runtime hash mismatch' }
    $sourceRecord = Join-Path $taskRoot $frame.derivedFrom.generationRecord
    if ((Get-FileHash -LiteralPath $sourceRecord -Algorithm SHA256).Hash.ToLowerInvariant() -ne $frame.derivedFrom.generationRecordSha256) { throw 'Source record hash mismatch' }
}
$targets = @()
foreach ($scope in $scopes) {
    if (-not $scope.StartsWith($taskRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Scope escaped root' }
    foreach ($file in Get-ChildItem -LiteralPath $scope -File -Recurse -Filter '*.png') {
        $resolved = (Resolve-Path -LiteralPath $file.FullName).Path
        if (-not $resolved.StartsWith($scope + '\', [StringComparison]::OrdinalIgnoreCase) -or [IO.Path]::GetExtension($resolved) -ne '.png') { throw 'Target escaped PNG scope' }
        $targets += [pscustomobject]@{ path=$resolved.Substring($taskRoot.Length+1).Replace('\','/'); absolutePath=$resolved; bytes=$file.Length; sha256=(Get-FileHash -LiteralPath $resolved -Algorithm SHA256).Hash.ToLowerInvariant() }
    }
}
$textFiles = @(Get-ChildItem -LiteralPath (Join-Path $taskRoot 'generation'), (Join-Path $taskRoot 'provenance') -Recurse -File | Where-Object { $_.Extension -in @('.json','.txt','.md') -and $_.Name -notlike 'cleanup-*' })
$textHashes = @{}
foreach ($file in $textFiles) { $textHashes[$file.FullName] = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash }
$plan = [ordered]@{ createdAt=[DateTime]::UtcNow.ToString('o'); root=$taskRoot; allowedScopes=$scopeNames; authorization='User explicitly requested rejected-image cleanup and confirmed retain only final game resources plus text provenance in AGENTS.md'; runtimeManifestSha256=(Get-FileHash -LiteralPath (Join-Path $taskRoot 'manifest.json')).Hash.ToLowerInvariant(); files=$targets; plannedImages=$targets.Count; plannedBytes=($targets | Measure-Object bytes -Sum).Sum; preservedTextFiles=$textFiles.Count }
$plan | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $recordDir 'cleanup-plan.json') -Encoding utf8
foreach ($item in $targets) {
    if ((Get-Item -LiteralPath $item.absolutePath).Length -ne $item.bytes -or (Get-FileHash -LiteralPath $item.absolutePath).Hash.ToLowerInvariant() -ne $item.sha256) { throw 'Cleanup target changed after planning' }
}
if ($PlanOnly) { [pscustomobject]$plan | Select-Object plannedImages, plannedBytes, preservedTextFiles | ConvertTo-Json -Compress; exit 0 }
$removed = @()
try {
    foreach ($item in $targets) { Remove-Item -LiteralPath $item.absolutePath; $removed += $item.path }
} catch {
    [ordered]@{ status='failed'; failedAt=[DateTime]::UtcNow.ToString('o'); deletedImages=$removed.Count; deletedPaths=$removed; reason=$_.Exception.Message } | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $recordDir 'cleanup-result.json') -Encoding utf8
    throw
}
foreach ($file in $textFiles) { if ((Get-FileHash -LiteralPath $file.FullName).Hash -ne $textHashes[$file.FullName]) { throw 'Text evidence changed' } }
foreach ($frame in $manifest.frames) { if ((Get-FileHash -LiteralPath (Join-Path $taskRoot $frame.file)).Hash.ToLowerInvariant() -ne $frame.sha256) { throw 'Runtime changed' } }
$result = [ordered]@{ status='completed'; completedAt=[DateTime]::UtcNow.ToString('o'); deletedImages=$targets.Count; deletedBytes=$plan.plannedBytes; preservedRuntimeImages=196; preservedContactSheets=14; preservedTextFiles=$textFiles.Count; plan='provenance/bamboo-reference-20261003/cleanup-plan.json' }
$result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $recordDir 'cleanup-result.json') -Encoding utf8
$result | ConvertTo-Json -Compress
