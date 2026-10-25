# Shortcut Remover for Tlamatini
# Removes the desktop and local shortcuts created by CreateShortcut.ps1
# and forces Windows Explorer to refresh so the icons disappear immediately.

$scriptDir = $PSScriptRoot
$ErrorActionPreference = 'Stop'

# SHChangeNotify C# interop code (may fail in Constrained Language Mode)
$csharpCode = 'using System; using System.Runtime.InteropServices; public class ShellNotify { [DllImport("shell32.dll", CharSet = CharSet.Auto, SetLastError = true)] public static extern void SHChangeNotify(int wEventId, int uFlags, IntPtr dwItem1, IntPtr dwItem2); }'

Write-Host "Eliminador de accesos directos de Tlamatini" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Cyan
Write-Host ""

# ── Remove desktop shortcut ──────────────────────────────────────────────────
$desktopPath = [Environment]::GetFolderPath("Desktop")
$desktopShortcut = Join-Path $desktopPath "Tlamatini.lnk"

if (Test-Path $desktopShortcut) {
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($desktopShortcut)
    $owned = $shortcut.WorkingDirectory.TrimEnd('\') -ieq $scriptDir.TrimEnd('\')
    if ($owned) {
        Remove-Item -LiteralPath $desktopShortcut -Force -ErrorAction Stop
        Write-Host "[OK] Acceso directo del escritorio eliminado: $desktopShortcut" -ForegroundColor Green
    } else {
        Write-Host '[--] Se deja el acceso directo del escritorio: es de otra copia de Tlamatini.'
    }
} else {
    Write-Host "[--] No hay acceso directo en el escritorio: $desktopShortcut" -ForegroundColor DarkGray
}

# ── Remove local shortcut in the install directory ───────────────────────────
$localShortcut = Join-Path $scriptDir "Tlamatini.lnk"

if (Test-Path $localShortcut) {
        Remove-Item -LiteralPath $localShortcut -Force -ErrorAction Stop
        Write-Host "[OK] Acceso directo local eliminado: $localShortcut" -ForegroundColor Green
} else {
    Write-Host "[--] No hay acceso directo local: $localShortcut" -ForegroundColor DarkGray
}

# ── Notify Windows Shell of the change ───────────────────────────────────────
Write-Host ""
Write-Host "Actualizando el Shell de Windows..." -ForegroundColor Cyan

try {
    Add-Type -TypeDefinition $csharpCode -ErrorAction Stop
    [ShellNotify]::SHChangeNotify(0x08000000, 0x0000, [IntPtr]::Zero, [IntPtr]::Zero)
    Write-Host "  [OK] Shell de Windows avisado (SHChangeNotify)" -ForegroundColor Green
}
catch {
    Write-Host "  [AVISO] Add-Type no disponible (Constrained Language Mode) - se usa el fallback" -ForegroundColor Yellow
    & rundll32.exe user32.dll, UpdatePerUserSystemParameters 2>$null
    Write-Host "  [OK] Shell avisado con el fallback de rundll32" -ForegroundColor Green
}

Write-Host ""
Write-Host "SUCCESS: se eliminaron los accesos directos." -ForegroundColor Green
