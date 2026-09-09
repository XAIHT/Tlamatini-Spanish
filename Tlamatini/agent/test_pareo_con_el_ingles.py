# -*- coding: utf-8 -*-
"""Guarda de PAREO con el arbol ingles: que el barrido sea una prueba, no un rito.

Hasta hoy, comprobar si esta edicion seguia pareada con
`C:\\Development\\XAIHT\\Tlamatini` era un barrido a mano. Un barrido a mano se
corre cuando alguien se acuerda, y lo que se comprueba cuando alguien se acuerda
no se comprueba. Esto lo vuelve una prueba dirigida.

QUE SE COMPARA, Y POR QUE ASI:

  * SUPERFICIE, NUNCA BYTES. Los comentarios, docstrings y textos de usuario de
    esta edicion estan en español A PROPOSITO; un diff de bytes saldria rojo en
    cada archivo y dejaria de leerse. Se comparan CONJUNTOS: agents, skills,
    modulos de frontend, keys de `config.json`, launchers `chat_agent_*`, y el
    AST (funciones / clases / constantes MAYUSCULAS) de cada `.py` compartido.

  * LOS RENAMES PAREADOS SE DESCUENTAN. Siete nombres se tradujeron a proposito
    (`take_shot`/`toma_foto`, `prune`/`podar`, ...). Sin descontarlos, la guarda
    reporta los mismos huecos falsos en cada corrida y termina ignorandose
    entera — que es exactamente como muere una guarda.

  * LO QUE SOLO DEBE EXISTIR ALLA SE DECLARA. `test_version_guard` prueba que el
    arbol INGLES no lleva letra de edicion; aqui esa prueba seria falsa. Se
    nombra en `SOLO_DEL_ARBOL_INGLES` con su motivo, no se silencia.

  * EL DESFASE DE MIGRATIONS ES +1, Y ES REAL. Esta edicion lleva la migration
    extra `0191_translate_prompt_catalog_to_spanish`, asi que la inglesa N pares
    con la española N+1. Se comprueba el desfase, no la igualdad.

  * PROCEDENCIA DE LOS HASHES. Un commit citado en los docs de aqui o resuelve
    en este repository, o resuelve en el ingles y lo declara, o no existe en
    ninguno y esta en la lista de huerfanos conocidos con su motivo.

SI EL ARBOL INGLES NO ESTA CLONADO, ESTAS PRUEBAS SE SALTAN. Una guarda que se
pone roja porque falta OTRO repository no informa de nada: entrena a quien la
lee a ignorar el color. Se puede apuntar a otra ruta con la variable de entorno
`TLAMATINI_ARBOL_INGLES`.
"""
import ast
import io
import json
import os
import re
import subprocess
import unittest

AQUI = os.path.dirname(os.path.abspath(__file__))              # .../Tlamatini/agent
RAIZ_ES = os.path.dirname(os.path.dirname(AQUI))               # raiz del repo español
RAIZ_EN = os.environ.get("TLAMATINI_ARBOL_INGLES",
                         r"C:\Development\XAIHT\Tlamatini")

# ── Renames TRADUCIDOS a proposito: ingles -> español. No son huecos. ───────
PAREADOS = {
    "take_shot": "toma_foto",
    "take_screenshot": "tomar_captura",
    "refusal_reason": "por_que_no_se_borra",
    "_silence_the_tests": "_silenciar_las_pruebas",
    "_english_voice": "_voz_inglesa",
    "assert_no_english": "afirma_sin_ingles",
    "_UNTOUCHABLE_DIRECTORIES": "_DIRECTORIOS_INTOCABLES",
    "_await_visible": "_wait_until_visible",
    "back_up": "respaldar",
    "check_newest": "revisar_ultimo",
    "prune": "podar",
    "verify": "verificar",
    "_set_alarm": "_prender_alarma",
    "ALARM_PATH": "ALARMA_PATH",
    # El arbol ingles guarda UNA marca; aqui hay una tupla de marcas. Esta
    # edicion va ADELANTE: una tupla contiene a la marca suelta.
    "READY_MARKER": "READY_MARKERS",
}

# ── Nombres que SOLO deben existir en el arbol ingles, con su motivo ────────
SOLO_DEL_ARBOL_INGLES = {
    "Tlamatini/agent/test_version_guard.py": {
        # Prueban que el arbol INGLES no lleve sufijo de edicion. Aqui la
        # verdad es la contraria: esta edicion DEBE llevar la `s`.
        "EnglishTreeStaysCleanSemverTests",
        "test_no_spanish_edition_suffix_helper",
    },
    "Tlamatini/agent/test_security_assets_carriage.py": {
        # Alla se exige `take_shot`; aqui la prueba esta INVERTIDA a proposito
        # y exige `toma_foto`.
        "test_harness_uses_take_shot_not_toma_foto",
    },
}

# ── Archivos que por diseño no viven en los dos arboles ────────────────────
SOLO_UN_ARBOL = (
    "agents_descriptions.es.md", "/Paper/", "docs/research/", ".claude/memory/",
    ".gemini/", "nepantla", "estado-actual", "tlamatini_app_summary.pdf",
    "_version.py", "db.sqlite3", ".antes_shoter",
    "shoter_shot.py", "shoter_foto.py",
    "test_shoter_takes_screenshots.py", "test_shoter_toma_las_fotos.py",
    "Tlamatini/hoy",          # archivo de 0 bytes, basura del lado ingles
    "/migrations/",           # el desfase +1 tiene su propia prueba
)

# ── Hashes que no resuelven en NINGUN arbol, con su motivo ─────────────────
# No se les cuelga la etiqueta "ingles": no lo son. Existieron y dejaron de
# existir, o nunca fueron un commit.
HUERFANOS_CONOCIDOS = {
    "2fc441d": "Living Canvas v0, revertido a la fuerza (2026-04-29)",
    "0705a9c": "Living Canvas v0, revertido a la fuerza (2026-04-29)",
    "d496cda": "Living Canvas v0, revertido a la fuerza (2026-04-29)",
    "356fb96": "incidente de llaves Kalier 2026-05-22, nunca pusheado",
    "e2af41d": "incidente de llaves Kalier 2026-05-22, nunca pusheado",
    "e99d2b8": "entrada fechada del fix log; el commit ya no existe",
    "abc1234": "valor de ejemplo dentro de un JSON en views.py",
}

_PODAR = {".git", "__pycache__", "node_modules", "dist", ".ruff_cache", "build",
          "staticfiles", "Temp", "Templates", "reports", "pools", "venv",
          ".venv", "site-packages", "ms-playwright", "jre", "python", "Go"}
_EXT_DOC = {".md", ".py", ".txt", ".tex", ".pmt"}
_HASH = re.compile(r"\b([0-9a-f]{7,8}|[0-9a-f]{40})\b")
_CONTEXTO = re.compile(r"commit|HEAD|tag\b|origin/main|rev-parse|rev-list|hash|`[0-9a-f]{7}`", re.I)
_NOTA = re.compile(r"Procedencia de los hashes:|Hash provenance:")
_EN_LINEA = re.compile(r"arbol ingl[e\u00e9]s|\u00e1rbol INGL\u00c9S|English tree|English-tree|rama inglesa", re.I)
_FALSOS = {"deadbeef", "cafebabe", "baadf00d", "0000000", "1234567", "abcdef0"}


def hay_arbol_ingles():
    return os.path.isdir(os.path.join(RAIZ_EN, ".git"))


def _git(repo, *args):
    return subprocess.run(("git", "-C", repo) + args, capture_output=True,
                          text=True, encoding="utf-8", errors="replace").stdout


def _tracked(repo):
    return {ln.strip() for ln in _git(repo, "ls-files").splitlines() if ln.strip()}


def _superficie(ruta):
    """Funciones, clases y constantes MAYUSCULAS de un modulo."""
    try:
        arbol = ast.parse(io.open(ruta, encoding="utf-8", errors="replace").read())
    except (OSError, SyntaxError):
        return None
    nombres = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            nombres.add(nodo.name)
        elif isinstance(nodo, ast.Assign):
            for t in nodo.targets:
                if isinstance(t, ast.Name) and t.id.isupper() and len(t.id) > 2:
                    nombres.add(t.id)
    return nombres


def _excluido(rel):
    return any(m in rel for m in SOLO_UN_ARBOL)


def _dirs(base):
    return {d for d in os.listdir(base)
            if os.path.isdir(os.path.join(base, d))} if os.path.isdir(base) else set()


def _archivos(base, ext):
    return {f for f in os.listdir(base)
            if f.lower().endswith(ext)} if os.path.isdir(base) else set()


def _existen_como_commit(repo, hashes):
    """Resuelve MUCHOS hashes en UNA sola llamada a git.

    Un `cat-file -t` por hash cuesta un proceso cada vez; con sesenta hashes la
    guarda tarda tanto que estorba, y una guarda que estorba se desactiva.
    `--batch-check` los responde todos por una tuberia.
    """
    if not hashes:
        return set()
    entrada = "\n".join(sorted(hashes)) + "\n"
    salida = subprocess.run(("git", "-C", repo, "cat-file", "--batch-check"),
                            input=entrada, capture_output=True, text=True,
                            encoding="utf-8", errors="replace").stdout
    vivos = set()
    for linea, h in zip(salida.splitlines(), sorted(hashes)):
        if " commit " in linea or linea.endswith(" commit"):
            vivos.add(h)
        elif len(linea.split()) >= 2 and linea.split()[1] == "commit":
            vivos.add(h)
    return vivos


def _citas_de_hashes():
    """(hash, ruta relativa, numero de linea, linea, tiene_nota) por cada cita."""
    for base, dirs, arch in os.walk(RAIZ_ES):
        dirs[:] = [d for d in dirs if d not in _PODAR]
        for a in arch:
            if os.path.splitext(a)[1].lower() not in _EXT_DOC:
                continue
            ruta = os.path.join(base, a)
            rel = os.path.relpath(ruta, RAIZ_ES).replace("\\", "/")
            try:
                texto = io.open(ruta, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            tiene_nota = bool(_NOTA.search(texto))
            todas = texto.splitlines()
            for i, ln in enumerate(todas, 1):
                if not _CONTEXTO.search(ln):
                    continue
                anterior = todas[i - 2] if i >= 2 else ""
                for h in _HASH.findall(ln):
                    if h in _FALSOS or h.isdigit():
                        continue
                    yield h, rel, i, ln, tiene_nota, anterior


saltar = unittest.skipUnless(
    hay_arbol_ingles(),
    "el arbol ingles no esta clonado en %s (apunta a otro sitio con "
    "TLAMATINI_ARBOL_INGLES); saltar es correcto: la ausencia de OTRO "
    "repository no es un defecto de esta edicion" % RAIZ_EN)


@saltar
class PareoDeSuperficies(unittest.TestCase):
    """Los conjuntos que el usuario puede tocar deben existir en las dos ediciones."""

    def _compara(self, titulo, ingles, espanol):
        faltan = sorted(ingles - espanol)
        self.assertEqual(
            faltan, [],
            "%s: el arbol ingles trae %d que esta edicion no tiene: %s. "
            "Portalos siguiendo NEPANTLA (nombres machine en ingles, prosa en "
            "español) o, si es a proposito, declaralo en SOLO_UN_ARBOL con su "
            "motivo." % (titulo, len(faltan), ", ".join(faltan[:10])))

    def test_los_agent_templates_existen_en_las_dos_ediciones(self):
        # Un agent que exista alla y aqui no, no se puede arrastrar al canvas.
        self._compara(
            "agent templates",
            _dirs(os.path.join(RAIZ_EN, "Tlamatini", "agent", "agents")),
            _dirs(os.path.join(RAIZ_ES, "Tlamatini", "agent", "agents")))

    def test_las_skills_existen_en_las_dos_ediciones(self):
        # Una skill ausente es una capacidad que el LLM no llega a ver.
        self._compara(
            "skills",
            _dirs(os.path.join(RAIZ_EN, "Tlamatini", "agent", "skills_pkg")),
            _dirs(os.path.join(RAIZ_ES, "Tlamatini", "agent", "skills_pkg")))

    def test_el_frontend_existe_en_las_dos_ediciones(self):
        est_en = os.path.join(RAIZ_EN, "Tlamatini", "agent", "static", "agent")
        est_es = os.path.join(RAIZ_ES, "Tlamatini", "agent", "static", "agent")
        self._compara("modulos JS",
                      _archivos(os.path.join(est_en, "js"), ".js"),
                      _archivos(os.path.join(est_es, "js"), ".js"))
        self._compara("hojas CSS",
                      _archivos(os.path.join(est_en, "css"), ".css"),
                      _archivos(os.path.join(est_es, "css"), ".css"))
        self._compara("templates HTML",
                      _archivos(os.path.join(RAIZ_EN, "Tlamatini", "agent", "templates", "agent"), ".html"),
                      _archivos(os.path.join(RAIZ_ES, "Tlamatini", "agent", "templates", "agent"), ".html"))

    def test_las_keys_de_config_json_existen_en_las_dos_ediciones(self):
        # Una key que falte aqui no da error: se convierte en un default
        # silencioso, que es la peor forma de perder una opcion.
        def keys(base):
            p = os.path.join(base, "Tlamatini", "agent", "config.json")
            return set(json.load(io.open(p, encoding="utf-8-sig")).keys())
        self._compara("keys de config.json", keys(RAIZ_EN), keys(RAIZ_ES))

    def test_los_launchers_chat_agent_existen_en_las_dos_ediciones(self):
        # El `tool_name` es superficie machine: es identico en las dos ediciones.
        def launchers(base):
            p = os.path.join(base, "Tlamatini", "agent", "chat_agent_registry.py")
            return set(re.findall(r'tool_name\s*=\s*"([^"]+)"',
                                  io.open(p, encoding="utf-8", errors="replace").read()))
        self._compara("launchers chat_agent_*", launchers(RAIZ_EN), launchers(RAIZ_ES))


@saltar
class DesfaseDeMigrations(unittest.TestCase):
    """El desfase es +1 y es real: aqui vive una migration que alla no existe."""

    def _nombres(self, base):
        d = os.path.join(base, "Tlamatini", "agent", "migrations")
        return sorted(f for f in os.listdir(d) if f.endswith(".py") and f != "__init__.py")

    def test_esta_edicion_lleva_exactamente_una_migration_mas(self):
        ingles, espanol = self._nombres(RAIZ_EN), self._nombres(RAIZ_ES)
        self.assertEqual(
            len(espanol) - len(ingles), 1,
            "el desfase de migrations dejo de ser +1 (ingles=%d, español=%d). "
            "Esta edicion lleva la migration extra "
            "`0191_translate_prompt_catalog_to_spanish`; si el numero cambio, "
            "una de las dos ediciones gano o perdio una migration sin pareja."
            % (len(ingles), len(espanol)))

    def test_cada_migration_inglesa_tiene_su_pareja_desplazada_uno(self):
        ingles, espanol = self._nombres(RAIZ_EN), self._nombres(RAIZ_ES)
        # El desfase empieza en 0191; antes de eso los numeros coinciden.
        sin_pareja = []
        por_sufijo_es = {f.split("_", 1)[1]: f for f in espanol if "_" in f}
        for f in ingles:
            if "_" not in f:
                continue
            numero, sufijo = f.split("_", 1)
            if sufijo not in por_sufijo_es:
                sin_pareja.append(f)
                continue
            if int(numero) >= 191:
                esperado = "%04d_%s" % (int(numero) + 1, sufijo)
                self.assertEqual(
                    por_sufijo_es[sufijo], esperado,
                    "la migration inglesa `%s` deberia parear con `%s` aqui, "
                    "pero pareo con `%s`." % (f, esperado, por_sufijo_es[sufijo]))
        self.assertEqual(
            sin_pareja, [],
            "estas migrations inglesas no tienen pareja aqui: %s. Portalas con "
            "el numero desplazado +1." % ", ".join(sin_pareja))


@saltar
class SuperficieEjecutableDeCadaModulo(unittest.TestCase):
    """La prosa puede diferir; lo que se ejecuta, no."""

    def test_ningun_modulo_perdio_funciones_o_clases_del_arbol_ingles(self):
        compartidos = sorted(f for f in (_tracked(RAIZ_EN) & _tracked(RAIZ_ES))
                             if f.endswith(".py") and not _excluido(f))
        self.assertGreater(
            len(compartidos), 100,
            "se compararon solo %d modulos; el barrido no esta viendo el arbol "
            "ingles y estaria pasando por vacio" % len(compartidos))
        huecos = {}
        for rel in compartidos:
            a = _superficie(os.path.join(RAIZ_EN, rel.replace("/", os.sep)))
            b = _superficie(os.path.join(RAIZ_ES, rel.replace("/", os.sep)))
            if a is None or b is None:
                continue
            b_ext = set(b)
            for ing, esp in PAREADOS.items():
                if esp in b:
                    b_ext.add(ing)
            faltan = a - b_ext - SOLO_DEL_ARBOL_INGLES.get(rel, set())
            if faltan:
                huecos[rel] = sorted(faltan)
        self.assertEqual(
            huecos, {},
            "estos modulos perdieron superficie del arbol ingles: %s. Si el "
            "nombre se tradujo, declaralo en PAREADOS; si solo debe existir "
            "alla, declaralo en SOLO_DEL_ARBOL_INGLES con su motivo; si es un "
            "hueco de verdad, portalo." % json.dumps(huecos, ensure_ascii=False))


@saltar
class CarriageDeLasSkillsDeCodex(unittest.TestCase):
    """Regresion del 2026-09-08: existian en disco pero no llegaban a un clone."""

    def test_las_skills_de_codex_estan_trackeadas_como_en_el_arbol_ingles(self):
        # `.gitignore` se tragaba `.codex` entero, asi que las dos skills de
        # dossier estaban adaptadas aqui y aun asi no viajaban. Estar en disco
        # no es estar entregado.
        alla = {f for f in _tracked(RAIZ_EN) if f.startswith(".codex/")}
        aqui = {f for f in _tracked(RAIZ_ES) if f.startswith(".codex/")}
        self.assertEqual(
            sorted(alla - aqui), [],
            "el arbol ingles trackea skills de `.codex/` que aqui no viajan: "
            "%s. Revisa que `.gitignore` conserve `!.codex/skills/`."
            % sorted(alla - aqui))


@saltar
class ProcedenciaDeLosHashes(unittest.TestCase):
    """Un hash citado o resuelve aqui, o declara que es ingles, o es huerfano conocido."""

    @classmethod
    def setUpClass(cls):
        cls.citas = list(_citas_de_hashes())
        todos = {h for h, *_ in cls.citas}
        cls.aqui = _existen_como_commit(RAIZ_ES, todos)
        cls.alla = _existen_como_commit(RAIZ_EN, todos - cls.aqui)

    def test_toda_cita_de_un_hash_ingles_declara_su_procedencia(self):
        sin_declarar = []
        for h, rel, i, ln, tiene_nota, anterior in self.citas:
            if h in self.aqui or h not in self.alla:
                continue
            if tiene_nota or _EN_LINEA.search(ln) or _EN_LINEA.search(anterior):
                continue
            sin_declarar.append("%s:%d (%s)" % (rel, i, h))
        self.assertEqual(
            sin_declarar, [],
            "estas citas son commits del arbol ingles y no lo dicen: %s. "
            "CLAUDE.md pide no citar hashes ingleses sin declararlos, porque no "
            "resuelven aqui: pon la nota de procedencia en el archivo o anota "
            "la linea." % ", ".join(sin_declarar[:12]))

    def test_ningun_hash_citado_es_inventado(self):
        huerfanos = {}
        for h, rel, i, _ln, _n, _a in self.citas:
            if h in self.aqui or h in self.alla or h in HUERFANOS_CONOCIDOS:
                continue
            huerfanos.setdefault(h, "%s:%d" % (rel, i))
        self.assertEqual(
            huerfanos, {},
            "estos hashes no existen en NINGUN arbol: %s. Un hash inventado es "
            "peor que uno viejo: manda a quien lo lee a un objeto que nunca se "
            "escribio. Sale de reemplazar un hash como substring — un hash "
            "corto es el PREFIJO del largo. Leelo de git, o declaralo en "
            "HUERFANOS_CONOCIDOS con su motivo."
            % json.dumps(huerfanos, ensure_ascii=False))


# ── Tokens que el ingles usa y aqui no aparecen, YA REVISADOS uno por uno ──
# Cada uno se abrio y se confirmo que es traduccion o reestructuracion, no un
# hueco. Se declaran con su motivo en vez de aflojar el detector: una lista con
# razones se puede volver a juzgar; un detector aflojado no.
TOLERADOS = {
    "backup_db.py": {
        # El modulo entero esta traducido: verify->verificar, prune->podar,
        # back_up->respaldar, y con ellos sus variables locales.
        ".fromtimestamp", ".items", "ALARM_PATH", "age_days", "counts",
        "files", "newest", "state", "verified",
    },
    "Tlamatini/agent/consumers.py": {
        # Esta edicion va ADELANTE: usa constants.MSG_OVERSIZED_DOCS_WARNING
        # donde el ingles todavia incrusta la frase inglesa en la linea.
        "detected_oversized_docs_warning", "fallback_llm_response",
    },
    "Tlamatini/agent/doc_generation/complete_project_docs.py": {
        ".search",    # regex del ingles para su propia numeracion v1.50.x
        "auto_fit",   # kwarg de una llamada que aqui esta reestructurada
    },
    ".claude/skills/tlamatini-daily-chat-test/harness/run_test.py": {
        # Las marcas viven en el modulo de constantes del harness español.
        "BUSY_MARKERS", "NOT_READY_MARKERS",
    },
    "Tlamatini/agent/test_watchdog_foreground_exemption.py": {
        "._await_visible",  # aqui se llama _wait_until_visible
        ".monotonic",       # el reloj se toma en otro punto de la funcion
    },
    "Tlamatini/agent/test_deleter_safety.py": {".refusal_reason"},   # -> por_que_no_se_borra
    "Tlamatini/agent/agents/kuberneter/kuberneter.py": {".lower"},
    "Tlamatini/agent/rag/interaction.py": {".lower"},
    "Tlamatini/agent/test_version_guard.py": {".read_text"},
}

# Un token machine es lo que NEPANTLA nunca traduce. El `enum` EXIGE guion bajo:
# sin eso, cualquier palabra inglesa en MAYUSCULAS dentro de prosa traducida
# ("REFUSING", "PASSED") se reportaba, y una guarda que grita por prosa se
# desactiva. Con el guion bajo: 66 falsos -> 21 revisados.
_TOKEN = re.compile(
    r'(?P<kw>\b[a-z_][a-z0-9_]{4,}\s*=(?!=))'
    r'|(?P<key>["\'][a-z_][a-z0-9_]{4,}["\']\s*:)'
    r'|(?P<enum>\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b)'
    r'|(?P<attr>\.[a-z_][a-z0-9_]{4,}\()')

_TOKEN_RUIDO = {
    "logger", "config", "result", "status", "return", "import", "except",
    "continue", "string", "number", "object", "boolean", "properties", "value",
    "field", "target", "source", "output", "input", "params", "timeout",
    "content", "message", "encoding", "errors", "utf-8", "default",
}


def _lineas_de_codigo(ruta):
    """Codigo sin docstrings: aqui la prosa esta en español a proposito."""
    try:
        src = io.open(ruta, encoding="utf-8", errors="replace").read()
    except OSError:
        return None, ""
    try:
        arbol = ast.parse(src)
    except SyntaxError:
        return None, src
    doc = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            d = ast.get_docstring(nodo, clean=False)
            if d and nodo.body and isinstance(nodo.body[0], ast.Expr):
                e = nodo.body[0]
                for i in range(e.lineno, (e.end_lineno or e.lineno) + 1):
                    doc.add(i)
    fuera = []
    for i, linea in enumerate(src.splitlines(), 1):
        if i in doc:
            continue
        s = linea.split("#", 1)[0].strip()
        if s:
            fuera.append(s)
    return fuera, src


@saltar
class HuecosDentroDeUnaFuncion(unittest.TestCase):
    """El hueco que un diff de NOMBRES no puede ver.

    Las cinco capacidades que faltaban el 2026-09-09 vivian DENTRO de funciones
    cuyo nombre coincidia en los dos arboles, asi que la comparacion de
    conjuntos daba vacia por construccion. Preguntar "¿existen los mismos
    simbolos?" no dice nada sobre el cuerpo.

    La pregunta que si sirve: ¿hay algun TOKEN MACHINE — una key de config, un
    parametro de API, un campo de schema, un enum — que el ingles use y que
    aqui no aparezca EN NINGUNA PARTE del archivo? No "escrito distinto":
    ausente. Eso es un hueco; lo demas es traduccion y portarlo seria la
    regresion.
    """

    def test_ningun_token_machine_del_ingles_falta_sin_declarar(self):
        compartidos = sorted(f for f in (_tracked(RAIZ_EN) & _tracked(RAIZ_ES))
                             if f.endswith(".py") and not _excluido(f))
        self.assertGreater(len(compartidos), 100,
                           "solo %d modulos comparados: el barrido no esta viendo "
                           "el arbol ingles" % len(compartidos))

        hallazgos, ilegibles = {}, []
        for rel in compartidos:
            ingles, _ = _lineas_de_codigo(os.path.join(RAIZ_EN, rel.replace("/", os.sep)))
            espanol, fuente_es = _lineas_de_codigo(os.path.join(RAIZ_ES, rel.replace("/", os.sep)))
            if espanol is None:
                # Un modulo que no parsea desaparecia de la comparacion en
                # silencio: la guarda salia verde porque no MIRO el archivo, no
                # porque estuviera bien. Un archivo ilegible es un fallo, no un
                # `continue`.
                ilegibles.append(rel)
                continue
            if ingles is None:
                continue
            ya_estan = set(espanol)
            perdonados = TOLERADOS.get(rel, set())
            faltan = set()
            for linea in ingles:
                if linea in ya_estan:
                    continue
                for m in _TOKEN.finditer(linea):
                    tok = (m.group("kw") or m.group("key") or m.group("enum")
                           or m.group("attr") or "").strip().strip("=:(").strip("\"'").strip()
                    if not tok or tok in _TOKEN_RUIDO or tok.isdigit():
                        continue
                    if tok in perdonados or tok in PAREADOS:
                        continue
                    # LA PRUEBA: no aparece en NINGUNA parte del archivo español.
                    if tok not in fuente_es:
                        faltan.add(tok)
            if faltan:
                hallazgos[rel] = sorted(faltan)

        self.assertEqual(
            ilegibles, [],
            "estos modulos de ESTA edicion no parsean, asi que quedaron FUERA "
            "de la comparacion: %s. Verde aqui no significaria 'pareado', "
            "significaria 'ni siquiera lo mire'. Arregla la sintaxis."
            % ", ".join(ilegibles))

        self.assertEqual(
            hallazgos, {},
            "el arbol ingles usa estos tokens machine y aqui no existen en "
            "ningun lado: %s.\n\nUn token machine (key de config, parametro, "
            "campo de schema, enum) NO se traduce, asi que su ausencia total "
            "significa que la capacidad no esta — aunque la funcion que la "
            "contiene si exista con el mismo nombre. Asi se escondieron las "
            "cinco de 2026-09-09: PDFer ignorando el modelo configurado, "
            "acp_doctor sin `deep`, el tool de PDFer sin `nuance`, `images_used` "
            "contando intenciones y build.py sin la asercion CPU-only.\n\n"
            "Abre cada uno. Si es traduccion, declaralo en TOLERADOS con su "
            "motivo; si es un rename, en PAREADOS; si es un hueco, portalo."
            % json.dumps(hallazgos, ensure_ascii=False, indent=1))


class LaGuardaSeExplicaSola(unittest.TestCase):
    """Esta corre SIEMPRE, aunque no haya arbol ingles."""

    def test_cada_huerfano_conocido_trae_su_motivo(self):
        # Una lista de excepciones sin motivo se convierte en un basurero donde
        # se tira todo lo que molesta.
        for h, motivo in HUERFANOS_CONOCIDOS.items():
            self.assertGreater(
                len(motivo), 20,
                "el huerfano `%s` esta perdonado sin explicar por que; escribe "
                "el motivo o quitalo de la lista" % h)

    def test_cada_excepcion_del_arbol_ingles_esta_acotada_a_un_archivo(self):
        for rel, nombres in SOLO_DEL_ARBOL_INGLES.items():
            self.assertTrue(
                rel.endswith(".py"),
                "SOLO_DEL_ARBOL_INGLES se declara por ARCHIVO, no en general: "
                "`%s` no es un modulo" % rel)
            self.assertTrue(nombres, "la excepcion de `%s` esta vacia" % rel)
