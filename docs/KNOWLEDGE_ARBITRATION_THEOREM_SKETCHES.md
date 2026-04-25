# Knowledge Arbitration Theorem Sketches

## Purpose

This document turns the current paper idea into explicit theorem targets.

It is not a proof archive yet. The goal is to move from "we should prove
something like X" to theorem statements that are sharp enough to guide both the
paper and the experiments.

Current status:

- Theorems are now written in a paper-usable form.
- Proofs are not yet complete.
- Experimental mappings are listed for each theorem so we can tell when the
  empirics are actually validating the theory rather than loosely gesturing at
  it.

## Shared setup

We consider a question `q`, a latent true answer `y*`, a parametric belief
distribution `p_theta(y | q)`, and a context-conditioned distribution
`p_ctx(y | q, c)`.

The context `c` is generated with latent reliability `r in [0, 1]`, and the
arbitration problem is to choose how much weight to put on parametric memory
versus retrieved context when these two sources disagree.

We write:

- `pi(y)` for the parametric prior induced by the model
- `l_c(y)` for the context likelihood contribution
- `R(a, y*)` for a loss incurred by taking action `a` when the truth is `y*`
- `a in {trust_parametric, trust_context, abstain, mix}` for possible
  arbitration actions

The theory target is not just "pick the better source." It is:

- derive the Bayes-optimal arbitration policy,
- prove that fixed trust policies are minimax-suboptimal,
- characterize when sequential chain-of-thought updates worsen calibration under
  conflict.

## Theorem 1: Bayes-Optimal Arbitration Rule

### Informal statement

If the system has a prior over context reliability and a likelihood model for
how context is generated conditional on the true answer, then the optimal
arbitration rule is a posterior-predictive mixture between parametric and
contextual beliefs with a reliability-dependent weight.

### Draft statement

Let `r` be a latent context-reliability variable with prior `pi(r)`, and assume
the answer posterior under context factorizes as:

`p(y | q, c, r) proportional to p_theta(y | q)^(1 - w(r, c)) * p_ctx(y | q, c)^(w(r, c))`

for a measurable weight function `w(r, c) in [0, 1]`. Under any strictly proper
scoring rule `S`, the Bayes-optimal arbitration policy minimizing posterior
predictive risk is:

`a*(q, c) = argmin_a E[S(a, Y) | q, c]`

and the induced predictive distribution is the posterior-reliability-weighted
mixture:

`p*(y | q, c) = integral p(y | q, c, r) p(r | q, c) dr`

In particular, if the action class is restricted to log-linear mixtures,
`p*(y | q, c)` is achieved by a reliability-adaptive weight
`w*(q, c) = E[r | q, c]` up to the calibration map induced by the likelihood
family.

### What this should predict empirically

- A Bayes-style adaptive rule should beat `always_context`,
  `always_parametric`, and fixed 50/50 interpolation on regret.
- The empirical arbitration distribution should move with observable proxies for
  reliability:
  - popularity / prior strength on `PopQA`
  - dynamicity / edit count on `DynamicQA`
  - contradiction family on `ConflictBank` and `WikiContradict`

### Current evidence

- Synthetic oracle experiments already support this direction.
- Real benchmark-backed pilots already show a strong regret ordering in favor
  of `Bayes Proxy`.

### Proof plan

1. Write the posterior-predictive decision problem under a strictly proper
   scoring rule.
2. Show that the Bayes action is the posterior expectation under the induced
   predictive distribution.
3. Restrict to the log-linear family and solve for the reliability-adaptive
   mixture weight.
4. Add an identifiability lemma tying `w*(q, c)` to observable reliability
   signals.

## Theorem 2: Fixed Policies Are Minimax-Suboptimal

### Informal statement

Any policy that always trusts context, always trusts parametric memory, or uses
one fixed global mixture weight will incur constant excess regret on some
knowledge-conflict distribution. A policy with access to a reliability signal
can do strictly better.

### Draft statement

Let `A_fixed` be the class of fixed arbitration policies:

- `always_context`
- `always_parametric`
- `constant_mix_w` for any constant `w in [0, 1]`

Assume there exist two families of conflict distributions `D_plus` and `D_minus`
such that context is reliable on `D_plus` and misleading on `D_minus`, while a
reliability signal `s(q, c)` separates the two families with error `epsilon`.

Then for every `a in A_fixed`, there exists a mixture distribution
`P_a over {D_plus, D_minus}` such that:

`Regret(a; P_a) >= c0`

for a universal constant `c0 > 0`, while there exists an adaptive policy
`a_adapt(s)` satisfying:

`Regret(a_adapt; P_a) <= c1 * epsilon`

Thus fixed trust policies are minimax-suboptimal over the conflict family.

### What this should predict empirically

- Fixed policies should have visibly worse regret than a reliability-aware
  Bayes-style rule.
- This should hold on:
  - `PopQA` prior-strength shifts
  - `DynamicQA` dynamicity shifts
  - `WikiContradict` and `ConflictBank` contradiction slices

### Current evidence

- Real benchmark-backed pilots already show:
  - `Bayes Proxy` at `0.0000` mean regret
  - `heuristic_adaptive` materially worse
  - fixed policies dramatically worse

### Proof plan

1. Construct two distributions on which opposite fixed policies fail.
2. Use a Yao-style minimax argument to lower bound the best fixed policy.
3. Show an adaptive policy using a separating reliability signal achieves regret
   proportional to the signal error.
4. Optional strengthening: add a Fano-style lemma showing no policy without
   auxiliary signal can escape the lower bound.

## Theorem 3: Conflict-Conditioned Calibration Coupling

### Informal statement

Under explicit conflict between parametric and contextual beliefs, iterative
reasoning updates can make confidence sharper faster than they make beliefs more
correct, causing calibration to worsen with longer chain-of-thought.

### Draft statement

Assume:

1. A conflict condition:
   `KL(p_theta(. | q) || p_ctx(. | q, c)) >= delta > 0`
2. A sequential reasoning process producing posteriors `p_k(y | q, c)` after
   `k` chain-of-thought steps
3. The updates are misspecified in the Berk / Grünwald sense: the true answer
   distribution is not in the family implicitly selected by the sequential
   reasoning process

Then there exists a calibration functional `C_k` such that, on the conflict
subset,

`E[C_{k+1}] - E[C_k] >= g(delta, k) - h(k)`

where `g` is positive and increases with conflict strength, while `h` captures
finite-sample noise and vanishes asymptotically.

Under a genericity condition ruling out degenerate equal-fit cases, calibration
error is strictly increasing over a non-trivial range of `k`.

### What this should predict empirically

- On conflict subsets, long CoT should worsen calibration.
- On no-conflict subsets, that degradation should disappear or reverse.
- The effect should survive deterministic decoding.

### Current evidence

- Broad pilots do **not** yet support this as a universal headline.
- The cleanest current positive slice is `WikiContradict`, where conflict ECE
  rises with long CoT while the no-conflict bucket improves.
- `ConflictBank` and `DynamicQA` currently do not match the desired direction in
  the proxy pipeline, so theorem 3 remains an open empirical target.
- The first partial real-generation run with `DeepSeek-R1-Distill-Qwen-7B`
  suggests a nearby but weaker phenomenon may be real: CoT can sharply increase
  overconfidence on hard knowledge QA even when the effect is not
  conflict-specific.

### Proof plan

1. Define a sequential posterior update model for CoT steps.
2. Map conflict-conditioned reasoning to misspecified Bayes updating.
3. Use posterior concentration under misspecification to show sharpening toward
   a KL projection rather than the truth.
4. Convert sharpening-with-misspecification into a lower bound on calibration
   degradation.
5. Add a boundary-case corollary showing why no-conflict subsets can improve.

### Fallback theorem if conflict-specificity fails

If the full real-generation runs continue to show confidence inflation without a
clear conflict/no-conflict separation, the paper should not force the original
theorem. The fallback version is:

`Theorem 3b (CoT-Induced Overconfidence on Hard Knowledge QA).`

Under misspecified sequential reasoning updates, there exists a hard-task
subset on which longer chain-of-thought increases the confidence-accuracy gap,
even when average accuracy does not improve.

This is weaker and less novel than the conflict-conditioned version, so it
should only be used if the completed real-generation matrix rules out the
sharper theorem.

### Alternate theorem if the effect is non-monotone rather than monotone

The current real-generation wave suggests a more interesting variant may be
available:

`Theorem 3c (Intermediate-CoT Overconfidence Peak).`

Under misspecified sequential reasoning updates with competing knowledge
sources, the confidence-accuracy gap need not grow monotonically with reasoning
depth. Instead, there can exist an interior reasoning budget `k* > 0` at which
overconfidence is maximized, followed by partial self-correction at longer
reasoning depths.

This version is now supported by the completed `DeepSeek-R1-Distill-Qwen-7B`
real-generation run:

- `ConflictBank` conflict gap:
  `0.5505 -> 0.7531 -> 0.5308`
- `WikiContradict` conflict gap:
  `0.2923 -> 0.4825 -> 0.4429`
- in both cases, `cot=128` is the peak-overconfidence bucket and `cot=1024`
  partially recovers relative to the peak.

If this pattern also survives the in-flight `DeepSeek-R1-Distill-Qwen-14B`
replication, it becomes the default theorem-3 landing point for the paper.

## Experimental pairing

| Theorem | Primary benchmark evidence | Current status |
| --- | --- | --- |
| Theorem 1 | `PopQA`, `DynamicQA`, synthetic oracle | early positive |
| Theorem 2 | broad real regret comparisons, `WikiContradict`, `ConflictBank` | early positive |
| Theorem 3 | `WikiContradict`, `ConflictBank`, real-trace CoT sweeps | landed in revised non-monotone form; scaling replication in flight |

## Immediate next steps

1. Turn Theorem 1 into a proof sketch with the exact decision class and loss.
2. Turn Theorem 2 into a two-distribution minimax lower bound.
3. Replicate Theorem 3c on `DeepSeek-R1-Distill-Qwen-14B`.
4. Add mitigation conditions:
   - parallel-chain bagging
   - confidence decoupling
   - deterministic decoding control
5. Promote the cleaned theorem statements into the paper outline now that the
   empirical theorem-3 story has a stable landing point.
