# Novelty Audit (April 2026)

This note is a guardrail for the paper. Its purpose is not to undersell the
project; it is to keep the novelty claim scientifically defensible as the
test-time-scaling literature evolves.

## Bottom line

The strongest current claim is **not**:

- "the first work to combine calibration and test-time scaling"
- "the first work to use statistical guarantees for test-time scaling"
- "the first work to use sequential methods at test time"

Those claims are now too broad.

The strongest defensible claim is closer to:

- execution-grounded **sequential falsification for code generation**
- explicit **population-level elimination** rather than single-candidate repair
- benchmark-aware **adversarial probe families** for code tasks
- a unified code-focused framework that compares falsification against majority
  vote, self-debugging, generated-test filtering, and local CodeT/S* proxies
- empirical confidence analysis for survivor ranking, with conservative wording
  about guarantees

## Recent literature that narrows the novelty window

### 1. S* (code test-time scaling)

Source:

- arXiv: [S*: Test Time Scaling for Code Generation](https://arxiv.org/abs/2502.14382)

What it means for us:

- We cannot claim to be the first serious code-domain test-time-scaling method.
- We cannot claim that adaptive input generation for code selection is new in
  the broad sense.
- We **can** still claim a different mechanism: falsification-by-elimination
  over a candidate population, rather than S*'s adaptive distinguishing-input
  comparison framework.

### 2. ATTS (adaptive test-time scaling with conformal/statistical control)

Source:

- arXiv / ICLR 2026: [ATTS: Asynchronous Test-Time Scaling via Conformal Prediction](https://arxiv.org/abs/2509.15148)

What it means for us:

- We cannot claim to be the first statistically grounded adaptive TTS method.
- We cannot claim that conformal / hypothesis-testing style control is absent
  from test-time scaling in general.
- We **can** still claim that our work is different in domain and mechanism:
  ATTS is about asynchronous adaptive scaling and rejection control, not
  execution-grounded code falsification with candidate elimination.

### 3. ORCA (reasoning calibration under TTS)

Source:

- arXiv: [Online Reasoning Calibration: Test-Time Training Enables Generalizable Conformal LLM Reasoning](https://arxiv.org/abs/2604.01170)

What it means for us:

- We cannot claim to be the first calibration paper for test-time scaling.
- We cannot claim that valid confidence or calibration for TTS is untouched.
- We **can** still claim that our code-generation setting and execution-based
  falsification pipeline are different from reasoning-process calibration.

## What is still plausibly novel

These claims remain credible if the paper stays careful:

1. **Execution-grounded sequential falsification for code generation as the
   central TTS primitive.**

   The paper's main mechanism is not just "more tests" or "more calibration."
   It is repeated adversarial challenge and elimination over a pool of code
   candidates.

2. **A benchmark-aware elimination pipeline spanning HumanEval+, MBPP+,
   LiveCodeBench, and math-style tasks in one repo.**

   This is a systems novelty / experimental novelty claim, not a theorem-level
   novelty claim.

3. **Population selection rather than repair.**

   Self-debug is exploitation over one candidate. Falsification is selection
   from diversity. That distinction still matters and should stay central.

4. **Adaptive vs non-adaptive generated-test comparison inside one framework.**

   The generated-test-filter baseline is important here because it isolates
   whether adaptivity matters.

5. **Honest confidence analysis for code-candidate survival/ranking.**

   The paper should frame this as empirical calibration and testing-inspired
   scoring unless we later add true externally calibrated false-alarm control.

## Claims to avoid in the paper

- "first calibrated TTS method"
- "first statistically valid TTS method"
- "first sequential TTS method"
- "first adaptive code selection method"
- "breaks the resampling ceiling" as a universal statement

Those are all broader than the current evidence supports.

## Safer paper framing

Prefer language like:

- "We study execution-grounded sequential falsification for code generation."
- "We show agreement-based selection can fail badly on reasoning-oriented code
  models, and that active elimination recovers much of the oracle gap."
- "Our current confidence score is testing-inspired and evaluated empirically;
  we do not claim a fully anytime-valid guarantee without external calibration."
- "The contribution is strongest as a code-focused elimination framework,
  baseline surface, and failure diagnosis for TTS selection."

## What would strengthen novelty further

1. Complete the adaptive-vs-non-adaptive baseline matrix.
2. Complete the HumanEval proxy rows.
3. Complete full LiveCodeBench / broader math coverage.
4. Replace local proxy baselines with canonical external implementations where
   feasible.
5. Add an externally calibrated false-alarm layer if we want stronger
   statistical claims.

## Practical recommendation

For a NeurIPS main submission, the paper should lead with:

- the failure of majority-vote style agreement on reasoning-oriented code models
- execution-grounded falsification as the selection alternative
- strong 32B HumanEval+ and strong 14B MBPP+ rows
- adaptive-vs-generated-test evidence

and treat calibration/theory as a careful supporting contribution rather than a
maximal "first ever" claim.
