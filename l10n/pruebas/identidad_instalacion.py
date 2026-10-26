# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "la que sabe"
#
#   Creado por  Angela López Mendoza   ·   @angelahack1
#   Desarrolladora · Arquitecta · Creadora de Tlamatini
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — no se quita (el nombre de Angela va en cada build)
"""Prueba VISIBLE de que Tlamatini-Spanish convive con Tlamatini (inglés), 100 % aparte.

Se corre en una consola a la vista, en tres fases:

    python l10n/pruebas/identidad_instalacion.py antes        # foto del inglés ANTES de instalar
    python l10n/pruebas/identidad_instalacion.py despues      # registro, archivos, accesos directos
    python l10n/pruebas/identidad_instalacion.py ejecucion    # las dos corriendo a la vez

`antes` guarda lo que el sistema operativo sabe del inglés (Aplicaciones instaladas,
descubrimiento, ProgIDs, capacidades, accesos directos, su programa). `despues` revisa
CADA valor que la instalación en español debió escribir y compara el inglés contra la
foto: nada del inglés puede cambiar. `ejecucion` arranca Tlamatini-Spanish por su
acceso directo y comprueba puertos, procesos, título de consola y el endpoint de flows
de las dos instalaciones al mismo tiempo. Las fotos de pantalla completa las toma el
agent Shoter de este árbol.

Salida: <repo>/Temp/identidad_instalacion/ (informe JSON + fotos). Código de salida:
0 todo pasó · 1 alguna revisión falló · 2 falta la foto `antes`.
"""
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
import winreg
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = RAIZ / "Temp" / "identidad_instalacion"
SHOTER = RAIZ / "Tlamatini" / "agent" / "agents" / "shoter"
FOTO_ANTES = SALIDA / "ingles_antes.json"

ES_DIR = Path(r"C:\XAIHT\Tlamatini-Spanish")
EN_DIR = Path(r"C:\Tlamatini")
VERSION = "1.91.0"
UNINSTALL = r"Software\Microsoft\Windows\CurrentVersion\Uninstall"
HKCU = winreg.HKEY_CURRENT_USER

resultados = []


def revisar(nombre: str, ok: bool, detalle: str = "") -> bool:
    resultados.append({"revision": nombre, "ok": bool(ok), "detalle": detalle})
    print(f"{'✓' if ok else '✗'} {nombre}" + (f"  — {detalle}" if detalle else ""), flush=True)
    return ok


# ───────────────────────── lectura del sistema ─────────────────────────

def valores(ruta: str) -> dict | None:
    """Todos los valores de una llave de HKCU (None si no existe)."""
    try:
        with winreg.OpenKey(HKCU, ruta) as llave:
            datos, i = {}, 0
            while True:
                try:
                    nombre, valor, _tipo = winreg.EnumValue(llave, i)
                except OSError:
                    return datos
                datos[nombre] = valor if not isinstance(valor, bytes) else valor.hex()
                i += 1
    except FileNotFoundError:
        return None


def valor(ruta: str, nombre: str = ""):
    v = valores(ruta)
    return None if v is None else v.get(nombre)


def powershell(script: str) -> str:
    r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
    return r.stdout.strip()


def escritorio() -> Path:
    return Path(powershell("[Environment]::GetFolderPath('Desktop')"))


def acceso_directo(lnk: Path) -> dict | None:
    if not lnk.is_file():
        return None
    salida = powershell(
        "$s=(New-Object -ComObject WScript.Shell).CreateShortcut('" + str(lnk).replace("'", "''") + "');"
        "[pscustomobject]@{Target=$s.TargetPath;Arguments=$s.Arguments;WorkingDirectory=$s.WorkingDirectory;"
        "Icon=$s.IconLocation;Description=$s.Description} | ConvertTo-Json -Compress")
    return json.loads(salida) if salida else None


def version_exe(exe: Path) -> dict | None:
    if not exe.is_file():
        return None
    salida = powershell(
        "$v=(Get-Item -LiteralPath '" + str(exe).replace("'", "''") + "').VersionInfo;"
        "[pscustomobject]@{ProductName=$v.ProductName;FileDescription=$v.FileDescription;"
        "OriginalFilename=$v.OriginalFilename;InternalName=$v.InternalName;"
        "ProductVersion=$v.ProductVersion;CompanyName=$v.CompanyName} | ConvertTo-Json -Compress")
    return json.loads(salida) if salida else None


def identidad_inglesa() -> dict:
    """Todo lo que el sistema operativo sabe del Tlamatini inglés."""
    lnk = escritorio() / "Tlamatini.lnk"
    exe = EN_DIR / "Tlamatini.exe"
    return {
        "arp": valores(UNINSTALL + r"\Tlamatini"),
        "descubrimiento": valores(r"Software\XAIHT\Tlamatini"),
        "progid_flw": valores(r"Software\Classes\Tlamatini.FlowFile"),
        "progid_flw_comando": valor(r"Software\Classes\Tlamatini.FlowFile\shell\open\command"),
        "progid_fpmt": valores(r"Software\Classes\Tlamatini.PromptFlowFile"),
        "progid_fpmt_comando": valor(r"Software\Classes\Tlamatini.PromptFlowFile\shell\open\command"),
        "capacidades": valores(r"Software\Tlamatini\FlowCapabilities"),
        "capacidades_asociaciones": valores(r"Software\Tlamatini\FlowCapabilities\FileAssociations"),
        "registrada": valor(r"Software\RegisteredApplications", "TlamatiniFlows"),
        "flw_predeterminado": valor(r"Software\Classes\.flw"),
        "fpmt_predeterminado": valor(r"Software\Classes\.fpmt"),
        "lnk_escritorio": acceso_directo(lnk),
        "exe_existe": exe.is_file(),
        "exe_tamano": exe.stat().st_size if exe.is_file() else None,
        "exe_mtime": exe.stat().st_mtime if exe.is_file() else None,
        "config_mtime": (EN_DIR / "config.json").stat().st_mtime if (EN_DIR / "config.json").is_file() else None,
    }


# ───────────────────────── Shoter ─────────────────────────

_RUNTIME = None


def foto(nombre: str) -> str | None:
    """Foto de TODO el escritorio con el agent Shoter de este árbol (nunca Pillow)."""
    global _RUNTIME
    if _RUNTIME is None:
        _RUNTIME = SALIDA / "_shoter_runtime"
        shutil.rmtree(_RUNTIME, ignore_errors=True)
        shutil.copytree(SHOTER, _RUNTIME, ignore=shutil.ignore_patterns("__pycache__", "*.log", "shoter_*"))
    with open(_RUNTIME / "config.yaml", "w", encoding="utf-8", newline="\n") as fh:
        fh.write(f"output_dir: {str(SALIDA).replace(chr(92), '/')}\n")
        fh.write("all_screens: true\n")
        fh.write(f"filename: {nombre}\n")
        fh.write("target_agents: []\n")
    r = subprocess.run([sys.executable, "shoter.py"], cwd=_RUNTIME, capture_output=True, text=True,
                       timeout=90, encoding="utf-8", errors="replace")
    destino = SALIDA / nombre
    revisar(f"Shoter tomó la foto {nombre}", destino.is_file(), "" if destino.is_file() else f"rc={r.returncode}")
    return str(destino) if destino.is_file() else None


# ───────────────────────── fases ─────────────────────────

def fase_antes() -> int:
    SALIDA.mkdir(parents=True, exist_ok=True)
    datos = identidad_inglesa()
    FOTO_ANTES.write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")
    revisar("foto del Tlamatini inglés guardada", True, str(FOTO_ANTES))
    revisar("el inglés está registrado en Aplicaciones instaladas", bool(datos["arp"]),
            (datos["arp"] or {}).get("InstallLocation", ""))
    revisar("Tlamatini-Spanish todavía NO existe en el registro",
            valores(UNINSTALL + r"\Tlamatini-Spanish") is None and valores(r"Software\XAIHT\Tlamatini-Spanish") is None)
    return 0


def fase_despues() -> int:
    if not FOTO_ANTES.is_file():
        print("✗ falta la foto `antes`: córrela antes de instalar", flush=True)
        return 2
    d = ES_DIR
    exe = d / "Tlamatini-Spanish.exe"
    # ── archivos ──
    revisar("carpeta de instalación", d.is_dir(), str(d))
    revisar("programa Tlamatini-Spanish.exe", exe.is_file())
    revisar("no hay Tlamatini.exe en la carpeta en español", not (d / "Tlamatini.exe").exists())
    revisar("Uninstaller.exe junto al programa", (d / "Uninstaller.exe").is_file())
    py = d / "python" / "python.exe"
    revisar("Python cargado propio (python\\python.exe)", py.is_file(), str(py))
    if py.is_file():
        r = subprocess.run([str(py), "-I", "-c", "import sys;print(sys.prefix)"], capture_output=True, text=True, timeout=60,
                           env={**{k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "PYTHONHOME")},
                                "PYTHONNOUSERSITE": "1"})
        prefijo = r.stdout.strip()
        revisar("el Python cargado vive dentro de Tlamatini-Spanish",
                Path(prefijo).resolve() == (d / "python").resolve(), prefijo)
        revisar("el Python cargado NO es el del inglés",
                Path(prefijo).resolve() != (EN_DIR / "python").resolve())
    try:
        cfg = json.loads((d / "config.json").read_text(encoding="utf-8-sig"))
    except Exception as exc:  # noqa: BLE001
        cfg = {}
        revisar("config.json legible", False, str(exc))
    revisar("puerto web propio 8052", cfg.get("django_port") == 8052, str(cfg.get("django_port")))
    revisar("puerto System-Metrics propio 8752", cfg.get("mcp_system_server_port") == 8752
            and cfg.get("mcp_system_client_uri") == "ws://127.0.0.1:8752")
    revisar("puerto Files-Search propio 50052", cfg.get("mcp_files_search_server_port") == 50052
            and cfg.get("mcp_files_search_client_uri") == "ws://127.0.0.1:50052")
    atajo = json.loads((d / "CreateShortcut.json").read_text(encoding="utf-8-sig")) if (d / "CreateShortcut.json").is_file() else {}
    revisar("CreateShortcut.json apunta a la carpeta en español", atajo.get("InstallDir", "").lower() == str(d).lower())
    try:
        mcps = (d / "external_mcps.json").read_text(encoding="utf-8-sig")
        revisar("la memoria del MCP 'memory' es propia (no la del inglés)",
                "Local\\\\Tlamatini\\\\memory" not in mcps and "Local\\Tlamatini\\memory" not in mcps)
    except FileNotFoundError:
        revisar("external_mcps.json instalado", False)
    # ── VERSIONINFO ──
    v = version_exe(exe) or {}
    revisar("VERSIONINFO ProductName = Tlamatini-Spanish", v.get("ProductName") == "Tlamatini-Spanish", str(v.get("ProductName")))
    revisar("VERSIONINFO OriginalFilename = Tlamatini-Spanish.exe", v.get("OriginalFilename") == "Tlamatini-Spanish.exe")
    revisar("VERSIONINFO FileDescription nombra Tlamatini-Spanish", str(v.get("FileDescription", "")).startswith("Tlamatini-Spanish"),
            str(v.get("FileDescription")))
    revisar(f"VERSIONINFO versión {VERSION}", str(v.get("ProductVersion", "")).startswith(VERSION), str(v.get("ProductVersion")))
    u = version_exe(d / "Uninstaller.exe") or {}
    revisar("el desinstalador se presenta como Tlamatini-Spanish Uninstaller",
            u.get("ProductName") == "Tlamatini-Spanish Uninstaller", str(u.get("ProductName")))
    # ── Aplicaciones instaladas (Panel de control) ──
    arp = valores(UNINSTALL + r"\Tlamatini-Spanish") or {}
    revisar("entrada propia en Aplicaciones instaladas", bool(arp))
    revisar("DisplayName = Tlamatini-Spanish", arp.get("DisplayName") == "Tlamatini-Spanish", str(arp.get("DisplayName")))
    revisar(f"DisplayVersion = {VERSION}", arp.get("DisplayVersion") == VERSION, str(arp.get("DisplayVersion")))
    revisar("Publisher = XAIHT", arp.get("Publisher") == "XAIHT")
    revisar("InstallLocation = carpeta en español", str(arp.get("InstallLocation", "")).lower() == str(d).lower())
    revisar("UninstallString = su propio Uninstaller.exe",
            arp.get("UninstallString", "").lower() == f'"{d / "Uninstaller.exe"}"'.lower(), str(arp.get("UninstallString")))
    revisar("DisplayIcon dentro de la carpeta en español", str(arp.get("DisplayIcon", "")).lower().startswith(str(d).lower()))
    revisar("URLInfoAbout = XAIHT/Tlamatini-Spanish", arp.get("URLInfoAbout") == "https://github.com/XAIHT/Tlamatini-Spanish")
    # ── descubrimiento (FlowPills) ──
    disc = valores(r"Software\XAIHT\Tlamatini-Spanish") or {}
    revisar("llave de descubrimiento propia", bool(disc))
    revisar("descubrimiento InstallLocation", str(disc.get("InstallLocation", "")).lower() == str(d).lower())
    revisar("descubrimiento AgentsRoot", str(disc.get("AgentsRoot", "")).lower() == str(d / "agents").lower())
    revisar("descubrimiento AgentManifestPath existe", bool(disc.get("AgentManifestPath")) and Path(disc["AgentManifestPath"]).is_file())
    revisar(f"descubrimiento Version = {VERSION}", disc.get("Version") == VERSION)
    # ── flows .flw / .fpmt ──
    for ext, prog in ((".flw", "TlamatiniSpanish.FlowFile"), (".fpmt", "TlamatiniSpanish.PromptFlowFile")):
        base = rf"Software\Classes\{prog}"
        revisar(f"ProgID {prog} es de esta instalación",
                str(valor(base, "TlamatiniInstallDir") or "").lower() == str(d).lower())
        comando = str(valor(base + r"\shell\open\command") or "")
        revisar(f"{prog} abre con Tlamatini-Spanish.exe", f'"{exe}" "%1"'.lower() in comando.lower(), comando)
        revisar(f"{prog} usa el ícono propio", str(d).lower() in str(valor(base + r"\DefaultIcon") or "").lower())
        revisar(f"{prog} se presenta como Tlamatini-Spanish", valor(base + r"\shell\open", "FriendlyAppName") == "Tlamatini-Spanish")
        abrir_con = valores(rf"Software\Classes\{ext}\OpenWithProgids") or {}
        revisar(f"{ext} ofrece Tlamatini-Spanish en 'Abrir con'", prog in abrir_con)
        revisar(f"capacidades: {ext} → {prog}",
                valor(r"Software\Tlamatini-Spanish\FlowCapabilities\FileAssociations", ext) == prog)
    revisar("capacidades ApplicationName = Tlamatini-Spanish",
            valor(r"Software\Tlamatini-Spanish\FlowCapabilities", "ApplicationName") == "Tlamatini-Spanish")
    revisar("RegisteredApplications\\TlamatiniSpanishFlows",
            valor(r"Software\RegisteredApplications", "TlamatiniSpanishFlows") == r"Software\Tlamatini-Spanish\FlowCapabilities")
    # ── accesos directos ──
    for lnk in (escritorio() / "Tlamatini-Spanish.lnk", d / "Tlamatini-Spanish.lnk"):
        a = acceso_directo(lnk)
        revisar(f"acceso directo {lnk.name} en {lnk.parent}", a is not None)
        if a:
            destino = (a.get("Target", "") + " " + a.get("Arguments", "")).lower()
            revisar(f"{lnk.parent.name}\\{lnk.name} arranca Tlamatini-Spanish.exe", str(exe).lower() in destino, destino)
            revisar(f"{lnk.parent.name}\\{lnk.name} trabaja en la carpeta en español",
                    str(a.get("WorkingDirectory", "")).lower() == str(d).lower())
    # ── registro de la instalación ──
    logs = Path(os.environ["LOCALAPPDATA"]) / "Tlamatini-Spanish" / "SetupLogs"
    revisar("bitácora del instalador en %LOCALAPPDATA%\\Tlamatini-Spanish\\SetupLogs",
            logs.is_dir() and any(logs.glob("*installation*.log")), str(logs))
    # ── el inglés no cambió ──
    comparar_ingles()
    foto("identidad_despues_escritorio.png")
    return guardar("despues")


def comparar_ingles():
    antes = json.loads(FOTO_ANTES.read_text(encoding="utf-8"))
    ahora = identidad_inglesa()
    for clave in antes:
        revisar(f"inglés intacto: {clave}", antes[clave] == ahora[clave],
                "" if antes[clave] == ahora[clave] else f"antes={antes[clave]!r} ahora={ahora[clave]!r}"[:300])


def escuchando() -> dict:
    """{puerto: (pid, ruta del programa)} de los puertos que nos importan."""
    import psutil
    puertos = {8000, 8765, 50051, 8052, 8752, 50052}
    datos = {}
    for c in psutil.net_connections(kind="tcp"):
        if c.status == psutil.CONN_LISTEN and c.laddr.port in puertos and c.pid:
            try:
                datos[c.laddr.port] = (c.pid, psutil.Process(c.pid).exe())
            except Exception:  # noqa: BLE001
                datos[c.laddr.port] = (c.pid, "?")
    return datos


def estado_flows(puerto: int):
    try:
        abridor = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with abridor.open(f"http://127.0.0.1:{puerto}/agent/flow_files/status/", timeout=5) as r:
            return json.loads(r.read(4097))
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}


def ventanas_con_titulo(texto: str) -> dict:
    """{hwnd: título} de las ventanas visibles cuyo título contiene `texto`."""
    import ctypes
    from ctypes import wintypes
    user32 = ctypes.windll.user32
    titulos = {}

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def cada(hwnd, _):
        if user32.IsWindowVisible(hwnd):
            n = user32.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(n + 1)
            user32.GetWindowTextW(hwnd, buf, n + 1)
            if texto in buf.value:
                titulos[int(hwnd or 0)] = buf.value
        return True
    user32.EnumWindows(cada, 0)
    return titulos


def fase_ejecucion() -> int:
    if not FOTO_ANTES.is_file():
        print("✗ falta la foto `antes`", flush=True)
        return 2
    exe = ES_DIR / "Tlamatini-Spanish.exe"
    antes_puertos = escuchando()
    revisar("el inglés está corriendo en 8000 con C:\\Tlamatini\\Tlamatini.exe",
            antes_puertos.get(8000, (0, ""))[1].lower() == str(EN_DIR / "Tlamatini.exe").lower(), str(antes_puertos.get(8000)))
    lnk = escritorio() / "Tlamatini-Spanish.lnk"
    # Otras consolas (p. ej. la del build) pueden llevar ya ese título: cuenta sólo las NUEVAS.
    ventanas_previas = ventanas_con_titulo("Tlamatini")  # incluye las de "Tlamatini-Spanish"
    print(f"Arrancando Tlamatini-Spanish por su acceso directo: {lnk}", flush=True)
    os.startfile(str(lnk))  # noqa: S606 — el mismo clic que haría Angela
    limite = time.monotonic() + 240
    while time.monotonic() < limite:
        p = escuchando()
        if all(x in p for x in (8052, 8752, 50052)) and "error" not in estado_flows(8052):
            break
        print(f"  esperando a Tlamatini-Spanish… puertos vistos: {sorted(p)}", flush=True)
        time.sleep(5)
    p = escuchando()
    for puerto in (8052, 8752, 50052):
        revisar(f"Tlamatini-Spanish escucha en {puerto} con su propio programa",
                p.get(puerto, (0, ""))[1].lower() == str(exe).lower(), str(p.get(puerto)))
    for puerto in (8000, 8765, 50051):
        revisar(f"el inglés sigue escuchando en {puerto}",
                p.get(puerto, (0, ""))[1].lower() == str(EN_DIR / "Tlamatini.exe").lower(), str(p.get(puerto)))
    es, en = estado_flows(8052), estado_flows(8000)
    revisar("el endpoint de flows en 8052 responde Tlamatini-Spanish", es.get("application") == "Tlamatini-Spanish", str(es))
    revisar("el endpoint de flows en 8000 sigue respondiendo Tlamatini", en.get("application") == "Tlamatini", str(en))
    revisar("las dos instancias tienen identidad distinta", es.get("instance") and es.get("instance") != en.get("instance"))
    nuevas = {h: t for h, t in ventanas_con_titulo("Tlamatini-Spanish").items() if h not in ventanas_previas}
    revisar("la consola NUEVA de Tlamatini-Spanish lleva su propio título",
            any(t.startswith("Tlamatini-Spanish") for t in nuevas.values()), "; ".join(list(nuevas.values())[:4]))
    revisar("ninguna ventana nueva se llama sólo 'Tlamatini' (eso sería el inglés)",
            not any(t == "Tlamatini" for h, t in ventanas_con_titulo("Tlamatini").items() if h not in ventanas_previas))
    time.sleep(15)  # el arranque publica el descubrimiento y repara su entrada en un hilo aparte
    disc = valores(r"Software\XAIHT\Tlamatini-Spanish") or {}
    revisar("tras arrancar, el descubrimiento sigue apuntando al español",
            str(disc.get("InstallLocation", "")).lower() == str(ES_DIR).lower())
    revisar("tras arrancar, su entrada en Aplicaciones instaladas sigue siendo la suya",
            (valores(UNINSTALL + r"\Tlamatini-Spanish") or {}).get("DisplayName") == "Tlamatini-Spanish")
    revisar("carpeta por usuario propia %LOCALAPPDATA%\\Tlamatini-Spanish",
            (Path(os.environ["LOCALAPPDATA"]) / "Tlamatini-Spanish").is_dir())
    comparar_ingles()
    foto("identidad_ejecucion_las_dos.png")
    subprocess.Popen(["control.exe", "appwiz.cpl"])
    time.sleep(6)
    foto("identidad_panel_de_control.png")
    return guardar("ejecucion")


def guardar(fase: str) -> int:
    fallas = [r for r in resultados if not r["ok"]]
    informe = SALIDA / f"informe_{fase}_{datetime.now():%Y%m%d_%H%M%S}.json"
    informe.write_text(json.dumps({"fase": fase, "revisiones": len(resultados), "fallas": len(fallas),
                                   "resultados": resultados}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n{len(resultados) - len(fallas)}/{len(resultados)} revisiones pasaron. Informe: {informe}", flush=True)
    return 1 if fallas else 0


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    SALIDA.mkdir(parents=True, exist_ok=True)
    fase = sys.argv[1] if len(sys.argv) > 1 else ""
    if fase == "antes":
        return fase_antes()
    if fase == "despues":
        return fase_despues()
    if fase == "ejecucion":
        return fase_ejecucion()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
