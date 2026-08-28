# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
#
#   Every line of this file was written by Angela López Mendoza.
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove (releases scrub the name automatically)
"""EL CANAL DE MÁQUINA NO SE TRADUCE. NUNCA.

Esta edición habla español: cada línea que la usuaria LEE va en español
latino. En los MISMOS archivos hay un segundo canal que NO es para ella —
lo lee el CÓDIGO — y traducir una sola palabra de ahí rompe el producto en
silencio.

QUÉ SE VIGILA
-------------
1. Las LLAVES del bloque ``INI_SECTION_<TIPO><<< … >>>END_SECTION_<TIPO>``.
   Los agents lo emiten así, en UNA sola llamada::

       logging.info(
           "INI_SECTION_GLOBBER<<<\\n"
           f"pattern: {pattern}\\n"
           f"status: {status}\\n"
           ...
           ">>>END_SECTION_GLOBBER")

   El Parametrizer busca esas llaves POR NOMBRE. Si ``status:`` se vuelve
   ``estado:``, el campo deja de existir y la conexión entre agents se corta
   sin un solo error en pantalla.

2. Los VALORES de ``status``. ``agent_verdict.py`` corre una tabla de reglas
   ORDENADA sobre ellos para pintar SUCCESS/FAILED en el Exec Report, y el
   auto-reporte del agent GANA sobre el exit code. Un valor traducido no casa
   con NINGUNA regla y el renglón queda impredecible.

3. El token ``TLM_VERDICT::PASS_OK`` que un Forker compara para ramificar.

POR QUÉ NO SE DETECTA POR ACENTOS  ⚠️  (el error de la primera versión)
----------------------------------------------------------------------
La primera versión marcaba lo traducido buscando acentos. Es inútil: la
traducción natural de ``refused`` es ``rechazado`` — SIN un solo acento. Una
prueba de mutación lo demostró: se tradujo un ``status:`` real y el guard
siguió en verde. Un guard que no puede fallar es peor que ninguno, porque
invita justo al error que dice prevenir.

Ahora la detección es por LISTA BLANCA, no por forma de la palabra: toda
llave y todo valor literal se compara contra el conjunto conocido. Así cae
``estado`` igual que ``estádo``.

DE DÓNDE SALE EL VOCABULARIO
----------------------------
De ``agent_verdict.py``, importado — NO copiado. ``docs/claude/exec-report.md``
exige UNA sola definición del vocabulario de estatus; una segunda copia aquí
se desincronizaría y este guard aprobaría un valor que el motor real rechaza.

Regla de oro: **si el código lo lee, se queda en inglés.**
"""

import os
import re
import sys
import unittest

_AQUI = os.path.dirname(os.path.abspath(__file__))
_AGENTS = os.path.join(_AQUI, 'agents')
sys.path.insert(0, os.path.dirname(_AQUI))

from agent import agent_verdict as _av  # noqa: E402

#: El vocabulario que el motor reconoce, IMPORTADO de su UNICA definicion.
#:
#: ⚠️ AQUI SE UNIAN SOLO TRES DE LOS CINCO CONJUNTOS. Cuando se escribio
#: esto (2026-08-15) `agent_verdict` tenia tres; el 2026-08-16 crecio a
#: cinco (WORK_COMPLETED y WORK_DEGRADED) y esta prueba no lo siguio. El
#: resultado fue una prueba que reprobaba valores PERFECTAMENTE VALIDOS:
#: netspeed_calculator emite `partial`, que vive en WORK_DEGRADED desde
#: entonces, y aqui salia reportado como desconocido. Un falso positivo en
#: un guard es caro: manda a leer el archivo equivocado.
#:
#: Por eso ahora se toma `KNOWN_STATUSES`, que es la union de los cinco y
#: la UNICA definicion del vocabulario. Si mañana se agrega un sexto
#: conjunto, esta prueba lo hereda sola. Es la misma regla que la casa ya
#: tiene escrita: no se teclea a mano lo que se puede DERIVAR.
STATUS_DEL_MOTOR = frozenset(_av.KNOWN_STATUSES)

#: Lo que los agents emiten hoy y el motor todavia NO conoce.
#:
#: Era una lista de 21 y quedo en UNO. Los otros 20 entraron al vocabulario
#: oficial cuando crecio a cinco conjuntos — incluidos los cuatro que el
#: hallazgo del 2026-08-15 señalo como huecos REALES (`unreachable`,
#: `forward_failed`, `rejected`, `ignored`): los cuatro viven ya en
#: WORK_NOT_DONE_STATUSES, asi que aquel hallazgo se atendio y mantenerlos
#: aqui solo duplicaba la verdad.
#:
#: `ready` (mcp_doctor) sigue afuera. No se agrega desde aqui: como decia
#: la nota original, en que conjunto entra un status es decision de
#: PRODUCTO — de como debe pintarse el renglon —, no de una prueba. Cae a
#: R7/R8 y lo decide el exit code, que para un diagnostico de solo lectura
#: que sale con 0 pinta verde, que es lo correcto.
#:
#: El guard sigue siendo TRINQUETE: cualquier valor fuera de estos dos
#: conjuntos falla — y una traduccion del token es exactamente eso.
STATUS_EMITIDOS_HOY = frozenset({'ready'})

STATUS_VALIDOS = STATUS_DEL_MOTOR | STATUS_EMITIDOS_HOY

#: Llaves que el Parametrizer y el motor leen POR NOMBRE. Si un agent nuevo
#: necesita una llave más, agrégala aquí a propósito — no la traduzcas.
LLAVES_VALIDAS = frozenset({
    'status', 'success', 'ok', 'error', 'errors', 'returncode', 'return_code',
    'exit_code', 'action', 'tool', 'mode', 'engine', 'stage', 'verdict',
    'verdict_token', 'confidence', 'motion_score', 'frames_analyzed',
    'output_path', 'output_dir', 'input_path', 'input_dir', 'filename',
    'file_path', 'project_dir', 'tex_path', 'json_path', 'xml_path',
    'transcript_path', 'audio_path', 'video_path', 'build_path',
    'response_body', 'body', 'url', 'method', 'endpoint', 'subject',
    'server_url', 'base_url', 'target', 'targets', 'pattern', 'path', 'glob',
    'matches', 'files_searched', 'truncated', 'occurrences', 'replacements',
    'findings_count', 'total_findings', 'tools_run', 'tools_skipped',
    'page_count', 'pages', 'bytes', 'passes', 'images_used', 'source_type',
    'device_index', 'device_name', 'camera_index', 'display_index',
    'sample_rate', 'play_sample_rate', 'file_sample_rate', 'channels',
    'duration_seconds', 'file_duration_seconds', 'played_seconds',
    'time_played_requested', 'play_mode', 'loops', 'partial_segment',
    'volume_percent', 'gain_percent', 'clipped_samples', 'resolution', 'fps',
    'media_type', 'format', 'model', 'models', 'language', 'voice', 'gender',
    'emotion', 'audio_seconds', 'char_count', 'word_count', 'segments',
    'played', 'agent_id', 'session_id', 'transport', 'settle', 'backend',
    'board', 'port', 'environment', 'fqbn', 'sketch_path', 'device',
    'config_path', 'name', 'server_key', 'supported', 'catalog_path',
    'runtime', 'pdcp_used', 'hosts_up', 'open_ports', 'npcap_present',
    'scan_technique', 'ports', 'return_message', 'message', 'message_id',
    'channel', 'to', 'matched', 'match_count', 'state', 'left', 'top',
    'width', 'height', 'window_title', 'repo_path', 'diff_ref', 'target_path',
    'distribution', 'warnings', 'bibliography', 'interpreter_model_1',
    'interpreter_model_2', 'merging_model', 'video_width', 'video_height',
    'window_width', 'window_height', 'fullscreen', 'has_audio',
    'display_geometry', 'timed_out', 'return_code_text',
    # Llaves propias de un solo agent, verificadas contra el árbol el
    # 2026-08-15. Cada una es un identificador que el Parametrizer puede
    # direccionar; ninguna se traduce.
    'actions_required', 'agent_count', 'all_screens', 'assert_result',
    'chat_id', 'cipher_text', 'command', 'connection_count', 'contact_status',
    'content_length', 'content_mode', 'crawl_type', 'deciphered_buffer',
    'direction', 'encapsulation', 'extension', 'final_url', 'flow_filename',
    'flw_path', 'git_command', 'host', 'initialization_vector', 'input',
    'input_source', 'label', 'min_severity', 'operation', 'output',
    'parameters', 'passwordless', 'platform', 'private_key', 'public_key',
    'recipient', 'repair_status', 'retry_status', 'source', 'start_url',
    'steps_run', 'target_words', 'telegram_status', 'title',
    'whatsapp_status',
})

#: `"clave: {var}\n"` o `"clave: literal\n"` dentro del bloque emitido.
_LLAVE_EN_BLOQUE = re.compile(r'^\s*f?["\']([A-Za-zÁÉÍÓÚÑáéíóúñ_][\wÀ-ſ]*)\s*:\s')
#: `"status": "<literal>"` en un dict de resultado.
_STATUS_DICT = re.compile(r'["\']status["\']\s*:\s*["\']([^"\']+)["\']')
#: `f"status: literal\n"` — un literal, no una variable.
_STATUS_INLINE = re.compile(r'["\']status:\s+(?!\{)([a-zA-ZÁÉÍÓÚÑáéíóúñ_]+)\\n')
#: `status = "matches"` y `status = "a" if cond else "b"`.
#:
#: ⚠️ Sin esta forma el guard tenía un punto ciego REAL: el bloque emite
#: `f"status: {status}"` — una VARIABLE — así que el valor literal nunca
#: aparece junto a la palabra `status:`. Globber, Grepper y varios más
#: asignan primero (`status = "matches" if matches else "no_matches"`) y
#: sólo interpolan después. Una prueba de mutación lo destapó: se tradujo
#: el valor a `coincidencias` y el guard siguió en verde.
_STATUS_ASIGNADO = re.compile(
    r'^\s*(?:self\.)?status\s*=\s*(.+)$', re.MULTILINE)


def _literales_de_valor(derecha):
    """Los literales que SON el valor, no los que son argumentos.

    La diferencia es la profundidad de paréntesis, y es exacta:

        status = "error" if resp.get("status") == "error" else "ok"
                 ^^^^^^^ valor          ^^^^^^ llave que se consulta

    `"status"` vive DENTRO de la llamada — es lo que se busca en el dict
    ajeno, no lo que este agente declara. Lo mismo pasa con
    `host.find("status")`, `getattr(resp, 'status', 200)`,
    `pisa.CreatePDF(..., encoding="utf-8")` y
    `any(diag.get("blockers") ...)`: los cinco falsos positivos que
    aparecieron la primera vez que se leyeron las asignaciones. Todos
    están a profundidad ≥ 1; todos los valores reales están a 0.
    """
    literales, profundidad, comilla, actual, i = [], 0, '', '', 0
    while i < len(derecha):
        car = derecha[i]
        if comilla:
            if car == '\\':
                i += 2
                continue
            if car == comilla:
                if profundidad == 0 and actual and _NOMBRE.fullmatch(actual):
                    literales.append(actual)
                comilla = ''
            else:
                actual += car
        elif car in '"\'':
            comilla, actual = car, ''
        elif car == '#':
            break            # comentario al final de la línea
        elif car in '([{':
            profundidad += 1
        elif car in ')]}':
            profundidad -= 1
        i += 1
    return literales


#: Un nombre de status: sin espacios, sin rutas, sin formato.
_NOMBRE = re.compile(r'[A-Za-zÁÉÍÓÚÑáéíóúñ_][\w\-]*')
_INI = re.compile(r'INI_SECTION_([A-Za-z0-9_]+)<<<')
_END = re.compile(r'>>>END_SECTION_([A-Za-z0-9_]+)')


def _agentes():
    for entrada in sorted(os.listdir(_AGENTS)):
        if entrada in ('pools', '__pycache__'):
            continue
        ruta = os.path.join(_AGENTS, entrada, entrada + '.py')
        if os.path.isfile(ruta):
            yield entrada, ruta


def _texto(ruta):
    with open(ruta, 'r', encoding='utf-8', errors='replace') as fh:
        return fh.read()


def _bloques(src):
    """Cada bloque INI_SECTION como texto crudo del FUENTE, no ejecutado."""
    fuera = []
    for m in _INI.finditer(src):
        fin = src.find('>>>END_SECTION', m.end())
        if fin != -1:
            fuera.append(src[m.end():fin])
    return fuera


class LlavesDeSeccionTests(unittest.TestCase):
    """Las llaves del bloque son identificadores, no texto."""

    def test_toda_llave_emitida_es_conocida(self):
        malas = []
        for nombre, ruta in _agentes():
            for bloque in _bloques(_texto(ruta)):
                for linea in bloque.splitlines():
                    m = _LLAVE_EN_BLOQUE.match(linea)
                    if not m:
                        continue
                    llave = m.group(1)
                    if llave not in LLAVES_VALIDAS:
                        malas.append('%s -> %s' % (nombre, llave))
        self.assertEqual(
            sorted(set(malas)), [],
            'Llave(s) desconocidas en un bloque INI_SECTION: %s.\n'
            'Si la tradujiste: REVIÉRTELA — el Parametrizer la busca por su '
            'nombre en inglés y traducida el campo deja de existir.\n'
            'Si es una llave NUEVA y legítima: agrégala a LLAVES_VALIDAS a '
            'propósito.' % sorted(set(malas)))

    def test_ini_y_end_empatan_y_son_ascii(self):
        for nombre, ruta in _agentes():
            src = _texto(ruta)
            abre, cierra = set(_INI.findall(src)), set(_END.findall(src))
            for tipo in abre | cierra:
                self.assertTrue(
                    tipo.isascii() and tipo.isupper(),
                    '%s: INI_SECTION_%s debe ser ASCII en MAYÚSCULAS.'
                    % (nombre, tipo))
            self.assertEqual(
                abre ^ cierra, set(),
                '%s: INI_SECTION/END_SECTION desparejados: %s.'
                % (nombre, sorted(abre ^ cierra)))


class ValoresDeStatusTests(unittest.TestCase):
    """`status` lo lee agent_verdict.py, no la usuaria."""

    def test_el_vocabulario_viene_de_agent_verdict(self):
        """Una segunda copia se desincroniza; por eso se importa."""
        self.assertGreaterEqual(len(STATUS_VALIDOS), 30)
        for esperado in ('refused', 'not_found', 'engine_unavailable',
                         'error', 'invalid', 'findings'):
            self.assertIn(esperado, STATUS_VALIDOS,
                          '%s salió del vocabulario de agent_verdict.'
                          % esperado)

    def test_ningun_status_literal_desconocido(self):
        malos = []
        for nombre, ruta in _agentes():
            src = _texto(ruta)
            for valor in _STATUS_DICT.findall(src):
                if '{' in valor or not valor.strip():
                    continue          # una variable, la valida el motor
                if valor.strip().lower() not in STATUS_VALIDOS:
                    malos.append('%s -> "status": "%s"' % (nombre, valor))
            for valor in _STATUS_INLINE.findall(src):
                if valor.strip().lower() not in STATUS_VALIDOS:
                    malos.append('%s -> status: %s' % (nombre, valor))
            # `status = "..."` — la forma que el bloque interpola después.
            for derecha in _STATUS_ASIGNADO.findall(src):
                for valor in _literales_de_valor(derecha):
                    if valor.strip().lower() not in STATUS_VALIDOS:
                        malos.append('%s -> status = "%s"' % (nombre, valor))
        self.assertEqual(
            sorted(set(malos)), [],
            'Valor(es) de status que agent_verdict.py NO reconoce: %s.\n'
            'Traducido => ninguna regla casa y el renglón del Exec Report '
            'queda impredecible. Usa un valor del vocabulario, o agrégalo a '
            'agent_verdict.py a propósito.' % sorted(set(malos)))


class TokensDeVeredictoTests(unittest.TestCase):
    """Los tokens que un Forker compara son literales, no mensajes."""

    def test_el_token_de_video_analyzer_no_cambia(self):
        ruta = os.path.join(_AGENTS, 'video_analyzer', 'video_analyzer.py')
        if not os.path.isfile(ruta):
            self.skipTest('video_analyzer no está en este árbol')
        src = _texto(ruta)
        self.assertIn('TLM_VERDICT::', src,
                      'Desapareció TLM_VERDICT:: — un Forker ramifica '
                      'comparando ese literal.')
        self.assertIn('PASS_OK', src, 'PASS_OK ya no aparece.')
        for token in re.findall(r'TLM_VERDICT::([A-Z_]+)', src):
            if token != 'PASS_OK':
                self.assertNotIn(
                    'PASS_OK', token,
                    'PASS_OK no puede ser substring de %s: una falla podría '
                    'rutear como éxito.' % token)


if __name__ == '__main__':
    unittest.main()
