# Tlamatini PowerShell Script
# Executes the Django development server with --noreload flag
# and automatically opens the browser on the configured web port
# Accepts an optional .flw or .fpmt file path as argument (e.g. from file association)

param(
    [string]$FlowFile
)

Write-Host "Iniciando el servidor de desarrollo de Tlamatini..." -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""

# Resolve paths relative to this script's directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$TlamatiniExe = Join-Path $scriptDir "Tlamatini.exe"

# Resolve an incoming relative path BEFORE changing the working directory.
if ($FlowFile) {
    if ([IO.Path]::GetExtension($FlowFile) -notin @('.flw', '.fpmt')) { throw 'Elige un archivo de flow .flw o .fpmt.' }
    $FlowFile = (Resolve-Path -LiteralPath $FlowFile -ErrorAction Stop).Path
}

# Set working directory to the script's directory (critical for PyInstaller builds)
Set-Location $scriptDir
Write-Host "Directorio de trabajo: $scriptDir" -ForegroundColor Gray

# Check if Tlamatini.exe exists
if (-not (Test-Path $TlamatiniExe)) {
    Write-Host "Error: falta Tlamatini.exe" -ForegroundColor Red
    Write-Host "Debe estar en: $TlamatiniExe" -ForegroundColor Yellow
    Read-Host "Presiona Enter para salir"
    exit 1
}

# Build argument list depending on whether a flow file was passed
# When a flow file is given, pass ONLY the file path to Tlamatini.exe
# (manage.py detects either flow format and internally rewrites argv to runserver --noreload)
# When no flow file is given, pass runserver --noreload explicitly.
if ($FlowFile) {
    if (-not (Test-Path $FlowFile)) {
        Write-Host "Aviso: no existe el archivo de flow: $FlowFile" -ForegroundColor Yellow
    }
    else {
        $FlowFile = (Resolve-Path $FlowFile).Path
    }
    Write-Host "Abriendo el archivo de flow: $FlowFile" -ForegroundColor Magenta
    $serverArgs = @($FlowFile)
}
else {
    $serverArgs = @('runserver', '--noreload')
}

Write-Host "Ejecutando: Tlamatini.exe $($serverArgs -join ' ')" -ForegroundColor Green
Write-Host ""

Write-Host "Arrancando el servidor..." -ForegroundColor Cyan
Write-Host "Presiona Ctrl+C para detener el servidor." -ForegroundColor Cyan
Write-Host ""

# manage.py opens the correct editor once, using the configured web port.

# Run Tlamatini.exe directly so all output and errors are visible in this console
& $TlamatiniExe $serverArgs

# If we get here, the process has exited
Write-Host ""
Write-Host "Tlamatini.exe se detuvo (exit code: $LASTEXITCODE)." -ForegroundColor Red
Read-Host "Presiona Enter para cerrar esta ventana"
