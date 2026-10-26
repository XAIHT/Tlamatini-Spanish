# Tlamatini Auto-Updater
# =====================================================================
# Runs OUTSIDE the install directory (a copy is placed under
# %LOCALAPPDATA%\Tlamatini\updater by self_update.py) so it can safely
# replace the whole install — including python\, jre\, git\ and
# Tlamatini-Spanish.exe — without locking the files it is overwriting.
#
# Sequence:
#   1. Validate install/staging boundaries and every staged file's receipt.
#   2. Close the running Tlamatini (and its child processes).
#   3. Verify a WAL-aware database backup, then rename agents -> agents_backup.
#   4. Delete the old install EXCEPT the preserved user-data set.
#   5. Move the new build in EXCEPT the preserved set (so the user's
#      config.json / DB / etc. are never overwritten).
#   6. Relaunch the new Tlamatini.
#
# It is launched by agent/self_update.py — do not run it by hand.
# =====================================================================

param(
    [Parameter(Mandatory = $true)][string]$InstallDir,
    [Parameter(Mandatory = $true)][string]$StagingDir,
    [Parameter(Mandatory = $true)][int]$ParentPid,
    [string]$RelaunchExe = "",
    [string]$LogPath = ""
)

$ErrorActionPreference = "Stop"
try { $Host.UI.RawUI.WindowTitle = "Actualizador de Tlamatini-Spanish" } catch {}

# Top-level names in the install root that must NEVER be deleted or
# overwritten. 'agents' is intentionally NOT here: it is renamed to
# 'agents_backup' (step 3) and then replaced by the new version (step 5).
# Uninstaller.exe is built separately and is NOT carried inside pkg.zip, so the
# staged build never contains it. Without preserving it, every self-update would
# delete the uninstaller already on disk. Keep the existing one.
#
# The comment sits ABOVE the array on purpose. agent/test_preserved_user_state.py
# parses this block with a quoted-string regex, so an apostrophe INSIDE it - the
# old comment read "the user's uninstaller" - opened a phantom string that ate
# the 'Uninstaller.exe' entry, and the guard reported it missing from a file that
# was perfectly correct. Keep apostrophes out of this block.
$Preserve = @(
    'config.json', 'external_mcps.json', 'contacts.json', 'DB', 'application', 'applications', 'content_generated',
    'Temp', 'context_files', 'doc_generated', 'documentation', 'Templates',
    'Uninstaller.exe'
)

function Write-Log {
    param([string]$Message, [string]$Color = "Gray")
    $line = "[{0}] {1}" -f (Get-Date -Format "HH:mm:ss"), $Message
    try { Write-Host $line -ForegroundColor $Color } catch { Write-Host $line }
    if ($LogPath) { try { Add-Content -Path $LogPath -Value $line -Encoding UTF8 } catch {} }
}

function Invoke-WithRetry {
    # Windows can hold file handles for a moment after a process dies, so
    # delete/rename/move operations are retried instead of failing outright.
    param([scriptblock]$Action, [int]$Attempts = 15, [int]$DelayMs = 600)
    for ($i = 1; $i -le $Attempts; $i++) {
        try { & $Action; return }
        catch {
            if ($i -eq $Attempts) { throw }
            Start-Sleep -Milliseconds $DelayMs
        }
    }
}

function Test-Preserved {
    param([string]$Name)
    foreach ($p in $Preserve) { if ($Name -ieq $p) { return $true } }
    return $false
}

function Assert-NoReparseAncestors {
    param([string]$Path)
    $cursor = [IO.Path]::GetFullPath($Path)
    while ($cursor) {
        if (Test-Path -LiteralPath $cursor) {
            $item = Get-Item -LiteralPath $cursor -Force
            if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
                throw "El path del actualizador pasa por un reparse point: '$cursor'. Se cancela."
            }
        }
        $cursor = [IO.Path]::GetDirectoryName($cursor)
    }
}

Write-Host ""
Write-Host "  ==================================================" -ForegroundColor Cyan
Write-Host "         TLAMATINI-SPANISH  --  APLICANDO EL UPDATE" -ForegroundColor Cyan
Write-Host "  ==================================================" -ForegroundColor Cyan
Write-Host ""
Write-Log "Carpeta destino : $InstallDir"
Write-Log "Carpeta staging : $StagingDir"
Write-Log "PID padre   : $ParentPid"
Write-Host ""

try {
    # 1) Validate the staged new version BEFORE touching anything.
    $InstallDir = [IO.Path]::GetFullPath($InstallDir).TrimEnd('\', '/')
    $StagingDir = [IO.Path]::GetFullPath($StagingDir).TrimEnd('\', '/')
    $updateRoot = Join-Path $InstallDir "Temp\_update"
    $expectedStaging = Join-Path $updateRoot "staging"
    if ($StagingDir -ine $expectedStaging -or
        $InstallDir -ieq [IO.Path]::GetPathRoot($InstallDir).TrimEnd('\', '/') -or
        $InstallDir -ieq $env:USERPROFILE -or $InstallDir -ieq $env:WINDIR) {
        throw "Frontera insegura entre la carpeta destino y staging. Staging debe estar exactamente en InstallDir\Temp\_update\staging."
    }
    Assert-NoReparseAncestors $InstallDir
    Assert-NoReparseAncestors $StagingDir
    if (-not (Test-Path -LiteralPath (Join-Path $InstallDir "Tlamatini-Spanish.exe") -PathType Leaf)) {
        throw "La carpeta destino no tiene el Tlamatini-Spanish.exe existente. Se cancela."
    }
    if ($ParentPid -le 0 -or $ParentPid -eq $PID) { throw "El PID de Tlamatini-Spanish no es correcto." }
    $newExe = Join-Path $StagingDir "Tlamatini-Spanish.exe"
    if (-not (Test-Path -LiteralPath $newExe)) {
        throw "El paquete del update no sirve -- falta Tlamatini-Spanish.exe en '$newExe'. Se cancela; todo sigue igual."
    }
    if (-not (Test-Path -LiteralPath $InstallDir)) {
        throw "No existe la carpeta destino '$InstallDir'. Se cancela."
    }
    # Database preservation must be available before closing the running app.
    # Prefer the staged helper/runtime so the swap uses the new release's code.
    $backupPython = Join-Path $StagingDir "python\python.exe"
    $backupHelper = Join-Path $StagingDir "sqlite_copy.py"
    $integrityHelper = Join-Path $StagingDir "build_runtime_assets.py"
    foreach ($required in @($backupPython, $backupHelper, $integrityHelper)) {
        if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
            throw "Falta un archivo requerido del update: '$required'. Todo sigue igual."
        }
    }
    Write-Log "Verificando cada archivo del update antes de cerrar Tlamatini-Spanish..."
    # -B prevents the verifier from adding .pyc files to the tree it is checking;
    # -S avoids unrelated site-package startup hooks. Both helpers use stdlib only.
    & $backupPython -I -B -S $integrityHelper --verify-tree $StagingDir
    if ($LASTEXITCODE -ne 0) { throw "El update viene incompleto o alterado. Todo sigue igual." }
    $userDb = Join-Path $InstallDir "_internal\db.sqlite3"
    if ((Test-Path -LiteralPath $userDb -PathType Leaf) -and
        (-not (Test-Path -LiteralPath $backupPython -PathType Leaf) -or
         -not (Test-Path -LiteralPath $backupHelper -PathType Leaf))) {
        throw "Falta el helper de backup de la base de datos o el Python incluido. Se cancela antes de cerrar Tlamatini-Spanish."
    }
    Write-Log "Update y archivos de backup de la base de datos validados." "Green"

    # 2) Close the running Tlamatini and its whole process tree -- but NEVER
    #    this updater process. The updater is launched by self_update.py as a
    #    child of $ParentPid (the Tlamatini-Spanish.exe). A blind
    #    `taskkill /T /PID $ParentPid` walks the recorded parent/child tree --
    #    which CREATE_BREAKAWAY_FROM_JOB does NOT change -- so it would also
    #    kill US, and the update would abort right here after "Closing
    #    Tlamatini..." (the exact symptom of the 1.19.5 -> 1.20.0 failure).
    #    So we enumerate the descendant tree ourselves and skip our own $PID.
    Write-Log "Cerrando Tlamatini-Spanish (PID $ParentPid) y sus procesos hijos..."
    Start-Sleep -Seconds 2
    try {
        $procs   = Get-CimInstance Win32_Process -ErrorAction Stop
        $toKill  = New-Object System.Collections.Generic.List[int]
        $queue   = New-Object System.Collections.Generic.Queue[int]
        $seen    = New-Object System.Collections.Generic.HashSet[int]
        [void]$queue.Enqueue([int]$ParentPid)
        [void]$seen.Add([int]$ParentPid)
        while ($queue.Count -gt 0) {
            $cur = $queue.Dequeue()
            foreach ($p in $procs) {
                if ([int]$p.ParentProcessId -eq $cur) {
                    $cid = [int]$p.ProcessId
                    if ($cid -eq $PID) { continue }          # never our own updater
                    if ($seen.Add($cid)) {
                        [void]$queue.Enqueue($cid)
                        $toKill.Add($cid)                    # children, collected first
                    }
                }
            }
        }
        foreach ($k in $toKill) {
            try { & taskkill.exe /PID $k /F 2>&1 | Out-Null } catch {}
        }
        try { & taskkill.exe /PID $ParentPid /F 2>&1 | Out-Null } catch {}
        Write-Log ("Se cerraron el padre + {0} proceso(s) descendiente(s); el actualizador sigue (PID {1})." -f $toKill.Count, $PID)
    }
    catch {
        # Never fall back to /T: it can kill this updater, leaving a half-run swap.
        throw "No se pudo revisar con seguridad los procesos de Tlamatini-Spanish; los archivos siguen igual."
    }
    # Let Windows release the file handles (python\, git\, jre\, exe).
    Start-Sleep -Seconds 3
    Write-Log "Tlamatini-Spanish: cerrada." "Green"

    # 3a) Preserve the user's DATABASE across the update. The live db.sqlite3
    #     lives INSIDE _internal\ (PyInstaller _MEIPASS), which step 4 deletes,
    #     so the top-level $Preserve set cannot protect it. Use SQLite's backup
    #     API to include committed WAL pages in one verified file, staged into
    #     the preserved DB\ToLoad folder and flag a post-update migrate: on the
    #     next launch manage.py's _apply_pending_db_swap restores it over the
    #     freshly shipped DB, then _run_post_update_migrate_if_flagged applies
    #     the new migrations (new agents / tools / demo prompts) to the user's
    #     data -- so chat history + custom toggles are KEPT, not wiped.
    if (Test-Path -LiteralPath $userDb) {
        $toLoadDir = Join-Path $InstallDir "DB\ToLoad"
        if (-not (Test-Path -LiteralPath $toLoadDir)) {
            Invoke-WithRetry { New-Item -ItemType Directory -Path $toLoadDir -Force | Out-Null }
        }
        $backupTarget = Join-Path $toLoadDir "db.sqlite3"
        & $backupPython -I -B -S $backupHelper $userDb $backupTarget
        if ($LASTEXITCODE -ne 0) {
            throw "No se pudo hacer el backup de la base de datos. Los archivos siguen igual; la base de datos original sigue intacta."
        }
        Set-Content -LiteralPath (Join-Path $InstallDir "DB\post_update_migrate.flag") -Value (Get-Date -Format o) -Encoding UTF8
        Write-Log "Tu base de datos (incluidos sus commits WAL) -> DB\ToLoad, con un migrate marcado para el arranque siguiente." "Green"
    }
    else {
        Write-Log "No hay base de datos en _internal\db.sqlite3 (primera vez?) -- no hay DB que conservar." "Yellow"
    }

    # 3b) Back up the old agents directory: agents -> agents_backup.
    $agentsDir = Join-Path $InstallDir "agents"
    $agentsBak = Join-Path $InstallDir "agents_backup"
    if (Test-Path -LiteralPath $agentsDir) {
        if (Test-Path -LiteralPath $agentsBak) {
            Write-Log "Borrando el agents_backup anterior..."
            Invoke-WithRetry { Remove-Item -LiteralPath $agentsBak -Recurse -Force }
        }
        Write-Log "Renombrando agents -> agents_backup ..."
        Invoke-WithRetry { Rename-Item -LiteralPath $agentsDir -NewName "agents_backup" }
        Write-Log "Los agents anteriores quedaron en 'agents_backup'." "Green"
    }
    else {
        Write-Log "No hay carpeta 'agents' para el backup." "Yellow"
    }

    # 3c) Preserve the Blue-hat toolkit's EVIDENCE across the update.
    #     security\ is application code: the new release MUST replace the
    #     defender/whitelist scripts. But security\security_logs\ is the
    #     operator's own evidence -- alerts.log, monitor.log and the visible
    #     asset-test proof -- and it lives INSIDE security\, so like the
    #     database it cannot be protected by the top-level $Preserve set.
    #     A blind delete-and-replace destroys incident history at exactly the
    #     moment it matters. Stash it under the preserved Temp\ (same volume,
    #     so this is a rename, not a copy) and restore it in step 5b.
    #     Fail CLOSED before deletion if evidence cannot be moved safely.
    $securityLogs = Join-Path $InstallDir "security\security_logs"
    $logsCarryover = Join-Path $InstallDir ("Temp\_security_logs_carryover_" + [Guid]::NewGuid().ToString("N"))
    try {
        if (Test-Path -LiteralPath $securityLogs) {
            $carryParent = Split-Path -Parent $logsCarryover
            if (-not (Test-Path -LiteralPath $carryParent)) {
                New-Item -ItemType Directory -Path $carryParent -Force | Out-Null
            }
            Invoke-WithRetry { Move-Item -LiteralPath $securityLogs -Destination $logsCarryover -Force }
            Write-Log "Tu evidencia de seguridad se conserva -> $logsCarryover." "Green"
        }
        else {
            Write-Log "No hay security\security_logs que conservar (el toolkit no se ha usado?)." "Yellow"
        }
    }
    catch {
        throw "No se pudo conservar la evidencia de seguridad; se cancela el borrado de la app: $($_.Exception.Message)"
    }

    # 4) Delete the old install -- everything except the preserved set and
    #    the agents_backup we just created.
    Write-Log "Borrando los archivos anteriores de la app (tus datos se quedan)..."
    Get-ChildItem -LiteralPath $InstallDir -Force | ForEach-Object {
        $name = $_.Name
        if ($name -ieq "agents_backup") { return }
        if (Test-Preserved $name) { Write-Log "  queda   $name"; return }
        $full = $_.FullName
        Write-Log "  borra   $name"
        Invoke-WithRetry { Remove-Item -LiteralPath $full -Recurse -Force }
    }

    # 5) Move the new version in -- everything except the preserved set, so
    #    the user's config.json / DB / runtime dirs are never overwritten.
    Write-Log "Instalando el nuevo release..."
    Get-ChildItem -LiteralPath $StagingDir -Force | ForEach-Object {
        $name = $_.Name
        $src = $_.FullName
        $dest = Join-Path $InstallDir $name
        if ((Test-Preserved $name) -and (Test-Path -LiteralPath $dest)) {
            Write-Log "  omite   $name (se queda el tuyo)"; return
        }
        if (Test-Path -LiteralPath $dest) {
            Invoke-WithRetry { Remove-Item -LiteralPath $dest -Recurse -Force }
        }
        Write-Log "  instala $name"
        Invoke-WithRetry { Move-Item -LiteralPath $src -Destination $dest -Force }
    }

    # 5b) Put the Blue-hat evidence back inside the NEW security\ tree.
    #     The new release ships security\ without security_logs\ (build.py
    #     ignores it on purpose), so this simply moves the operator's history
    #     back where the defender expects to append to it. FAIL-OPEN: on any
    #     error the unique stash is LEFT in Temp\ rather than
    #     deleted, so the evidence still exists and can be recovered by hand.
    try {
        if (Test-Path -LiteralPath $logsCarryover) {
            $securityDir = Join-Path $InstallDir "security"
            if (-not (Test-Path -LiteralPath $securityDir)) {
                New-Item -ItemType Directory -Path $securityDir -Force | Out-Null
            }
            if (Test-Path -LiteralPath $securityLogs) {
                throw "Ya hay evidencia nueva en '$securityLogs'; se conservan las dos copias."
            }
            Invoke-WithRetry { Move-Item -LiteralPath $logsCarryover -Destination $securityLogs -Force }
            Write-Log "Tu evidencia de seguridad regresa -> security\security_logs." "Green"
        }
    }
    catch {
        Write-Log "AVISO: la evidencia de seguridad sigue en '$logsCarryover' -- hay que regresarla a mano: $($_.Exception.Message)" "Yellow"
    }

    # Repair owned flow registrations after files have been replaced. Explicitly
    # unregistered types and Windows default-app choices remain untouched.
    $flowRegistration = Join-Path $InstallDir 'flow_file_associations.ps1'
    if (Test-Path -LiteralPath $flowRegistration -PathType Leaf) {
        try {
            & $flowRegistration -Action Repair -InstallDir $InstallDir
            Write-Log 'Registro de archivos de flow: reparado.'
        } catch { Write-Log "El registro de archivos de flow requiere revisarse: $_" 'Yellow' }
    }

    # 6) Clean up the staging area (best effort).
    try {
        # Exact validated directory from step 1, never a caller-derived parent.
        if ($updateRoot -and (Test-Path -LiteralPath $updateRoot)) {
            Remove-Item -LiteralPath $updateRoot -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
    catch {}

    Write-Host ""
    Write-Log "UPDATE COMPLETO." "Green"

    # 7) Relaunch Tlamatini.
    if (-not $RelaunchExe) { $RelaunchExe = Join-Path $InstallDir "Tlamatini-Spanish.exe" }
    if (Test-Path -LiteralPath $RelaunchExe) {
        Write-Log "Iniciando el nuevo Tlamatini-Spanish..." "Cyan"
        Start-Process -FilePath $RelaunchExe -WorkingDirectory $InstallDir -WindowStyle Hidden
    }
    else {
        Write-Log "Falta Tlamatini-Spanish.exe tras el update -- hay que iniciarlo a mano." "Yellow"
    }
    Start-Sleep -Seconds 4
    exit 0
}
catch {
    Write-Host ""
    Write-Log "ERROR EN EL UPDATE: $($_.Exception.Message)" "Red"
    Write-Log "Tus agents anteriores siguen en 'agents_backup'." "Yellow"
    if ($LogPath) { Write-Log "Log completo: $LogPath" "Yellow" }
    Write-Host ""
    try { Read-Host "Presiona Enter para cerrar" } catch {}
    exit 1
}
