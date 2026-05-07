# NeurIPS Experimental Setup Appendix Survey

Status date: `2026-05-06`

This note answers a practical question for the paper appendix:

> What do NeurIPS papers typically include in the experimental-setup /
> hyperparameter appendix, and what should we include to look complete and
> reviewer-friendly?

The guidance below combines:

- the official NeurIPS paper checklist guidance, and
- a small sample of real NeurIPS 2024 papers and supplements.

## Official NeurIPS Requirements

The official checklist is the anchor, not taste.

From the NeurIPS paper checklist guidelines:

- the paper PDF should contain:
  1. main paper
  2. optional appendices / supplemental material
  3. the NeurIPS checklist
- the checklist does **not** count toward the page limit
- for experiments, NeurIPS explicitly asks whether the paper specifies:
  - training details
  - data splits
  - hyperparameters
  - how hyperparameters were chosen
  - statistical significance / error bars
  - compute resources
- the important details should be in the main paper, while full details can be
  in the appendix, supplement, or code release
- for reproducibility, NeurIPS also wants:
  - code / data / instructions when possible
  - exact commands and environment if code is released

Practical interpretation:

- the main paper should contain the experimental story at a level that lets a
  reviewer understand the result
- the appendix should contain the exhaustive setup details that would let a
  reader reproduce the work without guesswork

Official source:
- [NeurIPS Paper Checklist Guidelines](https://nips.cc/public/guides/PaperChecklist)

## What Sampled NeurIPS Papers Actually Do

I sampled a few NeurIPS 2024 papers and looked for how they divide material
between the main paper and appendices.

### 1. `Superposed Decoding` (NeurIPS 2024)

Source:
- [NeurIPS proceedings paper page](https://papers.nips.cc/paper_files/paper/2024/file/d74f9efa1d8ca30b31d65cef8de7c2bf-Paper-Conference.pdf)

What it includes in the main paper:

- exact base model: `Llama-2-7B`
- GPU setup:
  - one `A40` GPU for most experiments
  - eight `A40` GPUs for perplexity evaluations
- batch size: `1`
- external corpus used to build n-gram models:
  - `200,000` RedPajama documents
  - about `200M` tokens
- storage footprint of auxiliary artifacts:
  - about `14 GB` total n-gram storage
- evaluation dataset and split:
  - OpenWebText test split
  - `5,000` documents
- prompt / generation setup:
  - first `15` tokens used as prefix
  - `k=3` drafts
  - `10` generated tokens
- hyperparameter selection policy:
  - selects interpolation weight `alpha` and temperature `tau` on validation
    data
- says explicitly that exact hyperparameter values are listed in `Appendix B`
- says robustness ablations for prefix length, generation length, and number of
  drafts appear in `Appendix E`

Takeaway:

- good NeurIPS papers often put the **core experimental knobs directly in the
  main paper**
- the appendix then holds the exhaustive hyperparameter table and robustness
  sweeps

### 2. `UQ-Guided Hyperparameter Optimization for Iterative Learners` (NeurIPS 2024)

Source:
- [NeurIPS proceedings paper PDF](https://proceedings.neurips.cc/paper_files/paper/2024/file/010c5ba0cafc743fece8be02e7adb8dd-Paper-Conference.pdf)

What it includes in the main paper:

- benchmark family and setup references in Section `4.1`
- unit of budget:
  - one training epoch
- total HPO budget:
  - `4 hours` per method by default
- says more benchmark/task information is in `Appendix F`
- includes appendix pseudocode for the actual algorithmic variants

Takeaway:

- even for algorithm papers, the main text usually states:
  - what counts as budget
  - total compute budget
  - benchmark family
- appendices then carry:
  - benchmark specifics
  - extra algorithm detail / pseudocode
  - expanded setup tables

### 3. `OPERA` (NeurIPS 2024)

Source:
- [NeurIPS proceedings paper PDF](https://papers.nips.cc/paper/2024/file/bba9be4bc526c5d515a9d3c16ccfe138-Paper-Conference.pdf)

What it illustrates:

- method papers still foreground:
  - what tasks are used
  - what estimator families / baselines are compared
  - which choices are treated as hyperparameters
- the experimental setup burden is not just “training hyperparameters”; it also
  includes:
  - estimator choices
  - selection rules
  - bootstrap / resampling procedures
  - constrained optimization details when the method itself has tuning knobs

Takeaway:

- if the method has meta-choices, calibration parameters, estimator pools, or
  decoding policies, those belong in the experimental setup appendix too

## Common Pattern Across NeurIPS Papers

Across the official checklist and sampled papers, the common appendix pattern is:

1. Experimental overview in main paper
2. Full setup details in appendix
3. Exact hyperparameters in one table or one subsection
4. Selection / tuning procedure explicitly explained
5. Compute budget and hardware explicitly stated
6. Extra ablations and robustness sweeps in appendix
7. Reproducibility artifacts linked at the end

## What Reviewers Expect To Find In An Experimental Setup Appendix

If this material is missing, reviewers often mark the checklist item weak even
when the results are good.

### A. Datasets and Splits

Include:

- dataset names
- version / snapshot date if relevant
- licenses if relevant
- number of examples per split
- exact train / validation / test split policy
- any filtering, deduplication, exclusion, or “kept examples” criteria
- prompt construction or retrieval context construction
- benchmark-specific preprocessing

### B. Models and Checkpoints

Include:

- exact model names
- checkpoint versions / commits / release tags
- whether models are base, instruct, distilled, merged, LoRA, RLHF, etc.
- tokenizer version
- max context / max sequence length used
- precision / quantization mode
- any non-default inference or training backend settings

### C. Training Hyperparameters

Include:

- optimizer
- learning rate
- scheduler
- warmup
- weight decay
- batch size
- gradient accumulation
- number of epochs or total steps
- early stopping criterion
- gradient clipping
- dropout if applicable
- seed(s)
- mixed precision / bf16 / fp16 / fp32
- LoRA / PEFT settings if used:
  - rank
  - alpha
  - target modules
  - dropout

### D. Decoding / Inference Hyperparameters

For LM papers this is mandatory.

Include:

- temperature
- top-p
- top-k
- beam size
- max new tokens
- stop criteria
- repetition penalties
- sampling vs greedy vs beam
- system prompt / no-system-prompt policy
- reasoning scaffold or answer-format scaffold
- any benchmark-specific decoding overrides

### E. Hyperparameter Search Procedure

This is one of the most commonly omitted but reviewer-important items.

Include:

- which hyperparameters were tuned
- search ranges
- search method:
  - grid
  - random
  - Bayesian
  - hand-tuned
- tuning budget
- validation metric used for selection
- whether the same ranges were used across models / benchmarks
- whether reported values are best-on-validation, fixed-beforehand, or defaults

Good phrasing to include:

- “We tuned `alpha` and `tau` on the validation split.”
- “All reported main-table results use the same fixed hyperparameters unless
  explicitly stated.”
- “For each family, we selected the checkpoint by minimum validation Brier.”

### F. Statistical Reporting

Include:

- number of seeds
- whether results are mean / median / best seed / pooled
- confidence intervals or error bars
- bootstrap procedure if used
- sign tests / e-values / permutation tests if used
- exact definition of the headline metric

### G. Compute and Runtime

NeurIPS explicitly asks for this.

Include:

- GPU / TPU / CPU type
- number of devices
- memory
- cluster vs cloud
- wall-clock runtime
- approximate storage footprint if material
- total budget per sweep if relevant

### H. Baselines

Include:

- exact baseline implementations
- whether they are from official code or your reimplementation
- any deviations from the original paper
- whether baselines were re-tuned or run with published defaults

### I. Reproducibility Hooks

Include:

- code repository URL or anonymized release
- exact commands or scripts
- environment / package versions
- where configs live
- where generated result files live

## Best-Practice Appendix Structure

For a NeurIPS empirical paper, a strong appendix structure usually looks like:

1. `Experimental Setup`
2. `Datasets and Splits`
3. `Models and Checkpoints`
4. `Training Hyperparameters`
5. `Inference / Decoding Hyperparameters`
6. `Hyperparameter Search and Model Selection`
7. `Baselines and Implementation Details`
8. `Metrics and Statistical Testing`
9. `Compute Resources and Runtime`
10. `Additional Ablations`
11. `Qualitative Examples`
12. `Reproducibility Checklist / Artifact Pointers`

## Recommended Table Set

If you want the appendix to feel “NeurIPS-complete,” include these tables:

1. Dataset table
   - dataset
   - split sizes
   - filtering
   - evaluation metric

2. Model table
   - family
   - checkpoint
   - tokenizer
   - context length
   - precision

3. Training hyperparameter table
   - optimizer
   - lr
   - batch
   - epochs / steps
   - warmup
   - wd
   - seed(s)

4. Inference hyperparameter table
   - temperature
   - top-p
   - max tokens
   - decoding mode
   - prompt protocol

5. Hyperparameter search table
   - tuned variable
   - candidate range
   - selection metric
   - final chosen value

6. Compute table
   - experiment
   - hardware
   - devices
   - wall time
   - peak memory if available

## What We Should Include In Our Paper

For this project specifically, the appendix should definitely contain:

- benchmark-by-benchmark split construction
- exact theorem-3 evaluation prompt / decoding settings
- matched-base training settings for `SFT`, `DPO`, `GRPO`
- DeepSeek-native vs generic eval protocol differences
- `eta` selection procedure and search grid
- multiseed aggregation method and bootstrap CI procedure
- compute table for:
  - matched-family runs
  - free-form `n≈200` runs
  - dense `rho*` trajectory runs
- exact file / script pointers for each major result family

## Bottom Line

If you want the appendix to feel complete to NeurIPS reviewers, make sure it
contains all of:

- data splits
- preprocessing
- checkpoints
- training hyperparameters
- inference hyperparameters
- tuning ranges and selection rules
- seeds and statistical tests
- compute budget and hardware
- baseline implementation details
- exact reproducibility hooks

That is the recurring pattern across both the official checklist and actual
NeurIPS papers: the main paper explains the experiment, while the appendix
removes guesswork.
