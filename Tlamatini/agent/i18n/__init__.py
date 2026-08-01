"""NEPANTLA language layer for Tlamatini (Spanish edition).

STEP 1 - language-neutral deterministic core.

THE REGISTER THIS PACKAGE SERVES
--------------------------------
Spanish is the MATRIX language; English is the EMBEDDED technical lexicon.
A Mexican developer says:

    "Haciendo un Pod en Dockerer y creando un Container en Kubernetes
     y haciendo el deployment en la LPAR"

Spanish supplies the grammar - haciendo, creando, un, en, la, y. English
supplies every technical term - Pod, Dockerer, Container, Kubernetes,
deployment, LPAR. The GUI is localized the SAME way: the carrier becomes
Spanish, the technical vocabulary does not move.

    Emailer tooltip:  "Envia un email por SMTP cuando se detecta un pattern
                       en el log."

Not "correo", not "patron", not "registro". Translating those would be
over-translation - it reads as foreign to the very audience it is for.

WHAT THIS MEANS FOR THIS PACKAGE, CONCRETELY
--------------------------------------------
Because the user already writes the English technical nouns, a large share of
Spanish requests hit the English capability hints DIRECTLY, with no mapping of
any kind. The lexicon therefore concentrates on what is genuinely Spanish in
such a sentence: the verbs and the connectives. A smaller, correct table beats
a large speculative one.

It also strengthens the correctness guarantee rather than weakening it: the
fewer terms that shift between locales, the larger the surface on which the
Spanish and English action vocabularies coincide.

WHY THIS PACKAGE HAS NO IMPORTS
-------------------------------
``capability_registry`` imports ``normalize`` DIRECTLY::

    from .i18n.normalize import fold_text, phrase_hit, expand_request

and never through a facade re-exported from here. If this __init__ pulled in
the termbase, the lexicon and the registries, an ImportError anywhere in that
graph would break the import of __init__ itself - and an ImportError-swallowing
facade is useless when the facade is the thing that failed. It would also
create a cycle, since capability_registry is imported by the very modules a
richer facade would want to reach.

So: no imports here, ever. Every submodule is independently importable and
independently fail-open.

MODULE MAP
----------
normalize.py    N1 folding, N2 boundary-aware phrase matching, N3 expansion gate.
                Stdlib only, never imports agent.* - it sits on the hot path.
lexicon_es.py   DATA ONLY. Spanish CARRIER terms -> canonical English hint
                tokens that already exist in the registry. Never invents one.
termbase_en.py  DATA ONLY. The do-not-translate inventory: machine sentinels,
                agent display names, tool names, product terms and the English
                technical lexicon that stays English in the Spanish GUI.
flags.py        The config.json switches. Stdlib only, fail-open.

NOTHING HERE EVER RENAMES AN ASSET
----------------------------------
Agent display names (Emailer, Asker, Apirer, Executer, Pythonxer, STM32er,
Kyber-KeyGen, File-Creator, De-Compresser, Monitor-Log, Node Manager, ...),
tool names, argument keys, config keys, CLI flags, protocol sentinels, CSS
classes, environment variables, log-line prefixes and every identifier in the
source are byte-identical in every locale, forever. This package changes only
how a USER'S SENTENCE is read, never what the machine is called.
"""

__all__: list[str] = []
