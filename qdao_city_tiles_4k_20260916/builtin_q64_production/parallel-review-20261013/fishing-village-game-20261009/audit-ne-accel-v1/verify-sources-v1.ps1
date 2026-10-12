param()
$ErrorActionPreference='Stop'
$map='D:\work\image\qdao_city_tiles_4k_20260916\builtin_q64_production\fishing-village-game-20261009'
$out='D:\work\image\qdao_city_tiles_4k_20260916\builtin_q64_production\parallel-review-20261013\fishing-village-game-20261009\audit-ne-accel-v1'
function Read-Json([string]$path) { Get-Content -LiteralPath $path -Raw | ConvertFrom-Json }
function Inspect-Source([string]$path,[string]$expected='') {
 $f=Get-Item -LiteralPath $path
 $hash=(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
 $d=$null
 if($f.Extension -eq '.png') {
  $stream=[System.IO.File]::OpenRead($path)
  try { $b=New-Object byte[] 24; [void]$stream.Read($b,0,24) } finally { $stream.Dispose() }
  if($b[0] -ne 137 -or $b[1] -ne 80 -or $b[2] -ne 78 -or $b[3] -ne 71) { throw "Invalid PNG signature $path" }
  $w=[uint32]$b[16]*16777216+[uint32]$b[17]*65536+[uint32]$b[18]*256+[uint32]$b[19]
  $h=[uint32]$b[20]*16777216+[uint32]$b[21]*65536+[uint32]$b[22]*256+[uint32]$b[23]
  $d=@($w,$h)
 }
 [ordered]@{path=$f.FullName;sha256=$hash;expectedSha256=$expected;hashMatches=if($expected){$expected -eq $hash}else{$null};dimensions=$d;bytes=$f.Length;lastWriteTimeUtc=$f.LastWriteTimeUtc.ToString('o')}
}
$activePath=Join-Path $map 'northeast\records\active-candidates.json'
$accelManifestPath=Join-Path $map 'accelerated-jewelry-approach\resume-20261012\candidate-manifest.json'
$active=Read-Json $activePath
$manifest=Read-Json $accelManifestPath
$candidates=@()
foreach($p in $active.tiles.PSObject.Properties) { $q=Inspect-Source $p.Value.path $p.Value.sha256; $q.tile=$p.Name; $q.owner='northeast'; $q.explicitSelection=$true; $q.reviewStatus=$p.Value.reviewStatus; $candidates+=$q }
foreach($s in $manifest.sources) { $q=Inspect-Source $s.file $s.sha256; $q.tile=$s.tile; $q.owner='accelerated-jewelry-approach'; $q.explicitSelection=$true; $q.globalCoreBox=$s.globalCoreBox; $q.regionPasteAt=$s.regionPasteAt; $candidates+=$q }
$partial=@()
$r04Path=Join-Path $map 'northeast\records\r04_c12.working-selection.json'
$r04=Read-Json $r04Path
foreach($p in $r04.PSObject.Properties) { $q=Inspect-Source (Join-Path $map ('northeast\native\'+$p.Value)); $q.patchId=$p.Name; $q.selection=$r04Path; $partial+=$q }
$r06Path=Join-Path $map 'northeast\records\west_sol\r06_c11.selected.json'
$r06=Read-Json $r06Path
foreach($p in $r06.PSObject.Properties) { $q=Inspect-Source $p.Value.path $p.Value.sha256; $q.patchId=$p.Name; $q.selection=$r06Path; $partial+=$q }
foreach($q in $partial) {
 if($q.patchId -match 'r(\d{2})_c(\d{2})_p([1-4])([1-4])') {
  $x=([int]$Matches[2]-1)*4096+([int]$Matches[4]-1)*1024
  $y=([int]$Matches[1]-1)*4096+([int]$Matches[3]-1)*1024
  $q.coreGlobalBox=@($x,$y,($x+1024),($y+1024)); $q.nativeGlobalBox=@(($x-115),($y-115),($x+1139),($y+1139)); $q.nativeCoreBox=@(115,115,1139,1139)
 }
}
$region=Inspect-Source $manifest.regionCandidate.file $manifest.regionCandidate.sha256
$records=@(Inspect-Source $activePath; Inspect-Source $accelManifestPath; Inspect-Source $r04Path; Inspect-Source $r06Path)
$report=[ordered]@{schemaVersion=1;auditedAtUtc=[datetime]::UtcNow.ToString('o');scope='read-only source selection/hash/PNG-header audit; no image visual QA';candidates=$candidates;partialSelectedNatives=$partial;existingSixTileRegion=$region;selectionRecords=$records;formalAcceptanceGranted=$false;generationPerformed=$false;gitOperationsPerformed=$false}
$report|ConvertTo-Json -Depth 9 | Set-Content -LiteralPath (Join-Path $out 'verified-sources-v1.json') -Encoding utf8
[ordered]@{report=(Join-Path $out 'verified-sources-v1.json');candidateCount=$candidates.Count;candidateHashMismatchCount=@($candidates|Where-Object{$_.hashMatches -eq $false}).Count;partialNativeCount=$partial.Count;partialHashMismatchCount=@($partial|Where-Object{$_.hashMatches -eq $false}).Count;allPartial1254=(@($partial|Where-Object{$_.dimensions[0] -ne 1254 -or $_.dimensions[1] -ne 1254}).Count -eq 0);region=$region}|ConvertTo-Json -Depth 5
