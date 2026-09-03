# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
#
#   Every line of this file was written by Angela López Mendoza.
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove (releases scrub the name automatically)
"""Impide que PyInstaller recoja los binarios de Torch para la app web congelada.

$PyInstaller-Hook-Priority: 2

``--exclude-module=torch`` bloquea los MODULOS de Torch, pero PyInstaller aun
puede ejecutar el ``hook-torch.py`` de upstream mientras analiza importadores
opcionales como torchvision/datasets. Ese hook llama a
``collect_dynamic_libs('torch')`` y copiaba 2.5 GB de DLLs de CUDA dentro de
``_internal/torch/lib`` aunque cada modulo ``torch.*`` estuviera excluido.

El proceso Django congelado de Tlamatini NO usa Torch. El Talker corre en un
subproceso aparte del pool, bajo el Python ACARREADO (``<install>/python``),
donde el build provisiona y verifica por su cuenta un Torch de solo CPU.

⚠️ ESA FRONTERA ENTRE INTERPRETES ES LA REGLA, y en esta edicion ademas cuida
la voz: el Talker y la Whisperer importan torch bajo el Python acarreado, asi
que excluir Torch AHI dejaria muda a Tlamatini. Este hook de prioridad mas
alta hace que la frontera valga tambien para los binarios, no solo para los
modulos de Python.
"""

datas = []
binaries = []
hiddenimports = []
excludedimports = ["torch"]
