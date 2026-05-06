# Paper style guide for Claude

Read this on every paper-editing turn before making changes. Apply on every revision. After any edit, reread the modified passage and check it against this list.

## Sentence structure: hard bans

1. **No "Not X, but Y" / "Not just X, but Y" / "Not X. It is Y."** Define by stating, not by negating. The single strongest AI tell. Cut on sight.
2. **No mirrored clause pairs.** "In principle X. In practice Y." Rephrase asymmetrically.
3. **No "from X to Y" range constructions.** Say the range plainly or list specifics.
4. **No triple parallel structures.** Three clauses or items in identical grammatical form is an AI signal. Two is fine.
5. **No trailing present participles.** Sentences ending with ", creating...", ", reflecting...", ", emphasizing...", ", making it...". Restructure.
6. **No short dramatic standalone sentences after long ones** as rhetorical punctuation. Fold the idea in.
7. **No mirror sentences across sentence boundaries.** "Where X does A, Y does B. Where X does C, Y does D." Break the symmetry.
8. **No "It is not X. It is Y." closers.** Strong AI tell.

## Word and phrase bans

9. **Banned vocabulary:** landscape, ecosystem, nascent, trajectory, catalyze, interlocking, legible, niche, multifaceted, nuanced, delve, underscore, tapestry, pivotal, groundbreaking, holistic, robust, keen, commendable, notable, noteworthy, invaluable, captivating, leverage (verb), seamless, paradigm shift, intricate, profound (overused).
10. **Banned throat-clearers:** "It is worth noting that", "It must be clearly communicated that", "A critical clarification must anchor", "Importantly", "Notably", "Crucially", "Indeed". Delete and say the thing.
11. **Banned vague-importance closers:** "This is the vacuum X was built to fill", "These are the questions X was built to answer". Say specifically what happens next.
12. **Banned sentence starters:** Rather, Thus, Moreover, Furthermore, Critically, Importantly. "However" sparingly, never paired with "Rather" nearby.
13. **Banned scene-setters:** "In today's", "In an era of", "In the realm of", "In a moment when", "At a time when". Cut.
14. **"Straightforward"** not allowed before a complex explanation. **"Precisely"** only for actual precision. **"Particularly"** / **"especially"** at most once per page.

## Structural bans

15. **No announcing what you're about to do.** "A critical clarification must anchor" before the clarification. Just write.
16. **No "The first is... The second is... The third is..."** Vary or use running prose.
17. **No cushioning every critique with a counterpoint.** State the point.
18. **No metaphor-then-explanation.** Trust the reader.
19. **No frictionless transitions.** Human writing has rougher joints. Not every paragraph needs a bridge.
20. **No grand summative section closers.** Let the last substantive point be the ending.
21. **No context-setting generalities at paragraph starts.** Lead with the specific.

## Punctuation

22. **Em dashes (---): at most one per page.** Prefer periods, commas, colons, parentheses.
23. **No colon-based titles** ("X: A Y" format). Plain titles only.

## Tense / framing

24. **No present-tense "as if it exists" for proposed work.** Use "is being designed to", "would", "the goal is".
25. **No prosecutorial framing of cited work.** State the technical disagreement, not the narrative.

## General

26. Vary sentence length. Short and long mixed.
27. Concrete specifics over abstractions. "Nobody is checking" beats "no existing institution is structured to systematically verify".
28. Don't use words you wouldn't say to a colleague.
29. If a sentence sounds impressive but says nothing specific, cut it.
30. After revising, reread. Check every sentence against this list. Then check again.

---

## Paper-specific consistency rules

These are the canonical numbers for *When Should LLMs Trust Retrieval?* Cross-check on every edit:

### Headline empirical claims (do not change)

- **CT1 powered head-to-head (n=210):** Bayes vs. CoCoA / Astute / Self-RAG = +0.043 / +0.032 / +0.022 regret, all CIs strictly above zero.
- **CT1 spotlight (25 cells):** CIs include zero against the same three baselines.
- **CT1 axis table:** six published methods + BayesArbiter, regrets +5.242 / +7.994 / +0.404 / -0.079 / -0.106 / -0.128 / -0.172.
- **CT2 Berk-Nash:** 12 cells over 3 model families (R1-14B, R1-8B-RLCR, Mistral-7B), pooled MAE 0.022, r=0.997, held-out ±0.08.
- **CT3 closed-form:** Δ Brier(η*) = (1-η*)² V_post + O((1-η*)³).
- **CT3 pooled:** +0.043 Brier, +0.071 accuracy.
- **CT3 worst-cell (RLCR+η):** accuracy 0.063 → 0.531, ECE 0.904 → 0.431.
- **Matched-base headline (Llama-3.1-8B):** SFT +0.029, DPO +0.045, GRPO +0.344 [0.230, 0.476]. GRPO−SFT +0.315.
- **Matched-base replications:** DeepSeek-R1-Distill-Llama-70B (RLVR) +0.388, Phi-3 (SFT/DPO/GRPO) +0.207 / +0.003 / +0.209, DeepSeek-R1-Distill-Llama-8B +0.076.
- **Latency:** 4.38 s/query end-to-end, 1.21 s for CAD; cached 1.09–2.19 s/query.
- **Free-form n≈200:** ASQA 0.27, NQ-open 0.31, TriviaQA-open 0.39 (Bayes EM, ties AdaCAD, beats CAD).
- **Frontier validation:** GPT-4o-mini / Claude / Gemini regret advantage +0.055 to +0.060.

### Scope rules

- **Matched-base causal anchor** is the Llama lineage (Llama-3.1-8B, DeepSeek-Llama-70B, DeepSeek-Llama-8B). Phi-3 is a cross-family replication. Other base families are not the load-bearing claim.
- **CT2** is scoped to the stable-answer subset; pre-saturated cells are out of scope.
- **CT3 (Brier closed-form)** assumes a non-degenerate cell ($p_K(y^\star) \ne 1/|\Y|$).
- **Free-form** at n≈200 is the only free-form result. No pilot table.

### Forbidden references in this draft

- No mention of "community checkpoint", "native rerun", "earlier", "previously", "now improved", "replaced", "had registered as failure", "version v6/v7", "Paper 2", "cluster status", "2026-05-XX".
- No "pre-registered" / "P1, P2, P3" / "falsified as binary" language.
- No "matched-base reversal", "Mistral GRPO closes the gap", "Gemma DPO/GRPO close the gap" — out of scope of the Llama-anchored claim.
- No multi-seed dispersion paragraph in appendix.

### Theorem labels

- CT1 = Bayes-optimal arbitration (Gibbs minimizer).
- CT1' = perturbation envelope.
- CT2 = trajectory envelope on F (Berk-Nash spectral rate).
- CT3 = closed-form Brier improvement under η-tempering.
- No CT4. No T-numbered references in body unless cross-referencing appendix.

### Figure / table placement

- Body floats: `[!htbp]` for first reference, `[H]` only inside subfigures.
- Captions begin with a bolded one-line claim, then optional explanation.
- No colon titles. No em-dashes in captions.

---

## Reviewer self-check (run after every substantive edit)

1. Search the diff for em-dashes. Count. If more than one new em-dash in a page-equivalent passage, rewrite.
2. Search for "Not X, but Y" / "Not just X" / "Not merely X". Rewrite each hit.
3. Search for trailing ", creating" / ", reflecting" / ", emphasizing" / ", making it". Restructure each.
4. Search for banned vocabulary (rule 9). Replace.
5. Search for banned starters (rule 12) at sentence beginnings. Restructure.
6. Search for "in plain English", "intuitively", "to put it simply", "in other words". Cut.
7. Cross-check every numerical claim against the canonical list above. Flag any drift.
8. Read three random paragraphs aloud (mentally). If anything sounds like a press release, rewrite.

If a passage passes all eight checks, leave it alone. Do not over-edit on subsequent passes.
