# Functional proof that the G1 carryover really preserves the operator's evidence.
# It does NOT retype the fix: it EXTRACTS steps 3c and 5b out of the real
# apply_update.ps1 and runs them against a scratch install, with the delete
# (step 4) and move-in (step 5) simulated exactly as the updater does them.
param([string]$Updater = "C:\Development\Tlamatini\apply_update.ps1")

$ErrorActionPreference = "Stop"

# ── scratch "install" ───────────────────────────────────────────────────────
$InstallDir = Join-Path $env:TEMP ("tlm_g1_proof_" + [guid]::NewGuid().ToString("N").Substring(0, 8))
$staging = Join-Path $InstallDir "_staged_new_build"
New-Item -ItemType Directory -Path (Join-Path $InstallDir "security\security_logs\asset_tests") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $InstallDir "Temp") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $InstallDir "DB") -Force | Out-Null

# the operator's evidence + the app code that MUST be replaced
Set-Content (Join-Path $InstallDir "security\security_logs\alerts.log")  "CRITICAL 203.0.113.9 brute force" -Encoding UTF8
Set-Content (Join-Path $InstallDir "security\security_logs\monitor.log") "INFO sweep complete"               -Encoding UTF8
Set-Content (Join-Path $InstallDir "security\security_logs\asset_tests\results.json") '{"passed":41}'        -Encoding UTF8
Set-Content (Join-Path $InstallDir "security\tlamatini_defender.ps1")    "OLD DEFENDER v2.1"                 -Encoding UTF8

# the incoming release: new security/ WITHOUT security_logs (build.py ignores it)
New-Item -ItemType Directory -Path (Join-Path $staging "security") -Force | Out-Null
Set-Content (Join-Path $staging "security\tlamatini_defender.ps1") "NEW DEFENDER v2.2 (fixed)" -Encoding UTF8

# ── stubs the extracted blocks depend on ───────────────────────────────────
function Write-Log { param([string]$Message, [string]$Color = "Gray") Write-Host "    [updater] $Message" }
function Invoke-WithRetry { param([scriptblock]$Action) & $Action }
$Preserve = @('config.json', 'DB', 'Temp', 'Templates')
function Test-Preserved { param([string]$Name) foreach ($p in $Preserve) { if ($Name -ieq $p) { return $true } } return $false }

# ── extract the REAL steps 3c and 5b from the shipped updater ──────────────
$src = Get-Content $Updater -Raw
$m3c = [regex]::Match($src, '(?s)#\s*3c\)(.*?)#\s*4\)')
$m5b = [regex]::Match($src, '(?s)#\s*5b\)(.*?)#\s*6\)')
if (-not $m3c.Success) { throw "could not extract step 3c from $Updater" }
if (-not $m5b.Success) { throw "could not extract step 5b from $Updater" }
# The regex consumed the leading '#' of the first comment line, so put it back
# or PowerShell tries to RUN that prose as a command.
$step3c = '# ' + $m3c.Groups[1].Value
$step5b = '# ' + $m5b.Groups[1].Value
Write-Host "  extracted step 3c ($($step3c.Length) chars) and step 5b ($($step5b.Length) chars) from the real updater" -ForegroundColor DarkGray

Write-Host ""
Write-Host "  BEFORE:" -ForegroundColor Cyan
Get-ChildItem (Join-Path $InstallDir "security") -Recurse -File | ForEach-Object { "    " + $_.FullName.Replace($InstallDir, "<install>") }

# ── run step 3c (stash) ────────────────────────────────────────────────────
Write-Host ""
Write-Host "  -- step 3c (stash) --" -ForegroundColor Yellow
Invoke-Expression $step3c

# ── simulate step 4: delete everything not preserved ───────────────────────
Write-Host ""
Write-Host "  -- step 4 (delete old install) --" -ForegroundColor Yellow
Get-ChildItem -LiteralPath $InstallDir -Force | ForEach-Object {
    if ($_.Name -eq "_staged_new_build") { return }
    if (Test-Preserved $_.Name) { Write-Host "    keep    $($_.Name)"; return }
    Write-Host "    remove  $($_.Name)"
    Remove-Item -LiteralPath $_.FullName -Recurse -Force
}

# ── simulate step 5: move the new build in ─────────────────────────────────
Write-Host ""
Write-Host "  -- step 5 (install new version) --" -ForegroundColor Yellow
Get-ChildItem -LiteralPath $staging -Force | ForEach-Object {
    if (Test-Preserved $_.Name) { return }
    Write-Host "    install $($_.Name)"
    Move-Item -LiteralPath $_.FullName -Destination (Join-Path $InstallDir $_.Name) -Force
}

# ── run step 5b (restore) ──────────────────────────────────────────────────
Write-Host ""
Write-Host "  -- step 5b (restore) --" -ForegroundColor Yellow
Invoke-Expression $step5b

# ── verdict ────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "  AFTER:" -ForegroundColor Cyan
Get-ChildItem (Join-Path $InstallDir "security") -Recurse -File | ForEach-Object { "    " + $_.FullName.Replace($InstallDir, "<install>") }

$fail = 0
function Check($label, $cond) {
    if ($cond) { Write-Host "  PASS  $label" -ForegroundColor Green }
    else { Write-Host "  FAIL  $label" -ForegroundColor Red; $script:fail++ }
}

Write-Host ""
$alerts = Join-Path $InstallDir "security\security_logs\alerts.log"
$monitor = Join-Path $InstallDir "security\security_logs\monitor.log"
$nested = Join-Path $InstallDir "security\security_logs\asset_tests\results.json"
$defender = Join-Path $InstallDir "security\tlamatini_defender.ps1"

Check "alerts.log survived the update"            (Test-Path $alerts)
Check "alerts.log CONTENT is intact"              ((Test-Path $alerts) -and ((Get-Content $alerts -Raw).Trim() -eq "CRITICAL 203.0.113.9 brute force"))
Check "monitor.log survived"                      (Test-Path $monitor)
Check "nested asset_tests/results.json survived"  (Test-Path $nested)
Check "the DEFENDER SCRIPT was REPLACED (v2.2)"   ((Test-Path $defender) -and ((Get-Content $defender -Raw).Trim() -eq "NEW DEFENDER v2.2 (fixed)"))
Check "no leftover carryover in Temp"             (-not (Test-Path (Join-Path $InstallDir "Temp\_security_logs_carryover")))

Remove-Item -LiteralPath $InstallDir -Recurse -Force -ErrorAction SilentlyContinue

Write-Host ""
if ($fail -eq 0) {
    Write-Host "  ================================================" -ForegroundColor Green
    Write-Host "   PROVEN: evidence survives, defender is replaced" -ForegroundColor Green
    Write-Host "  ================================================" -ForegroundColor Green
    exit 0
}
Write-Host "  $fail CHECK(S) FAILED" -ForegroundColor Red
exit 1
