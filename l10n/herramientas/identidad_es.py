# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "la que sabe"
#
#   Creado por  Angela López Mendoza   ·   @angelahack1
#   Desarrolladora · Arquitecta · Creadora de Tlamatini
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — no se quita (el nombre de Angela va en cada build)
"""Identidad de sistema operativo de Tlamatini-Spanish (decisión de Angela, 2026-10-25).

Tlamatini-Spanish tiene que instalarse en la MISMA máquina que Tlamatini (inglés),
100 % independiente: otra carpeta, otro programa, otra entrada en Aplicaciones
instaladas, otras llaves de registro, otros ProgIDs, otros accesos directos, otras
carpetas por usuario, otros mutex y otros puertos. Este script declara TODAS esas
adaptaciones como marcas `"codigo"` en la memoria de traducción (la única forma
permitida de cambiar código, GUIA_DE_PORTEO §5), así que sobreviven a cada
sincronización con una versión nueva del inglés:

    python l10n/herramientas/identidad_es.py            # memoriza las decisiones
    python l10n/portar.py aplicar
    python l10n/portar.py verificar

Lo que cambia (inglés → español):
  carpeta de instalación   <padre>\\Tlamatini          → <padre>\\Tlamatini-Spanish
  programa                 Tlamatini.exe               → Tlamatini-Spanish.exe
  Aplicaciones instaladas  Uninstall\\Tlamatini         → Uninstall\\Tlamatini-Spanish
  descubrimiento           Software\\XAIHT\\Tlamatini    → Software\\XAIHT\\Tlamatini-Spanish
  flows (.flw / .fpmt)     Tlamatini.FlowFile …        → TlamatiniSpanish.FlowFile …
                           Software\\Tlamatini\\…        → Software\\Tlamatini-Spanish\\…
                           RegisteredApplications\\TlamatiniFlows → TlamatiniSpanishFlows
  accesos directos         Tlamatini.lnk               → Tlamatini-Spanish.lnk
  por usuario              %LOCALAPPDATA%\\Tlamatini\\…  → %LOCALAPPDATA%\\Tlamatini-Spanish\\…
  mutex / AUMID            XAIHT.Tlamatini.*           → XAIHT.TlamatiniSpanish.*
  puertos                  8000 / 8765 / 50051         → 8052 / 8752 / 50052
  actualizaciones          XAIHT/Tlamatini             → XAIHT/Tlamatini-Spanish
  release                  Tlamatini_Release_v*        → Tlamatini-Spanish_Release_v*

La persona del chat sigue llamándose Tlamatini: sólo cambia lo que ve el sistema
operativo (y las ventanas del instalador/desinstalador que lo muestran).
"""
import base64
import json
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
L10N = AQUI.parent
RAIZ = L10N.parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(L10N))

from memorizar import memorizar  # noqa: E402
from memoria import cargar_memoria  # noqa: E402

PRODUCTO = "Tlamatini-Spanish"
PUERTO_WEB, PUERTO_METRICAS, PUERTO_ARCHIVOS = 8052, 8752, 50052

M_CARPETA = "Identidad de Tlamatini-Spanish: su carpeta de instalación propia, junto a la de Tlamatini (inglés)"
M_EXE = "Identidad de Tlamatini-Spanish: su programa se llama Tlamatini-Spanish.exe, no Tlamatini.exe"
M_ARP = "Identidad de Tlamatini-Spanish: su entrada propia en Aplicaciones instaladas (HKCU Uninstall)"
M_DESC = "Identidad de Tlamatini-Spanish: su llave de descubrimiento propia (HKCU Software\\XAIHT\\Tlamatini-Spanish)"
M_FLOWS = "Identidad de Tlamatini-Spanish: sus ProgIDs y capacidades de .flw/.fpmt propios; no toca los del inglés"
M_LNK = "Identidad de Tlamatini-Spanish: su acceso directo propio (Tlamatini-Spanish.lnk)"
M_USUARIO = "Identidad de Tlamatini-Spanish: sus carpetas por usuario propias (%LOCALAPPDATA%\\Tlamatini-Spanish)"
M_MUTEX = "Identidad de Tlamatini-Spanish: sus mutex, AppUserModelID y título de consola propios"
M_PUERTO = "Identidad de Tlamatini-Spanish: puertos propios (8052 web, 8752 System-Metrics, 50052 Files-Search) para correr al mismo tiempo que el inglés"
M_UPDATE = "Identidad de Tlamatini-Spanish: se actualiza desde XAIHT/Tlamatini-Spanish y su release se llama Tlamatini-Spanish_Release_v*"
M_VERSION = "Identidad de Tlamatini-Spanish: VERSIONINFO del .exe (ProductName, FileDescription, OriginalFilename)"

EXE = ("Tlamatini.exe", "Tlamatini-Spanish.exe", M_EXE)
EXE_MIN = ("'tlamatini.exe'", "'tlamatini-spanish.exe'", M_EXE)
LNK = ("Tlamatini.lnk", "Tlamatini-Spanish.lnk", M_LNK)
ARP = ("CurrentVersion\\Uninstall\\Tlamatini\"", "CurrentVersion\\Uninstall\\Tlamatini-Spanish\"", M_ARP)
DESC_PY = ("XAIHT\\Tlamatini\"", "XAIHT\\Tlamatini-Spanish\"", M_DESC)
DESC_PS = ("XAIHT\\Tlamatini'", "XAIHT\\Tlamatini-Spanish'", M_DESC)
PROG_FLW = ("Tlamatini.FlowFile", "TlamatiniSpanish.FlowFile", M_FLOWS)
PROG_FPMT = ("Tlamatini.PromptFlowFile", "TlamatiniSpanish.PromptFlowFile", M_FLOWS)
CAPS = ("\\Tlamatini\\FlowCapabilities", "\\Tlamatini-Spanish\\FlowCapabilities", M_FLOWS)
TIPOS = ("\\Tlamatini\\FileTypes", "\\Tlamatini-Spanish\\FileTypes", M_FLOWS)


def _usuario(en):
    """Una carpeta por usuario: `"Tlamatini"` → `"Tlamatini-Spanish"` dentro del join dado."""
    return (en, en.replace("Tlamatini", PRODUCTO, 1), M_USUARIO)


CODIGO = {
    # ── instalador / desinstalador / ventanas de setup ──────────────────────────
    "install.py": [
        ('os.path.join(raw, "Tlamatini")', 'os.path.join(raw, "Tlamatini-Spanish")', M_CARPETA),
        EXE, LNK, ARP,
        ('winreg.REG_SZ, "Tlamatini")', 'winreg.REG_SZ, "Tlamatini-Spanish")', M_ARP),
        ('"https://github.com/XAIHT/Tlamatini")', '"https://github.com/XAIHT/Tlamatini-Spanish")', M_ARP),
        ('r"Software\\XAIHT\\Tlamatini"', 'r"Software\\XAIHT\\Tlamatini-Spanish"', M_DESC),
    ],
    "setup_wizard.py": [
        ('os.path.join(raw, "Tlamatini") if raw', 'os.path.join(raw, "Tlamatini-Spanish") if raw', M_CARPETA),
        ('text="TLAMATINI", font=', 'text="TLAMATINI-SPANISH", font=', M_CARPETA),
        # El título de la ventana mientras avanza (sin traducción propia: sólo nombre y marcadores).
        ('f"Tlamatini — {self._working_label}', 'f"Tlamatini-Spanish — {self._working_label}', M_CARPETA),
    ],
    "uninstall.py": [
        ('STAGING_PREFIX = "Tlamatini-Uninstaller-"', 'STAGING_PREFIX = "Tlamatini-Spanish-Uninstaller-"', M_CARPETA),
        PROG_FLW, PROG_FPMT, EXE, EXE_MIN, ARP,
        ('"product": "Tlamatini",', '"product": "Tlamatini-Spanish",', M_DESC),
    ],
    "uninstall_processes.py": [EXE],
    "setup_windows.py": [
        PROG_FLW, PROG_FPMT, CAPS, TIPOS, ARP, DESC_PY, LNK,
        ('"TlamatiniFlows")', '"TlamatiniSpanishFlows")', M_FLOWS),
    ],
    "setup_recovery.py": [
        ('"Local\\\\XAIHT.Tlamatini.Setup.v1"', '"Local\\\\XAIHT.TlamatiniSpanish.Setup.v1"', M_MUTEX),
        LNK,
    ],
    "setup_logging.py": [
        ARP, PROG_FLW,
        ('/ "Tlamatini/SetupLogs"', '/ "Tlamatini-Spanish/SetupLogs"', M_USUARIO),
        ('f"Tlamatini {operation}', 'f"Tlamatini-Spanish {operation}', M_MUTEX),
    ],
    "CreateShortcut.ps1": [EXE, LNK, ('"D:\\\\Tlamatini" }', '"D:\\\\Tlamatini-Spanish" }', M_CARPETA)],
    "RemoveShortcut.ps1": [LNK],
    "Tlamatini.ps1": [EXE],
    "apply_update.ps1": [EXE],
    "flow_file_associations.ps1": [
        ("XAIHT\\\\Tlamatini\\\\FileAssociationTests", "XAIHT\\\\Tlamatini-Spanish\\\\FileAssociationTests", M_FLOWS),
        CAPS, TIPOS, PROG_FLW, PROG_FPMT, EXE,
        ("Name = 'Tlamatini Agent Flow'", "Name = 'Flow de agents de Tlamatini-Spanish'", M_FLOWS),
        ("Name = 'Tlamatini Prompting Flow'", "Name = 'Flow de prompts de Tlamatini-Spanish'", M_FLOWS),
        ("registeredAppUser=TlamatiniFlows", "registeredAppUser=TlamatiniSpanishFlows", M_FLOWS),
        ("'FriendlyAppName' 'Tlamatini'", "'FriendlyAppName' 'Tlamatini-Spanish'", M_FLOWS),
        ("'ApplicationName' 'Tlamatini'", "'ApplicationName' 'Tlamatini-Spanish'", M_FLOWS),
        ("'Edit agent flows and prompting flows in Tlamatini.'",
         "'Edita flows de agents y flows de prompts en Tlamatini-Spanish.'", M_FLOWS),
        ("'TlamatiniFlows'", "'TlamatiniSpanishFlows'", M_FLOWS),
    ],
    "scripts/flow_file_associations_test.ps1": [
        ("XAIHT\\Tlamatini\\FileAssociationTests", "XAIHT\\Tlamatini-Spanish\\FileAssociationTests", M_FLOWS),
        CAPS, PROG_FLW, PROG_FPMT, EXE,
        ("'TlamatiniFlows'", "'TlamatiniSpanishFlows'", M_FLOWS),
    ],
    # ── security (scripts opcionales de Angela) ─────────────────────────────────
    "security/tlamatini_whitelist_v2.ps1": [EXE, DESC_PS],
    "security/enable_tlamatini_v2.bat": [EXE, DESC_PS],
    "security/tlamatini_defender.ps1": [
        DESC_PS,
        ('(Join-Path $env:LOCALAPPDATA "Tlamatini")', '(Join-Path $env:LOCALAPPDATA "Tlamatini-Spanish")', M_USUARIO),
    ],
    # ── build y release ─────────────────────────────────────────────────────────
    "build.py": [
        ('product_name="Tlamatini",', 'product_name="Tlamatini-Spanish",', M_VERSION),
        EXE,
        ('else "Tlamatini")', 'else "Tlamatini-Spanish")', M_EXE),
    ],
    "build_runtime_assets.py": [
        ('"tlamatini.exe",', '"tlamatini-spanish.exe",', M_EXE),
        EXE,
    ],
    "build_installer.py": [
        ('product_name="Tlamatini Installer",', 'product_name="Tlamatini-Spanish Installer",', M_VERSION),
        ('f"Tlamatini_Release_v{safe_version}"', 'f"Tlamatini-Spanish_Release_v{safe_version}"', M_UPDATE),
    ],
    "build_uninstaller.py": [
        ('product_name="Tlamatini Uninstaller",', 'product_name="Tlamatini-Spanish Uninstaller",', M_VERSION),
    ],
    "build_complete_private_release.py": [
        ('"Tlamatini_Release_v*"', '"Tlamatini-Spanish_Release_v*"', M_UPDATE),
        ('/ "Tlamatini" / "contacts.json"', '/ "Tlamatini-Spanish" / "contacts.json"', M_USUARIO),
        ('/ "Tlamatini" / "external_mcps.json"', '/ "Tlamatini-Spanish" / "external_mcps.json"', M_USUARIO),
        ('Path(r"C:\\Tlamatini")', 'Path(r"C:\\XAIHT\\Tlamatini-Spanish")', M_CARPETA),
    ],
    "build_complete_public_release.py": [
        ('"Tlamatini_Release_v*"', '"Tlamatini-Spanish_Release_v*"', M_UPDATE),
    ],
    "versioning.py": [
        ('product_name: str = "Tlamatini",', 'product_name: str = "Tlamatini-Spanish",', M_VERSION),
        EXE,
    ],
    "Tlamatini/agent/version.py": [
        ('product_name: str = "Tlamatini",', 'product_name: str = "Tlamatini-Spanish",', M_VERSION),
        ('file_description: str = "Tlamatini —', 'file_description: str = "Tlamatini-Spanish —', M_VERSION),
        ('internal_name: str = "Tlamatini",', 'internal_name: str = "Tlamatini-Spanish",', M_VERSION),
        EXE,
    ],
    # ── la aplicación ───────────────────────────────────────────────────────────
    "Tlamatini/manage.py": [
        ('SetConsoleTitleW("Tlamatini")', 'SetConsoleTitleW("Tlamatini-Spanish")', M_MUTEX),
        ('"XAIHT.Tlamatini.Server"', '"XAIHT.TlamatiniSpanish.Server"', M_MUTEX),
        ('def _resolve_django_port(default_port: int = 8000)',
         f'def _resolve_django_port(default_port: int = {PUERTO_WEB})', M_PUERTO),
    ],
    "Tlamatini/agent/config.json": [
        ('"django_port": 8000,', f'"django_port": {PUERTO_WEB},', M_PUERTO),
        ('"mcp_system_server_port": 8765,', f'"mcp_system_server_port": {PUERTO_METRICAS},', M_PUERTO),
        ('"mcp_system_client_uri": "ws://127.0.0.1:8765",',
         f'"mcp_system_client_uri": "ws://127.0.0.1:{PUERTO_METRICAS}",', M_PUERTO),
        ('"mcp_files_search_server_port": 50051,', f'"mcp_files_search_server_port": {PUERTO_ARCHIVOS},', M_PUERTO),
        ('"mcp_files_search_client_uri": "ws://127.0.0.1:50051",',
         f'"mcp_files_search_client_uri": "ws://127.0.0.1:{PUERTO_ARCHIVOS}",', M_PUERTO),
    ],
    "Tlamatini/agent/mcp_system_server.py": [
        ('config.get("mcp_system_server_port", 8765)', f'config.get("mcp_system_server_port", {PUERTO_METRICAS})', M_PUERTO),
    ],
    "Tlamatini/agent/mcp_system_client.py": [
        ('"ws://127.0.0.1:8765")', f'"ws://127.0.0.1:{PUERTO_METRICAS}")', M_PUERTO),
    ],
    "Tlamatini/agent/chain_system_lcel.py": [
        ('"ws://127.0.0.1:8765")', f'"ws://127.0.0.1:{PUERTO_METRICAS}")', M_PUERTO),
    ],
    "Tlamatini/agent/mcp_files_search_server.py": [
        ("CONFIG.get('mcp_files_search_server_port', 50051)",
         f"CONFIG.get('mcp_files_search_server_port', {PUERTO_ARCHIVOS})", M_PUERTO),
    ],
    "Tlamatini/agent/mcp_files_search_client.py": [
        ("config.get('mcp_files_search_server_port', 50051)",
         f"config.get('mcp_files_search_server_port', {PUERTO_ARCHIVOS})", M_PUERTO),
    ],
    "Tlamatini/agent/agents/teletlamatini/config.yaml": [
        ('base_url: "http://127.0.0.1:8000"', f'base_url: "http://127.0.0.1:{PUERTO_WEB}"', M_PUERTO),
    ],
    "Tlamatini/agent/agents/teletlamatini/teletlamatini.py": [
        ("'http://127.0.0.1:8000'", f"'http://127.0.0.1:{PUERTO_WEB}'", M_PUERTO),
    ],
    "Tlamatini/agent/flow_file_open.py": [
        ("profile / 'Tlamatini' / 'FlowFileOpen'", "profile / 'Tlamatini-Spanish' / 'FlowFileOpen'", M_USUARIO),
        ("{'application': 'Tlamatini',", "{'application': 'Tlamatini-Spanish',", M_DESC),
        ("'Local\\\\Tlamatini.FlowFile.'", "'Local\\\\TlamatiniSpanish.FlowFile.'", M_MUTEX),
        (".get('django_port', 8000))", f".get('django_port', {PUERTO_WEB}))", M_PUERTO),
        ("    return 8000\n", f"    return {PUERTO_WEB}\n", M_PUERTO),
    ],
    "Tlamatini/agent/windows_app_registration.py": [
        ('ARP_KEY_NAME = "Tlamatini"', 'ARP_KEY_NAME = "Tlamatini-Spanish"', M_ARP),
        ('DISPLAY_NAME = "Tlamatini"', 'DISPLAY_NAME = "Tlamatini-Spanish"', M_ARP),
        ('ABOUT_URL = "https://github.com/XAIHT/Tlamatini"', 'ABOUT_URL = "https://github.com/XAIHT/Tlamatini-Spanish"', M_ARP),
        EXE,
        ('XAIHT_DISCOVERY_KEY = r"Software\\XAIHT\\Tlamatini"',
         'XAIHT_DISCOVERY_KEY = r"Software\\XAIHT\\Tlamatini-Spanish"', M_DESC),
    ],
    "Tlamatini/agent/self_update.py": [
        ('GITHUB_REPO = "Tlamatini"', 'GITHUB_REPO = "Tlamatini-Spanish"', M_UPDATE),
        ('_USER_AGENT = "Tlamatini-Updater"', '_USER_AGENT = "Tlamatini-Spanish-Updater"', M_UPDATE),
        _usuario('os.path.join(base, "Tlamatini", "updater")'),
        EXE,
    ],
    "Tlamatini/agent/templates/agent/agent_page.html": [
        ('href="https://github.com/XAIHT/Tlamatini/releases"',
         'href="https://github.com/XAIHT/Tlamatini-Spanish/releases"', M_UPDATE),
    ],
    "Tlamatini/agent/prompt.pmt": [EXE],
    # ── carpetas por usuario (%LOCALAPPDATA%\Tlamatini-Spanish\…) ───────────────
    "Tlamatini/agent/runtime_provisioner.py": [_usuario('os.path.join(base, "Tlamatini", "runtimes")')],
    "Tlamatini/agent/model_brain.py": [_usuario('os.path.join(base, "Tlamatini", "model_brain")')],
    "Tlamatini/agent/external_mcp_defaults.py": [_usuario('"Tlamatini", "memory", "memory.json"')],
    "Tlamatini/agent/external_mcps.json": [
        ("AppData\\\\Local\\\\Tlamatini\\\\memory", "AppData\\\\Local\\\\Tlamatini-Spanish\\\\memory", M_USUARIO),
    ],
    "Tlamatini/agent/agents/arduiner/arduiner.py": [_usuario('os.path.join(base, "Tlamatini", "arduino-cli")')],
    "Tlamatini/agent/agents/discoverer/discoverer.py": [_usuario('return os.path.join(base, "Tlamatini")')],
    "Tlamatini/agent/agents/esp32er/esp32er.py": [_usuario('os.path.join(base, "Tlamatini", "platformio")')],
    "Tlamatini/agent/agents/esphomer/esphomer.py": [_usuario('os.path.join(base, "Tlamatini", "esphome-lib")')],
    "Tlamatini/agent/agents/googler/googler_engines.py": [_usuario('os.path.join(base, "Tlamatini", "googler"')],
    "Tlamatini/agent/agents/latexer/latexer.py": [_usuario('return os.path.join(base, "Tlamatini")')],
    "Tlamatini/agent/agents/mcp_doctor/mcp_doctor.py": [_usuario('os.path.join(base, "Tlamatini", "runtimes")')],
    "Tlamatini/agent/agents/netspeed_calculator/netspeed_calculator.py": [_usuario('return os.path.join(base, "Tlamatini")')],
    "Tlamatini/agent/agents/nmapper/nmapper.py": [
        _usuario('return os.path.join(base, "Tlamatini")'),
        _usuario('os.path.join(base, "Tlamatini", "nmap")'),
    ],
    "Tlamatini/agent/agents/stm32er/stm32er.py": [
        _usuario('os.path.join(base, "Tlamatini", "STM32TemplateProjectMCP")'),
        _usuario('os.path.join(base, "Tlamatini", "platformio")'),
    ],
    "Tlamatini/agent/agents/talker/talker.py": [_usuario("os.path.join(base, 'Tlamatini', 'piper')")],
    "Tlamatini/agent/agents/video_analyzer/video_fetch.py": [_usuario("os.path.join(base, 'Tlamatini', 'runtimes')")],
    "Tlamatini/agent/agents/camcorder/camcorder.py": [_usuario('os.path.expanduser("~"), "Tlamatini", "Temp")')],
}

# ── pruebas que fijan la identidad: ahora fijan la de Tlamatini-Spanish ─────────
M_PRUEBA = "Prueba de la identidad de Tlamatini-Spanish: fija los valores propios de esta edición"
_PUERTO = [
    ("_DEFAULT_PORT = 8000", f"_DEFAULT_PORT = {PUERTO_WEB}"),
    ("(default 8000).", f"(default {PUERTO_WEB})."),
    ("def test_shipped_default_is_8000", f"def test_shipped_default_is_{PUERTO_WEB}"),
    ("must stay 8000 —", f"must stay {PUERTO_WEB} —"),
    ("http://127.0.0.1:8000/.", f"http://127.0.0.1:{PUERTO_WEB}/."),
    ("falls_back_to_8000", f"falls_back_to_{PUERTO_WEB}"),
    ("fall_back_to_8000", f"fall_back_to_{PUERTO_WEB}"),
    ("must still boot on 8000.", f"must still boot on {PUERTO_WEB}."),
    ("['manage.py', 'runserver', '8000']", f"['manage.py', 'runserver', '{PUERTO_WEB}']"),
    ("\"'0.0.0.0:8000'\"", f"\"'0.0.0.0:{PUERTO_WEB}'\""),
    ("'\"0.0.0.0:8000\"'", f"'\"0.0.0.0:{PUERTO_WEB}\"'"),
    ("'http://localhost:8000/'", f"'http://localhost:{PUERTO_WEB}/'"),
]
PRUEBAS = {
    "Tlamatini/agent/test_django_port_config.py": _PUERTO,
    "Tlamatini/agent/test_mcp_configured_endpoints.py": [
        ("({}, 'localhost:50051'),", f"({{}}, 'localhost:{PUERTO_ARCHIVOS}'),"),
    ],
    "Tlamatini/agent/test_build_root_assets.py": [EXE[:2]],
    "Tlamatini/agent/test_prompt_flow_panel_carriage.py": [EXE[:2]],
    "Tlamatini/agent/test_createsuperuser_wizard.py": [EXE[:2]],
    "Tlamatini/agent/test_self_update.py": [EXE[:2]],
    "Tlamatini/agent/test_uninstaller_lifecycle.py": [EXE[:2]],
    "Tlamatini/agent/test_model_brain.py": [('"Tlamatini", "model_brain")', '"Tlamatini-Spanish", "model_brain")')],
    "Tlamatini/agent/test_windows_app_registration.py": [
        EXE[:2],
        ('ARP_KEY_NAME, "Tlamatini")', 'ARP_KEY_NAME, "Tlamatini-Spanish")'),
        ('self.assertEqual(name, "Tlamatini")', 'self.assertEqual(name, "Tlamatini-Spanish")'),
    ],
    "Tlamatini/agent/test_agent_manifest.py": [
        ('XAIHT_DISCOVERY_KEY, r"Software\\XAIHT\\Tlamatini")', 'XAIHT_DISCOVERY_KEY, r"Software\\XAIHT\\Tlamatini-Spanish")'),
    ],
}
for _ruta, _pares in PRUEBAS.items():
    CODIGO.setdefault(_ruta, []).extend((en, es, M_PRUEBA) for en, es in _pares)

# Archivos cuyas VENTANAS (textos ya traducidos) nombran el producto ante el sistema
# operativo: el instalador, el desinstalador, el setup wizard, la recuperación, los
# scripts de accesos directos y del launcher, el actualizador y el diálogo de abrir flow.
VENTANAS = (
    "install.py", "uninstall.py", "setup_wizard.py", "setup_recovery.py",
    "CreateShortcut.ps1", "RemoveShortcut.ps1", "Tlamatini.ps1", "apply_update.ps1",
    "Tlamatini/agent/flow_file_open.py",
)
_PALABRA = re.compile(r"(?<![\w\\/.-])Tlamatini(?!\.[A-Za-z])(?![\w\\/-])")
_MAYUS = re.compile(r"(?<![\w-])TLAMATINI(?![\w-])")


def renombrar(texto: str) -> str:
    return _MAYUS.sub("TLAMATINI-SPANISH", _PALABRA.sub(PRODUCTO, texto))


# El wizard de createsuperuser (prompt 1) corre `<raíz>\Tlamatini.exe createsuperuser` en
# modo frozen; su texto final vive en el payload base64 de la migración 0185.
WIZARD_B64 = "Tlamatini/agent/migrations/0185_standardize_prompt_params_batch3.py"


def _marcas(seg):
    return {k: v for k, v in seg.items() if k not in ("en", "es", "n")}


def decisiones_de(archivo: str) -> list[dict]:
    ruta_mem = L10N / "memoria" / (archivo + ".json")
    previas = cargar_memoria(ruta_mem)["segmentos"] if ruta_mem.exists() else []
    decisiones = []
    if archivo in VENTANAS:
        for seg in previas:
            if seg.get("codigo"):
                continue
            nuevo = renombrar(seg["es"])
            if nuevo != seg["es"] or PRODUCTO in nuevo or "TLAMATINI-SPANISH" in nuevo:
                marcas = _marcas(seg)
                # En ESTA ventana «Tlamatini» es el nombre del producto, que aquí es
                # Tlamatini-Spanish: el término no sobrevive tal cual a propósito.
                marcas["libres"] = sorted(set(marcas.get("libres", ())) | {"Tlamatini", "TLAMATINI"})
                decisiones.append({"en": seg["en"], "es": nuevo, **marcas})
    if archivo == WIZARD_B64:
        for seg in previas:
            texto = base64.b64decode(seg["es"].strip('"')).decode("utf-8")
            if "Tlamatini.exe" in texto:
                nuevo = texto.replace("Tlamatini.exe", "Tlamatini-Spanish.exe")
                b64 = base64.b64encode(nuevo.encode("utf-8")).decode("ascii")
                decisiones.append({"en": seg["en"], "es": '"' + b64 + '"', **_marcas(seg)})
    for en, es, motivo in CODIGO.get(archivo, ()):
        decisiones.append({"en": en, "es": es, "codigo": motivo})
    return decisiones


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    import portar  # noqa: E402 — usa la base inglesa anotada
    base = portar.leer_base()
    fallas = 0
    for archivo in sorted(set(CODIGO) | set(VENTANAS) | {WIZARD_B64}):
        decisiones = decisiones_de(archivo)
        if not decisiones:
            print(f"· {archivo}: nada que decidir")
            continue
        try:
            original = portar.original_ingles(base, archivo)
            mem = memorizar(L10N / "memoria", original, archivo, decisiones)
            codigo = sum(1 for s in mem["segmentos"] if s.get("codigo"))
            print(f"✓ {archivo}: {len(decisiones)} decisiones ({codigo} adaptaciones de código)")
        except Exception as exc:  # noqa: BLE001 — se reporta y se sigue
            fallas += 1
            print(f"✗ {archivo}: {exc}")
    return 1 if fallas else 0


if __name__ == "__main__":
    sys.exit(main())
