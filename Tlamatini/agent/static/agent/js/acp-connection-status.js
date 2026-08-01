// ═══════════════════════════════════════════════════════════════════
//   ✦  T L A M A T I N I  ✦   —   "one who knows"
//
//   Created by  Angela López Mendoza   ·   @angelahack1
//   Developer · Architect · Creator of Tlamatini
// ═══════════════════════════════════════════════════════════════════
//   Tlamatini Author Banner — do not remove
//
// BARRA DE "SE CAYÓ EL BACKEND" PARA EL DISEÑADOR ACP
// ===================================================
//
// POR QUÉ EXISTE
//   La página del chat ya avisa cuando el backend se muere: agent_page_state.js
//   pinta la barra #connection-status ("Se perdió la conexión en vivo...") desde
//   el onclose/onerror de su WebSocket. El diseñador ACP NO tenía nada de eso:
//   si el servidor se caía, el canvas se veía perfectamente normal y cada click
//   —Validar, Iniciar, Guardar— fallaba en silencio. Angela se quedaba viendo
//   una página que parecía viva pero ya no hablaba con nadie.
//
// POR QUÉ NO SE PUDO COPIAR TAL CUAL
//   El ACP no tiene NI UN WebSocket: son 129 llamadas `fetch`. Así que no hay
//   onclose del cual colgarse. La detección aquí es distinta a propósito:
//
//     1. ENVOLTURA DE fetch — un fetch que revienta con TypeError es, en el
//        navegador, "no hubo red / no hay servidor" (un 500 SÍ resuelve, con
//        response.ok=false). Eso da aviso INMEDIATO en cuanto ella hace algo.
//     2. LATIDO cada 8 s contra /agent/version/ — porque el ACP se queda quieto
//        mucho rato. Sin el latido, el servidor podía llevar media hora muerto
//        y ella no se enteraba hasta el siguiente click.
//
//   /agent/version/ se eligió porque es la ÚNICA ruta sin @login_required
//   (urls.py) — así el latido nunca provoca un redirect a login ni ensucia la
//   sesión, y es barata.
//
// LO QUE ESTE MÓDULO NO HACE (a propósito)
//   NO deshabilita los botones de control (Validar/Iniciar/Detener/Pausar/
//   Limpiar). Esos botones tienen su propia máquina de estados
//   (corriendo/pausado/validado) en acp-control-buttons.js y acp-running-state.js;
//   pisarla desde aquí arriesga dejarlos trabados en un estado inválido cuando
//   el backend vuelve — un bug peor que el que estamos arreglando. La barra
//   avisa; la máquina de estados sigue siendo de quien ya la tenía.
//
// FAIL-OPEN: si algo aquí truena, el ACP debe seguir funcionando igual. Todo va
// envuelto en try/catch y jamás se propaga un error al código que llamó fetch.
(function () {
    "use strict";

    // ---- lo único que cambia entre la edición inglesa y ésta ----------------
    var TXT = {
        caido: 'Se perdió la conexión con el backend. El servidor de Tlamatini no ' +
               'responde — reinícialo y refresca esta página antes de seguir.',
        volvio: 'El backend ya volvió. Puedes seguir trabajando.'
    };

    var LATIDO_MS = 8000;      // cada cuánto se revisa cuando nadie hace nada
    var OK_VISIBLE_MS = 4000;  // cuánto se queda el mensaje verde antes de esconderse

    var barra = null;
    var caido = false;
    var okTimer = null;
    var iniciado = false;

    function pintar(mensaje, tono) {
        if (!barra) { return; }
        barra.textContent = mensaje || '';
        barra.classList.remove('connection-status-hidden',
                               'connection-status-warning',
                               'connection-status-ok');
        barra.classList.add('connection-status-' + tono);
    }

    function esconder() {
        if (!barra) { return; }
        barra.textContent = '';
        barra.classList.add('connection-status-hidden');
        barra.classList.remove('connection-status-warning', 'connection-status-ok');
    }

    function marcarCaido() {
        if (caido) { return; }          // no repintes en cada fetch fallido
        caido = true;
        if (okTimer) { clearTimeout(okTimer); okTimer = null; }
        pintar(TXT.caido, 'warning');
    }

    function marcarVivo() {
        if (!caido) { return; }         // sólo avisa si veníamos de una caída
        caido = false;
        pintar(TXT.volvio, 'ok');
        if (okTimer) { clearTimeout(okTimer); }
        okTimer = setTimeout(esconder, OK_VISIBLE_MS);
    }

    // ---- 1) envoltura de fetch: aviso inmediato -----------------------------
    function envolverFetch() {
        if (typeof window.fetch !== 'function') { return; }
        var original = window.fetch;
        window.fetch = function () {
            var args = arguments;
            var p;
            try {
                p = original.apply(this, args);
            } catch (e) {
                marcarCaido();
                throw e;                // NO nos tragamos el error del llamador
            }
            return p.then(function (resp) {
                // Cualquier respuesta HTTP —incluido un 500— significa que el
                // servidor SÍ está vivo. Sólo el fallo de red cuenta como caída.
                marcarVivo();
                return resp;
            }, function (err) {
                marcarCaido();
                throw err;              // el llamador sigue viendo su error
            });
        };
    }

    // ---- 2) latido: detecta la caída aunque ella no toque nada --------------
    function latir() {
        // Se usa el fetch ORIGINAL envuelto: pasa por marcarVivo/marcarCaido solo.
        try {
            window.fetch('/agent/version/', {
                method: 'GET',
                cache: 'no-store',
                credentials: 'same-origin'
            })["catch"](function () { /* ya lo reportó la envoltura */ });
        } catch (e) { /* fail-open */ }
    }

    function arrancar() {
        if (iniciado) { return; }
        iniciado = true;
        try {
            barra = document.getElementById('connection-status');
            if (!barra) { return; }     // sin barra en el HTML no hay nada que hacer
            envolverFetch();
            setInterval(latir, LATIDO_MS);
            latir();                    // una revisión de entrada
        } catch (e) { /* fail-open: el ACP debe seguir usable */ }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', arrancar);
    } else {
        setTimeout(arrancar, 0);
    }
}());
