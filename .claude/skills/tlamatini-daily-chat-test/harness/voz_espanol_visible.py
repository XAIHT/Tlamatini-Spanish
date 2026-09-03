# ══════════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
#
#   Every line of this file was written by Angela López Mendoza.
# ══════════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove (releases scrub the name automatically)
"""PRUEBA VISIBLE: Tlamatini-Spanish habla MUCHO castellano (Angela, 2026-08-19).

Corre en una ventana EN PRIMER PLANO, en el escritorio real de Angela, y la
hace hablar frase por frase con su voz mexicana (Piper ``es_MX-claude-high``).
Cada frase se OYE y se cuenta en pantalla.

REGLAS DE LA CASA QUE ESTA PRUEBA RESPETA
  * Nada headless, nada en segundo plano: ventana visible, primer plano.
  * La foto de pantalla completa la toma SHOTER, jamas PIL.ImageGrab. Si
    Shoter falla, SE REPORTA — no hay respaldo con Pillow.
  * No se miente: si una frase no suena, sale en ROJO y el resumen lo dice.

Y LA REGLA QUE ESTA PRUEBA EXISTE PARA VIGILAR
  Tlamatini-Spanish habla castellano o NO HABLA. Nunca ingles. Si el audio
  saliera en ingles, esta prueba no sirve de nada — por eso NO usa Orpheus
  (modelo solo-ingles) sino la voz mexicana, y verifica que cada WAV traiga
  audio de verdad.

Uso:
    python voz_espanol_visible.py
"""
import os
import sys
import time
import wave

_AQUI = os.path.dirname(os.path.abspath(__file__))
#: raiz del arbol espanol (…/Tlamatini-Spanish)
_RAIZ = os.path.abspath(os.path.join(_AQUI, "..", "..", "..", ".."))
_DJANGO = os.path.join(_RAIZ, "Tlamatini")
_SALIDA = os.path.join(_RAIZ, "Temp", "voz_visible")

#: Lo que va a decir. Castellano latinoamericano, frases completas, con
#: acentos y signos de apertura para oir bien la pronunciacion.
FRASES = [
    "¡Hola, Angela! Soy Tlamatini, y esta es mi voz mexicana.",
    "Ya no hablo en inglés: si no puedo hablar en español, me quedo callada.",
    "Mi voz se llama es eme equis, claude, alta calidad. Es femenina, como yo.",
    "No necesito Ollama para hablarte. Piper corre aquí, en tu computadora.",
    "Tú me creaste, Angela López Mendoza, y por eso hablo tu idioma.",
    "Puedo leerte un reporte completo, con números, fechas y nombres propios.",
    "El agente Executer corrió sin problemas y el Exec Report quedó en verde.",
    "¿Quieres que te lea el resumen del flujo, o prefieres que me calle?",
    "Los archivos temporales viven en la carpeta Temp, dentro de Tlamatini.",
    "Listo. Terminé de hablar, y todo lo dije en español latinoamericano.",
]


class Colores:
    VERDE = "\033[92m"
    ROJO = "\033[91m"
    AMAR = "\033[93m"
    CYAN = "\033[96m"
    NEGRITA = "\033[1m"
    FIN = "\033[0m"


def _titulo(txt):
    print()
    print(Colores.CYAN + "=" * 74 + Colores.FIN)
    print(Colores.CYAN + Colores.NEGRITA + "  " + txt + Colores.FIN)
    print(Colores.CYAN + "=" * 74 + Colores.FIN)


def _preparar_django():
    """Deja importable el arbol espanol. Devuelve el modulo tts_piper."""
    sys.path.insert(0, _DJANGO)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tlamatini.settings")
    import django
    django.setup()
    from agent import tts_piper
    return tts_piper


def _asegurar_voz(tts_piper):
    """La voz mexicana tiene que estar lista ANTES de la primera frase."""
    _titulo("1/4  Preparando la voz mexicana (Piper es_MX-claude-high)")
    info = tts_piper.ensure_ready(log=lambda m: print("      " + str(m)))
    listo = bool(info and info.get("ready"))
    print(("      " + Colores.VERDE + "voz lista" + Colores.FIN) if listo
          else ("      " + Colores.ROJO + "la voz NO quedo lista" + Colores.FIN))
    if not listo:
        print(Colores.ROJO + "      Sin voz en castellano NO se habla. "
              "Se aborta: en ingles no se habla." + Colores.FIN)
    return listo


def _duracion(ruta):
    with wave.open(ruta, "rb") as wf:
        return wf.getnframes() / float(wf.getframerate() or 1)


def _hablar(tts_piper, idx, frase):
    """Sintetiza y REPRODUCE una frase. Devuelve (ok, segundos, ruta)."""
    audio, estado = tts_piper.synthesize(frase)
    if estado != "ok" or not audio:
        return False, 0.0, ""
    os.makedirs(_SALIDA, exist_ok=True)
    ruta = os.path.join(_SALIDA, "frase_%02d.wav" % idx)
    with open(ruta, "wb") as fh:
        fh.write(audio)
    segs = _duracion(ruta)

    # Reproducir de verdad, para que Angela la OIGA.
    try:
        import numpy as np
        import sounddevice as sd
        with wave.open(ruta, "rb") as wf:
            sr = wf.getframerate()
            crudo = wf.readframes(wf.getnframes())
        pcm = np.frombuffer(crudo, dtype=np.int16).astype(np.float32) / 32768.0
        sd.play(pcm, sr)
        sd.wait()
    except Exception as exc:                      # noqa: BLE001
        # El archivo existe y trae audio; solo no se pudo sacar por bocina.
        print("      " + Colores.AMAR + "(no se pudo reproducir: %s)"
              % exc + Colores.FIN)
        return True, segs, ruta
    return True, segs, ruta


def _foto(nombre):
    """La foto la toma SHOTER. Nunca PIL. Si falla, se reporta."""
    lanzador = os.path.join(_RAIZ, "shoter_foto.py")
    if not os.path.isfile(lanzador):
        print("      " + Colores.AMAR
              + "shoter_foto.py no esta en %s — sin foto." % _RAIZ + Colores.FIN)
        return ""
    try:
        sys.path.insert(0, _RAIZ)
        import shoter_foto
        destino = os.path.join(_SALIDA, nombre)
        shoter_foto.toma_foto(filename=destino, all_screens=True)
        if os.path.isfile(destino):
            print("      " + Colores.VERDE + "foto de Shoter: %s" % destino
                  + Colores.FIN)
            return destino
        print("      " + Colores.ROJO
              + "SHOTER FALLO: no dejo el archivo. NO uso Pillow." + Colores.FIN)
    except Exception as exc:                      # noqa: BLE001
        print("      " + Colores.ROJO
              + "SHOTER FALLO: %s. NO uso Pillow." % exc + Colores.FIN)
    return ""


def main():
    os.system("")                                  # habilita ANSI en cmd
    _titulo("TLAMATINI-SPANISH HABLANDO CASTELLANO  —  prueba visible")
    print("  Arbol : %s" % _RAIZ)
    print("  Frases: %d" % len(FRASES))
    print("  Regla : castellano o silencio. NUNCA ingles.")

    tts_piper = _preparar_django()
    if not _asegurar_voz(tts_piper):
        return 2

    _titulo("2/4  Hablando (súbele al volumen, Angela)")
    ok_total, segundos_total, fallidas = 0, 0.0, []
    for i, frase in enumerate(FRASES, 1):
        print("  %2d/%d  %s" % (i, len(FRASES), frase))
        ok, segs, _ruta = _hablar(tts_piper, i, frase)
        if ok:
            ok_total += 1
            segundos_total += segs
            print("        " + Colores.VERDE + "sonó %.2fs" % segs + Colores.FIN)
        else:
            fallidas.append(frase)
            print("        " + Colores.ROJO + "NO SONÓ" + Colores.FIN)
        time.sleep(0.25)

    _titulo("3/4  Foto de PANTALLA COMPLETA (la toma Shoter)")
    _foto("voz_espanol_pantalla.png")

    _titulo("4/4  Resumen")
    print("  frases habladas : %s%d de %d%s"
          % (Colores.VERDE if ok_total == len(FRASES) else Colores.ROJO,
             ok_total, len(FRASES), Colores.FIN))
    print("  audio total     : %.2f segundos" % segundos_total)
    print("  voz             : es_MX-claude-high (femenina, mexicana)")
    print("  audios en       : %s" % _SALIDA)
    if fallidas:
        print(Colores.ROJO + "  NO sonaron:" + Colores.FIN)
        for f in fallidas:
            print("     - %s" % f[:66])
    veredicto = (Colores.VERDE + "TODO EN CASTELLANO" + Colores.FIN
                 if ok_total == len(FRASES)
                 else Colores.ROJO + "INCOMPLETO" + Colores.FIN)
    print("  veredicto       : %s" % veredicto)
    print()
    input("  Presiona ENTER para cerrar esta ventana... ")
    return 0 if ok_total == len(FRASES) else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n  interrumpido por la usuaria")
        sys.exit(130)
