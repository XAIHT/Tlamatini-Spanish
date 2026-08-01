## Editorial notes — *not part of the spliced text*

**Three references require bibliographic completion.** The fertility argument cites three works by arXiv identifier only, because verified title/author/year metadata was not available at drafting time:

- `[fertility-african]` — arXiv:2509.05486 (10 LLMs × 16 African languages; regression slopes −0.08 to −0.18)
- `[fertility-ukrainian]` — arXiv:2605.14890 (Ukrainian zero-shot; ρ = −0.43, p = 0.34)
- `[fertility-european]` — arXiv:2605.24718 (24 European languages, six tokenizers; EN 1.23, ES 1.46 tokens/word)

Per §1.5 and §9 (*Bibliographic integrity*), each must be re-fetched and its title, authors, year and identifier confirmed — and each numeric value re-checked against its source table — before publication. A new **"Tokenization cost"** sub-heading already exists in the reference list; these belong there beside `[nayeem2025strr]` and `[petrov2023tokenizerunfairness]`.

**Two places elsewhere in §6 are now contradicted by the implementation and need a one-line correction each.**

1. **§6.2, the architecture diagram** (line 498). The `PROBE` node is captioned `capability profile — chooses the START rung only`, and the edge into `LADDER` is labelled `optimisation, not a gate`. The implemented profile also gates N3 at Stage 2. Suggested minimal patch — retarget the dashed edge so it reaches both stages, and soften the caption:

   ```
   PROBE[("capability profile<br/><i>start rung + assist policy</i>")] -.->|"optimisation, not a gate"| LADDER
   PROBE -.->|"gates N3 expansion only"| NEUTRAL
   ```

2. **§6.7, the pseudocode** (line 622). The line

   ```python
   key    = N3(N1(u), lang)                     # fold + canonical expansion
   ```

   should read

   ```python
   key    = N3(N1(u), lang, profile.assist(model))   # expansion gated by measured tier
   ```

   with the existing comment `# identity on ASCII: an English u yields today's exact plan` retained — it is still true, since N3 short-circuits on `ℓ = en` regardless of tier.

**One claim in the previous §7.3 was dropped rather than carried forward, deliberately.** The original text specified a *per-path* profile ("a starting rung for the conversational path and another for the operator path") and a *daily single-call canary* whose response hash would fingerprint a silent cloud-model swap. Neither is implemented. The battery instead weights the operator check heaviest (2.0 against 1.0/1.5/1.0) within a single scalar tier, and the swap-detection role is carried by digest-or-exact-id identity plus L2's demote authority. Per-path emission remains a clean future refinement and costs nothing to adopt later, because the per-check raw features are already persisted — splitting the tier by path requires no re-probe. The replacement text says this; it does not restate the canary as though it existed.

**Assessment requested on the two corollaries, stated flatly.**

- **Corollary 1 (Probe Safety) — strengthened in motivation, narrowed in scope.** Observation 1 makes a *gating* probe undeliverable, so the corollary is what makes the whole approach admissible rather than merely convenient. But the implemented profile appears twice, not once, and only one appearance is covered by the corollary's proof. The statement and proof are unchanged; **Corollary 1′** is added to cover the second appearance with a weaker, honestly-bounded claim, and the context-overflow exposure is named rather than absorbed.
- **Corollary 2 (Naming Necessity) — strengthened, and along a new axis.** The corollary was already *proved*; what was only *argued* was its practical inescapability. Observation 1 closes the single escape route — a locale-indexed action vocabulary — by showing that the oracle such a design requires is published by nobody. The upgrade is stated precisely and not overclaimed: this is not an impossibility proof, it is a demonstration that the alternative has no available input, and it would have to be reopened if a provider ever published language metadata.
