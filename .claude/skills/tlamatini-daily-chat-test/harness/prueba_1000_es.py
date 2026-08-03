# PROHIBIDO PIL.ImageGrab (Angela, 2026-08-02): las fotos las toma
# SHOTER, el agent de Tlamatini. Ver shoter_foto.py.
from shoter_foto import toma_foto
# -*- coding: utf-8 -*-
# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove
"""
Tlamatini — 1000 preguntas EN ESPAÑOL a través del chat REAL, con evidencia
fotográfica de pantalla completa (todo el escritorio, con el RELOJ visible)
para CADA pregunta.

Angela's rules this runner obeys, without exception:
  * HEADED, real Chrome, on her real desktop. Never headless (run_test.py
    hard-refuses --headless anyway).
  * One FULL-SCREEN photo per test, taskbar clock visible.
  * NEVER record a stale / transient / busy answer as a pass:
      - busy + "not ready" banners are filtered accent-insensitively
        (config.is_busy_banner / is_not_ready),
      - self-healing "Tactic #..." status frames are rejected and re-asked,
      - an answer identical to the previous question's answer is rejected.
  * Multi-Turn is RE-ASSERTED immediately before every single send.

What it actually judges (this is a SPANISH test, not a smoke test):
  1. ¿contestó?            non-empty, plausible length
  2. ¿contestó EN ESPAÑOL? Spanish function-word score must beat English.
                           A Spanish question answered in English is a FAIL --
                           that is the whole point of the Spanish edition.
  3. ¿respetó el registro? For questions carrying `keep_en`, the English
                           technical noun must survive. A register BREAK is
                           scored only when the English term is ABSENT *and*
                           its Spanish translation is PRESENT -- so an answer
                           that says "un container (contenedor)" is fine, and
                           common Spanish words never cause a false positive.
  4. gemelas de acentos    the 60 accented/unaccented pairs are compared after
                           the run: both halves must reach the same verdict.

Usage (from this folder):
    python prueba_1000_es.py                 # all 1000, resumable
    set ES_N=25 && python prueba_1000_es.py  # a short sanity slice first
"""
import os
import sys
import time
import json
import random
import html
import unicodedata
import datetime as _dt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# Credentials live in .creds.env (gitignored). Load before importing config.
_CREDS = os.path.join(HERE, ".creds.env")
if os.path.exists(_CREDS):
    with open(_CREDS, "r", encoding="utf-8-sig") as _fh:
        for _line in _fh:
            _line = _line.strip()
            if not _line or _line.startswith("#") or "=" not in _line:
                continue
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())

import config as C          # noqa: E402
import run_test as R        # noqa: E402
from preguntas_es import CORPUS   # noqa: E402
