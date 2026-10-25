// ═══════════════════════════════════════════════════════════════════
//   ✦  T L A M A T I N I  ✦   —   "la que sabe"
//
//   Creado por  Angela López Mendoza   ·   @angelahack1
//   Desarrolladora · Arquitecta · Creadora de Tlamatini
// ═══════════════════════════════════════════════════════════════════
//   Tlamatini Author Banner — no se quita (el nombre de Angela va en cada build)
//
// Lista cada literal de cadena y de plantilla de un archivo JS con su rango
// de bytes y su contexto sintáctico, como JSON en stdout.
// uso: node js_cadenas.cjs <carpeta-de-acorn> <archivo.js>
'use strict';
const fs = require('fs');
const acorn = require(process.argv[2]);
const src = fs.readFileSync(process.argv[3], 'utf8');

function parsear(codigo) {
  const base = { ecmaVersion: 'latest', locations: true, ranges: true,
    allowHashBang: true, allowReturnOutsideFunction: true,
    allowAwaitOutsideFunction: true, allowImportExportEverywhere: true };
  try { return acorn.parse(codigo, Object.assign({ sourceType: 'module' }, base)); }
  catch (e1) { return acorn.parse(codigo, Object.assign({ sourceType: 'script' }, base)); }
}

const ast = parsear(src);
const salida = [];

function nombreLlamada(nodo) {
  if (!nodo) return '';
  if (nodo.type === 'Identifier') return nodo.name;
  if (nodo.type === 'MemberExpression') {
    const p = nodo.property && (nodo.property.name || nodo.property.value);
    return nombreLlamada(nodo.object) + '.' + (p || '?');
  }
  return nodo.type;
}

function contexto(nodo, padre, llave, dueno) {
  if (!padre) return 'root';
  switch (padre.type) {
    case 'CallExpression': case 'NewExpression':
      return 'call:' + nombreLlamada(padre.callee) + ':arg' + padre.arguments.indexOf(nodo);
    case 'AssignmentExpression':
      return 'assign:' + nombreLlamada(padre.left);
    case 'Property':
      // la llave de un objeto que es el valor de `buttons:` es la etiqueta
      // de un botón de jQuery UI: texto de pantalla
      if (llave === 'key') return dueno ? 'propkey:' + dueno : 'propkey';
      return 'prop:' + (padre.key && (padre.key.name || padre.key.value));
    case 'BinaryExpression':
      return 'bin:' + padre.operator;
    case 'SwitchCase': return 'case';
    case 'VariableDeclarator': return 'var:' + (padre.id && padre.id.name);
    case 'ArrayExpression': return 'array';
    case 'ReturnStatement': return 'return';
    case 'ConditionalExpression': return 'cond';
    case 'LogicalExpression': return 'logic:' + padre.operator;
    case 'MemberExpression': return 'member';
    case 'ImportDeclaration': case 'ExportNamedDeclaration': case 'ExportAllDeclaration': return 'import';
    case 'TemplateLiteral': return 'tplexpr';
    case 'TaggedTemplateExpression': return 'tagged:' + nombreLlamada(padre.tag);
    default: return padre.type;
  }
}

function recorrer(nodo, padre, llave, dueno) {
  if (!nodo || typeof nodo.type !== 'string') return;
  if (nodo.type === 'Literal' && typeof nodo.value === 'string') {
    salida.push({ kind: 'lit', start: nodo.start, end: nodo.end, line: nodo.loc.start.line,
      raw: src.slice(nodo.start, nodo.end), value: nodo.value, ctx: contexto(nodo, padre, llave, dueno) });
  } else if (nodo.type === 'TemplateLiteral') {
    salida.push({ kind: 'tpl', start: nodo.start, end: nodo.end, line: nodo.loc.start.line,
      raw: src.slice(nodo.start, nodo.end), quasis: nodo.quasis.map(q => q.value.cooked),
      nexpr: nodo.expressions.length, ctx: contexto(nodo, padre, llave, dueno) });
  }
  // nombre de la propiedad cuyo valor es este objeto (para las llaves de `buttons: {...}`)
  let duenoHijos = '';
  if (nodo.type === 'ObjectExpression' && padre && padre.type === 'Property' && llave === 'value') {
    duenoHijos = String((padre.key && (padre.key.name || padre.key.value)) || '');
  }
  for (const k of Object.keys(nodo)) {
    if (k === 'loc' || k === 'range') continue;
    const v = nodo[k];
    const d = nodo.type === 'Property' ? dueno : duenoHijos;
    if (Array.isArray(v)) v.forEach(c => { if (c && typeof c.type === 'string') recorrer(c, nodo, k, d); });
    else if (v && typeof v.type === 'string') recorrer(v, nodo, k, d);
  }
}
recorrer(ast, null, null, '');

// acorn da offsets en unidades UTF-16; se reportan también los offsets en
// bytes UTF-8 para que Python empalme bytes exactos.
const codificador = new TextEncoder();
let ultimoU16 = 0, ultimoByte = 0;
const ordenadas = salida.slice().sort((a, b) => a.start - b.start);
function aByte(u16) {
  if (u16 < ultimoU16) { ultimoU16 = 0; ultimoByte = 0; }
  ultimoByte += codificador.encode(src.slice(ultimoU16, u16)).length;
  ultimoU16 = u16;
  return ultimoByte;
}
for (const s of ordenadas) { s.bstart = aByte(s.start); s.bend = aByte(s.end); }
process.stdout.write(JSON.stringify(ordenadas));
