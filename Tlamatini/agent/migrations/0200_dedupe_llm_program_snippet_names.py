"""Repara los nombres duplicados de LLMProgram / LLMSnippet que dejo un build viejo.

Angela, 2026-09-06. Los nombres de program y de snippet se arman como
``<marca de tiempo UTC al SEGUNDO>_<nombre>`` (services/filesystem.get_time_stamp),
asi que dos bloques de codigo emitidos en la MISMA respuesta recibian el MISMO
nombre — mientras que todos los lectores lo buscaban por NOMBRE con ``.get()``.
Ese par de filas quedaba inalcanzable para siempre:

* ``load_canvas_view`` lanzaba ``MultipleObjectsReturned`` — un 500 SIN ATRAPAR,
  porque ``except LLMProgram.DoesNotExist`` no lo cacha — asi que "Cargar en el
  canvas" simplemente fallaba.
* ``save_files_from_db`` chocaba con la misma excepcion y registraba
  ``!!! ERROR while saving file: get() returned more than one LLMProgram``,
  para LAS DOS gemelas, asi que ninguno de los dos archivos se podia escribir
  jamas al disco.

El contenido nunca se perdio, solo se volvia inalcanzable. Lo que se guarda
nuevo ya se desambigua al guardarse (``services/response_parser._uniquify_name``)
y todos los lectores se hicieron a prueba de colisiones, pero una base escrita
por un build VIEJO todavia carga los duplicados — esta migracion los repara.

NO DESTRUCTIVA POR DISENO: aqui no se borra nada, nunca. La fila con el id mas
bajo conserva el nombre original y cada gemela posterior se RENOMBRA a
``<nombre>_2`` / ``<nombre>_3`` … (saltando cualquier sufijo ya ocupado), asi que
AMBOS archivos vuelven a poderse cargar y guardar con nombres distintos. Tambien
es idempotente y FAIL-OPEN: una base sin duplicados no se toca, y cualquier error
inesperado se traga en vez de bloquear el migrate completo (un post-update
migrate que aborta dejaria a la usuaria sin sus agents/tools/prompts nuevos, que
es muchisimo peor que un duplicado sin reparar).

NEPANTLA: la prosa va en español; el tag de log ``[NAME-GUARD]`` y el sufijo
``_2`` / ``_3`` son canal de maquina y se quedan en ingles, byte-exactos.

Numeracion: en el arbol ingles esta migracion es la 0198->0199. Aqui es la
**0200** porque esta edicion lleva una migracion extra desde el principio
(``0191_translate_prompt_catalog_to_spanish``), asi que va un numero adelante y
depende de ``0199_add_pdfer_nuance_demo_prompt``.
"""
from django.db import migrations
from django.db.models import Count

_SUFFIX_LIMIT = 999


def _dedupe(model, field):
    """Renombra cada duplicado de `field` salvo la fila de id mas bajo. Devuelve el conteo."""
    renamed = 0
    dupes = (
        model.objects.values(field)
        .annotate(n=Count(field))
        .filter(n__gt=1)
        .values_list(field, flat=True)
    )
    for name in list(dupes):
        rows = list(model.objects.filter(**{field: name}).order_by('pk'))
        for row in rows[1:]:  # la PRIMERA fila conserva el nombre original
            for n in range(2, _SUFFIX_LIMIT + 1):
                candidate = f"{name}_{n}"
                if not model.objects.filter(**{field: candidate}).exists():
                    setattr(row, field, candidate)
                    row.save(update_fields=[field])
                    renamed += 1
                    print(f"--- [NAME-GUARD] duplicado reparado '{name}' -> '{candidate}'")
                    break
    return renamed


def dedupe_names(apps, schema_editor):
    try:
        total = 0
        total += _dedupe(apps.get_model('agent', 'LLMProgram'), 'programName')
        total += _dedupe(apps.get_model('agent', 'LLMSnippet'), 'snippetName')
        if total:
            print(f"--- [NAME-GUARD] {total} nombre(s) duplicado(s) reparado(s) - los archivos vuelven a cargar")
    except Exception as exc:  # FAIL-OPEN: jamas bloquear un post-update migrate
        print(f"--- [NAME-GUARD] reparacion de nombres duplicados omitida: {exc}")


def noop_reverse(apps, schema_editor):
    """Irreversible a proposito — renombrar de vuelta recrearia el estado roto."""
    pass


class Migration(migrations.Migration):
    dependencies = [('agent', '0199_add_pdfer_nuance_demo_prompt')]
    operations = [migrations.RunPython(dedupe_names, noop_reverse)]
