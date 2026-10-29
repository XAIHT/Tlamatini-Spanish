# Tlamatini Author Banner — Created by Angela López Mendoza · @angelahack1
"""Spanish-edition speech spelling, shared by Django, the avatar and Talker.

This module is stdlib-only and travels as a flat sibling with every Talker pool
copy. It prepares text, never account identifiers or authentication data.
Explicit accents win, except Angéla, which Angela explicitly asked to correct.
"""

import re
import unicodedata


def _fold(value):
    # Remove acute accents only: ñ and ü are different letters, not missing tildes.
    return unicodedata.normalize(
        'NFC', unicodedata.normalize('NFD', value.lower()).replace('\u0301', ''))


# Curated spellings, not a guess at where every unknown person's stress belongs.
# Unaccented names (Ana, Laura, Guadalupe, Luis, etc.) are
# otherwise left alone. No n -> ñ conversion and no forced accent on foreign names.
_NAMES = '''
Ábner Ágata Agustín Aída Álvaro Amílcar América Anahí Andrés Ángel Ángela Ángeles
Angélica Aníbal Aristóteles Aarón
Asunción Bárbara Bartolomé Benjamín Belén Bernabé Brígida Cándida Cándido
César Cristóbal Damián Darío Débora Delfín Diógenes Doménica
Edén Efraín Elías Édgar Eloísa Érika Fabián Fátima Félix Fermín Fernán
Germán Hernán Hipólito Héctor Inés Iván
Jaír Jeremías Jerónimo Jesús Joaquín Jonás José Julián Lázaro León
Lía Lucía Máximo María Martín Matías Míriam Mónica Moisés
Néstor Nicolás Noé Noemí Óliver Óscar Ósmar Óseas Penélope
Pía Pío Plácido Ramón Raúl René Rocío Román Rubén Salomé Salomón Saúl
Sebastián Simón Sofía Sócrates Teófilo Tomás Tránsito Úrsula Valentín
Verónica Víctor Xóchitl Yasmín Zacarías Zoé
Álvarez Ávalos Ávila Báez Benítez Bermúdez Chávez Cortés Córdova Díaz Domínguez
Enríquez Fernández García Gómez González Gutiérrez Hernández Jiménez Juárez
López Márquez Martínez Méndez Muñoz Núñez Ordóñez Páez Pérez Ramírez Rodríguez
Sánchez Suárez Téllez Vázquez Velázquez Zárate Zúñiga
'''
NAME_ACCENTS = {_fold(name): name for name in _NAMES.split()}
# These can also be ordinary words. Only infer them in name fields, explicit
# per-person overrides, or capitalized prose; never change a lower-case verb.
AMBIGUOUS = frozenset({'cesar', 'leon', 'maximo', 'pio', 'transito'})
_WORD = re.compile(r"[^\W\d_]+", re.UNICODE)
# One tokenizer in both runtimes. Keep URLs, mail, paths, code, HTML and opaque
# identifiers intact. Punctuation around a name is not part of its spelling.
TOKEN_PATTERN = (
    r'```[\s\S]*?```|`[^`\n]*`|<[^>\n]*>|'
    r'(?:https?://|www\.)[^\s<>]+|'
    r'[\w.+-]+@[\w.-]+\.[\w-]+|'
    r'@[\w]+|'
    r'(?:[A-Za-z]:[\\/]|[./\\])[\w./\\-]+|'
    r'[\w]+(?:[_.+@/\\-][\w]+)+|'
    r'\w*\d\w*|[^\W\d_]+'
)
_TOKEN = re.compile(TOKEN_PATTERN, re.UNICODE)


def _case_like(source, replacement):
    if source.isupper():
        return replacement.upper()
    if source.islower():
        return replacement.lower()
    return replacement


def accent_name(value):
    """Restore known Spanish names in a NAME field, retaining separators/case."""
    value = unicodedata.normalize('NFC', str(value or ''))

    def replace(match):
        token = match.group()
        key = _fold(token)
        if key != 'angela' and any(c in token.lower() for c in 'áéíóú'):
            return token
        return _case_like(token, NAME_ACCENTS.get(key, token))

    return _WORD.sub(replace, value)


def speech_text(value, overrides=None, language='es-MX'):
    """Prepare spoken prose without rewriting source text, logins or code.

    Overrides are exact names/aliases -> desired spoken spelling. Existing
    accents and unknown names are retained. No invented phonemes or SSML.
    """
    text = unicodedata.normalize('NFC', str(value or ''))
    if str(language).lower().replace('_', '-').split('-')[0] not in ('es', 'spanish', 'español'):
        return text
    aliases = {unicodedata.normalize('NFC', str(k)).lower(): str(v)
               for k, v in (overrides or {}).items() if k and v}

    def replace(match):
        token = match.group()
        # An account alias can contain separators; never override a URL/mail/path.
        if token.lower() in aliases and not re.search(r'[@/\\<>`]', token):
            return aliases[token.lower()]
        if not _WORD.fullmatch(token):
            return token
        if token.islower() and _fold(token) in AMBIGUOUS:
            return token
        return accent_name(token)

    return _TOKEN.sub(replace, text)


def browser_payload(user=None):
    """Serialize one catalog and the current account's names; no other user data."""
    first = str(getattr(user, 'first_name', '') or '').strip().split()
    username = str(getattr(user, 'username', '') or '').strip()
    raw = first[0] if first else username
    name = accent_name(raw)
    name = name[:1].upper() + name[1:]
    aliases = {s: name for s in (raw, username) if s and name}
    return {'names': NAME_ACCENTS, 'ambiguous': sorted(AMBIGUOUS),
            'token_pattern': TOKEN_PATTERN, 'display_name': name, 'aliases': aliases}
