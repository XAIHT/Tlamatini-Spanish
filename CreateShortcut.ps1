# Shortcut Creator for Tlamatini
# Reads the installation directory from CreateShortcut.json

param(
    [switch]$DesktopOnly,
    [switch]$LocalOnly
)

$ErrorActionPreference = 'Stop'

$scriptDir = $PSScriptRoot
$configPath = Join-Path $scriptDir "CreateShortcut.json"

Write-Host "Creador de accesos directos de Tlamatini-Spanish" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Cyan
Write-Host ""

# Read install directory from CreateShortcut.json
if (-not (Test-Path $configPath)) {
    Write-Host "Error: no existe CreateShortcut.json en: $configPath" -ForegroundColor Red
    Write-Host "Hay que crearlo con un contenido como este:" -ForegroundColor Yellow
    Write-Host '  { "InstallDir": "D:\\Tlamatini-Spanish" }' -ForegroundColor Yellow
    exit 1
}

try {
    $config = Get-Content $configPath -Raw | ConvertFrom-Json
} catch {
    Write-Host "Error: no se pudo leer CreateShortcut.json: $_" -ForegroundColor Red
    exit 1
}

if (-not $config.InstallDir) {
    Write-Host 'Error: falta la llave "InstallDir" en CreateShortcut.json' -ForegroundColor Red
    exit 1
}

$installDir = $config.InstallDir

if (-not (Test-Path $installDir)) {
    Write-Host "Error: no existe la carpeta destino: $installDir" -ForegroundColor Red
    exit 1
}

$installDir = (Resolve-Path $installDir).Path
$exePath = Join-Path $installDir "Tlamatini-Spanish.exe"
$iconPath = Join-Path $installDir "Tlamatini.ico"
$conhostPath = Join-Path $env:SystemRoot "System32\conhost.exe"

Write-Host "Carpeta destino: $installDir" -ForegroundColor White

# Two launch strategies:
#   * conhost.exe wrapper -- the shortcut target is conhost.exe and the
#     argument is Tlamatini-Spanish.exe.  Forces the legacy Console Host to own the
#     window even when Windows Terminal is the default host, so WM_SETICON
#     and the embedded .exe icon take effect on the title bar.
#   * Direct Tlamatini-Spanish.exe -- the shortcut targets the .exe straight.  Works
#     on machines with restrictive Group Policy / AppLocker / WDAC where
#     conhost.exe is allowed to run but is silently prevented from launching
#     arbitrary child executables, which made earlier "always wrap" versions
#     produce shortcuts that did nothing when clicked.
# We probe end-to-end at install time and pick the right one for THIS host.
if (-not (Test-Path $exePath)) {
    Write-Host "Error: falta Tlamatini-Spanish.exe en: $exePath" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Tlamatini-Spanish.exe encontrado: $exePath" -ForegroundColor Green

# Check icon
if (Test-Path $iconPath) {
    Write-Host "[OK] Icono encontrado: $iconPath" -ForegroundColor Green
} else {
    Write-Host "[!] Aviso: falta Tlamatini.ico en $iconPath" -ForegroundColor Yellow
    Write-Host "    El acceso directo va a usar el icono incluido en el .exe." -ForegroundColor Yellow
}

function Test-ConhostWrapperUsable {
    # Returns $true only when `conhost.exe <child.exe>` can actually launch
    # its child end-to-end.  On AppLocker / WDAC / restrictive-Group-Policy
    # machines the conhost binary itself is allowed (it's system-essential)
    # but the parent->child launch is silently blocked, which is the exact
    # failure mode that made the unconditional wrapper produce dead
    # shortcuts.  We exercise the same chain with a benign, fast,
    # always-available probe: cmd.exe /c exit 0.
    if (-not (Test-Path $conhostPath)) {
        Write-Host "[probe] falta conhost.exe; se apunta directo al exe." -ForegroundColor Gray
        return $false
    }
    try {
        $proc = Start-Process -FilePath $conhostPath `
            -ArgumentList @('cmd.exe', '/c', 'exit 0') `
            -PassThru -WindowStyle Hidden -ErrorAction Stop
        $exited = $proc.WaitForExit(5000)
        if (-not $exited) {
            try { $proc.Kill() } catch {}
            Write-Host "[probe] la prueba del wrapper conhost.exe dio timeout; el host se trata como restringido." -ForegroundColor Gray
            return $false
        }
        if ($proc.ExitCode -eq 0) {
            return $true
        }
        Write-Host "[probe] la prueba del wrapper conhost.exe dio el exit code $($proc.ExitCode); el host se trata como restringido." -ForegroundColor Gray
        return $false
    } catch {
        Write-Host "[probe] error en la prueba del wrapper conhost.exe: $_" -ForegroundColor Gray
        return $false
    }
}

$useConhost = Test-ConhostWrapperUsable
if ($useConhost) {
    Write-Host "[OK] el wrapper conhost.exe sirve -- el acceso directo va a forzar el console host de siempre (el icono se ve bien aunque Windows Terminal sea el predeterminado)." -ForegroundColor Green
} else {
    Write-Host "[!] el wrapper conhost.exe NO sirve en esta computadora -- el acceso directo va a apuntar directo a Tlamatini-Spanish.exe." -ForegroundColor Yellow
    Write-Host "    En la barra de la ventana se va a leer 'Tlamatini-Spanish', pero el icono de la ventana puede ser el del host." -ForegroundColor Yellow
}
$useConhostFlag = if ($useConhost) { '1' } else { '0' }

Write-Host ""
Write-Host "Creando los accesos directos con el helper de VBScript..." -ForegroundColor White
Write-Host ""

# Create a temporary VBScript to create the shortcut
# Pass installDir as a command-line argument to the VBScript
$vbsScript = @"
Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Args: 0 = install directory, 1 = useConhost flag ("1" or "0")
If WScript.Arguments.Count < 2 Then
    WScript.Echo "Error: se requieren los argumentos de carpeta destino y useConhost."
    WScript.Quit 1
End If

strInstallDir = WScript.Arguments(0)
bUseConhost = (WScript.Arguments(1) = "1")
strExePath = objFSO.BuildPath(strInstallDir, "Tlamatini-Spanish.exe")
strIconPath = objFSO.BuildPath(strInstallDir, "Tlamatini.ico")
strConhostPath = objShell.ExpandEnvironmentStrings("%SystemRoot%\System32\conhost.exe")

' Two strategies, decided by the PowerShell-side probe:
'   bUseConhost = True  -> wrap with conhost.exe so the running-window icon
'                          is the .exe's embedded Tlamatini icon under any
'                          terminal host (Windows Terminal ignores
'                          WM_SETICON, so the wrapper is the only way).
'   bUseConhost = False -> target Tlamatini-Spanish.exe directly; required on
'                          AppLocker / WDAC / restrictive-policy machines
'                          where the wrapper produces dead shortcuts.

Sub CreateShortcut(shortcutPath)
    Set objShortcut = objShell.CreateShortcut(shortcutPath)

    If bUseConhost Then
        objShortcut.TargetPath = strConhostPath
        objShortcut.Arguments = """" & strExePath & """"
    Else
        objShortcut.TargetPath = strExePath
        objShortcut.Arguments = ""
    End If
    objShortcut.WorkingDirectory = strInstallDir
    objShortcut.Description = "Servidor de desarrollo de Tlamatini-Spanish"
    objShortcut.WindowStyle = 1

    ' Set icon: prefer the standalone .ico (sharper at all sizes for the
    ' .lnk file in Explorer/Desktop); fall back to the .exe's embedded icon.
    ' This is independent of TargetPath -- it controls the .lnk's icon in
    ' Explorer/Desktop, not the running console-window icon.
    If objFSO.FileExists(strIconPath) Then
        objShortcut.IconLocation = strIconPath & ",0"
    Else
        objShortcut.IconLocation = strExePath & ",0"
    End If

    objShortcut.Save
    If bUseConhost Then
        WScript.Echo "[OK] Creado (con conhost): " & shortcutPath
    Else
        WScript.Echo "[OK] Creado (exe directo):  " & shortcutPath
    End If
End Sub

' Create desktop shortcut
strDesktop = objShell.SpecialFolders("Desktop")
Call CreateShortcut(objFSO.BuildPath(strDesktop, "Tlamatini-Spanish.lnk"))

' Create local shortcut in install directory
Call CreateShortcut(objFSO.BuildPath(strInstallDir, "Tlamatini-Spanish.lnk"))

WScript.Echo ""
WScript.Echo "Listo: accesos directos creados."
"@

# Save the VBScript to a temporary file
$vbsPath = Join-Path $scriptDir "CreateShortcut_Temp.vbs"
$vbsScript | Out-File -FilePath $vbsPath -Encoding ASCII

# Try VBScript first, fall back to pure PowerShell COM if cscript is blocked
$vbsSuccess = $false
try {
    $output = & cscript.exe //NoLogo $vbsPath "$installDir" "$useConhostFlag" 2>&1
    if ($LASTEXITCODE -eq 0) {
        $output | ForEach-Object { Write-Host $_ -ForegroundColor Green }
        $vbsSuccess = $true
    }
} catch {
    Write-Host "[!] cscript.exe dio error o lo bloquea una regla del sistema -- se usa el fallback de PowerShell." -ForegroundColor Yellow
}

# Clean up the temporary VBS file regardless
Remove-Item $vbsPath -ErrorAction SilentlyContinue

# PowerShell COM fallback -- works even when cscript/wscript are blocked by
# AppLocker / WDAC / Group Policy, because WScript.Shell COM is still
# accessible from PowerShell running under -ExecutionPolicy Bypass.
if (-not $vbsSuccess) {
    Write-Host "Creando los accesos directos con el fallback COM de PowerShell..." -ForegroundColor White
    try {
        $shell = New-Object -ComObject WScript.Shell

        function New-TlamatiniShortcut($lnkPath) {
            $sc = $shell.CreateShortcut($lnkPath)
            if ($script:useConhost) {
                $sc.TargetPath = $script:conhostPath
                $sc.Arguments = "`"$script:exePath`""
            } else {
                $sc.TargetPath = $script:exePath
                $sc.Arguments = ""
            }
            $sc.WorkingDirectory = $script:installDir
            $sc.Description = "Servidor de desarrollo de Tlamatini-Spanish"
            $sc.WindowStyle = 1
            if (Test-Path $script:iconPath) {
                $sc.IconLocation = "$script:iconPath,0"
            } else {
                $sc.IconLocation = "$script:exePath,0"
            }
            $sc.Save()
            $tag = if ($script:useConhost) { "con conhost" } else { "exe directo" }
            Write-Host "[OK] Creado ($tag): $lnkPath" -ForegroundColor Green
        }

        # Desktop shortcut
        $desktopPath = [Environment]::GetFolderPath("Desktop")
        New-TlamatiniShortcut (Join-Path $desktopPath "Tlamatini-Spanish.lnk")

        # Local shortcut in install directory
        New-TlamatiniShortcut (Join-Path $installDir "Tlamatini-Spanish.lnk")

        Write-Host ""
        Write-Host "Listo: accesos directos creados." -ForegroundColor Green
    } catch {
        Write-Error "Error al crear los accesos directos con PowerShell: $_"
        exit 1
    }
}

# A fallback that succeeded must not inherit cscript's earlier failing exit code.
$global:LASTEXITCODE = 0

Write-Host ""
Write-Host "Ahora puedes:" -ForegroundColor Cyan
Write-Host "  1. Hacer doble clic en el acceso directo del escritorio" -ForegroundColor White
Write-Host "  2. Hacer doble clic en 'Tlamatini-Spanish.lnk' dentro de $installDir" -ForegroundColor White
Write-Host "  3. Anclar el acceso directo a la barra de tareas o a Inicio" -ForegroundColor White
