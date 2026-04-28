# Theorem 3 RLVR Reframing Note

## Headline

- Conditional law: Reasoning-time overconfidence under knowledge conflict is best written as a conditional RLVR / misspecification law, not as a universal scale law.
- DeepSeek `7B -> 14B` asymmetry replicates: `True`
- Qwen `7B -> 14B` asymmetry replicates: `False`
- Conflict/no-conflict eta shrink factor: `0.52`

## Recommended Theorem-3 Wording

Models trained with verifiable-reward reasoning objectives can enter a misspecified, endogenous-evidence regime under knowledge conflict, where longer CoT sharpens confidence faster than it improves accuracy. The effect is benchmark-dependent and strongest on controlled conflict families.

## Contrast With Nearby Literature

| Paper | Setting | Their result | How it lines up with the current theorem-3 read |
|---|---|---|---|
| Yoon et al. (NeurIPS 2025) | QA without explicit knowledge conflict | CoT improves confidence calibration in most settings. | Compatible. That is the well-specified or low-conflict side of the split. |
| Lacombe et al. (ICML 2025 workshop) | Knowledge-intensive confidence assessment | Longer reasoning budgets impair calibration. | Compatible. This is the hard-QA / misspecified side of the split. |
| Welch et al. (arXiv 2603.16728) | Vision-language uncertainty under CoT | Implicit answer conditioning drives overconfidence. | This is the best mechanistic phrase for the endogenous-evidence side of theorem 3. |
| Damani et al. (RLCR) | Reward design for reasoning calibration | Binary reward reasoning hurts calibration; Brier-style rewards repair it. | This is the training-time cousin of our test-time conditional law. |

## Read

- The repo no longer supports a universal `7B recovers / 14B saturates` theorem. That stronger statement is false.
- The repo now does support a better theorem: controlled conflict can keep larger reasoning models in a saturated overconfidence regime, while naturalistic contradiction can still show partial self-correction.
- The RLVR framing is the cleanest way to reconcile the DeepSeek-vs-Qwen split without throwing away the theorem-3 contribution.
