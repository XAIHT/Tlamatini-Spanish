# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
#
#   Every line of this file was written by Angela López Mendoza.
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove (releases scrub the name automatically)
from __future__ import annotations

import argparse
from pathlib import Path

from markdown import markdown
from xhtml2pdf import pisa


DEFAULT_CSS = """
@page { size: A4; margin: 18mm; }

body {
  font-family: Helvetica, Arial, sans-serif;
  line-height: 1.35;
  font-size: 11pt;
}

h1, h2, h3 { margin: 0.6em 0 0.3em; }
p { margin: 0.35em 0; }

code, pre {
  font-family: Courier, monospace;
  font-size: 9.5pt;
}

pre {
  padding: 10px;
  border: 1px solid #ddd;
  white-space: pre-wrap;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin: 0.6em 0;
}
th, td {
  border: 1px solid #ddd;
  padding: 6px;
  vertical-align: top;
}
"""


def markdown_text_to_pdf(md_text: str, output_pdf: Path, base_dir: Path | None = None, css_text: str = DEFAULT_CSS) -> None:
    """Convierte Markdown a PDF estilizado.

    ``base_dir`` conserva el directorio de referencia para imágenes relativas como
    ``![](images/a.png)``; se mantiene en el contrato aunque xhtml2pdf resuelva el
    contenido inline actual sin necesitarlo.
    """
    # Extensiones base: tablas y bloques de código cercados.
    html_body = markdown(
        md_text,
        extensions=["fenced_code", "tables", "toc"],
        output_format="html5",
    )

    html_doc = f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Documento Tlamatini</title>
    <meta name="author" content="Angela López Mendoza">
    <style>
      {css_text}
    </style>
  </head>
  <body>
    {html_body}
  </body>
</html>
"""

    with open(str(output_pdf), "w+b") as pdf_file:
        pisa_status = pisa.CreatePDF(
            html_doc,
            dest=pdf_file,
            encoding="utf-8",
        )

    if pisa_status.err:
        raise RuntimeError(f"xhtml2pdf encontró {pisa_status.err} error(es) durante la conversión.")


def main() -> None:
    ap = argparse.ArgumentParser(description="Convierte Markdown a PDF con Markdown + xhtml2pdf.")
    ap.add_argument("input", help="Ruta de un archivo .md (o '-' para leer stdin)")
    ap.add_argument("output", help="Ruta del PDF de salida")
    ap.add_argument("--css", help="Ruta opcional de una hoja CSS", default=None)
    args = ap.parse_args()

    output_pdf = Path(args.output)

    if args.input == "-":
        md_text = __import__("sys").stdin.read()
        base_dir = Path.cwd()
    else:
        input_md = Path(args.input)
        md_text = input_md.read_text(encoding="utf-8")
        base_dir = input_md.parent

    css_text = DEFAULT_CSS
    if args.css:
        css_text = Path(args.css).read_text(encoding="utf-8")

    markdown_text_to_pdf(md_text, output_pdf, base_dir=base_dir, css_text=css_text)
    print(f"Escrito: {output_pdf.resolve()}")


if __name__ == "__main__":
    main()
