// ═══════════════════════════════════════════════════════════════════
//   ✦  T L A M A T I N I  ✦   —   "la que sabe"
//
//   Creado por  Angela López Mendoza   ·   @angelahack1
//   Desarrolladora · Arquitecta · Creadora de Tlamatini
// ═══════════════════════════════════════════════════════════════════
//   Tlamatini Author Banner — no se quita (el nombre de Angela va en cada build)
//
// Emite el flujo de tokens de un archivo JS con el contenido de las cadenas y
// plantillas en blanco, para comprobar que entre dos archivos "sólo cambiaron
// los textos".
// uso: node js_tokens.cjs <carpeta-de-acorn> <archivo.js>
'use strict';
const fs = require('fs');
const acorn = require(process.argv[2]);
const src = fs.readFileSync(process.argv[3], 'utf8');

function tokens(sourceType) {
  const salida = [];
  for (const t of acorn.tokenizer(src, { ecmaVersion: 'latest', sourceType,
      allowHashBang: true, allowReturnOutsideFunction: true,
      allowAwaitOutsideFunction: true, allowImportExportEverywhere: true })) {
    const l = t.type.label;
    if (l === 'string' || l === 'template') salida.push(l);
    else if (l === 'regexp') salida.push('re:' + t.value.pattern + '/' + t.value.flags);
    else salida.push(l + ':' + (t.value === undefined ? '' : String(t.value)));
  }
  return salida;
}
let resultado;
try { resultado = tokens('module'); } catch (e) { resultado = tokens('script'); }
process.stdout.write(JSON.stringify(resultado));
