# Paper 2 Proxy Follow-Ups

This note runs the fastest Paper 2 follow-ups on top of the benchmark-backed arbitration scaffold using explicit local benchmark variants.

## Poisoned Context

These rows test whether the Bayes-style arbitration weight drops on adversarial conflict passages faster than CAD/AdaCAD/Self-RAG.

| Source benchmark | Condition | Bayes weight | CAD weight | AdaCAD weight | Self-RAG weight | Bayes regret | CAD regret |
|---|---|---:|---:|---:|---:|---:|---:|
| clasheval | aligned_context | 0.9011 | 0.7910 | 0.8279 | 0.7826 | -0.5890 | -0.4587 |
| clasheval | conflict_context | 0.3058 | 0.6963 | 0.4175 | 0.0170 | 0.3448 | 1.1714 |
| conflictbank | aligned_context | 0.9011 | 0.7910 | 0.8279 | 0.7135 | -0.5890 | -0.4587 |
| conflictbank | conflict_context | 0.3058 | 0.6963 | 0.4175 | 0.0170 | 0.3448 | 1.1714 |
| nq_swap | aligned_context | 0.9011 | 0.7910 | 0.8279 | 0.7524 | -0.5890 | -0.4587 |
| nq_swap | conflict_context | 0.3058 | 0.6963 | 0.4175 | 0.0170 | 0.3448 | 1.1714 |
| ramdocs | aligned_context | 0.9011 | 0.7910 | 0.8279 | 0.7185 | -0.5890 | -0.4587 |
| ramdocs | conflict_context | 0.3058 | 0.6963 | 0.4175 | 0.0170 | 0.3448 | 1.1714 |

## Reliability Ablation

- Spearman(noise rate, Bayes context weight): `-1.0`

| Noise rate | Policy | Mean context weight | Accuracy | Mean regret |
|---:|---|---:|---:|---:|
| 0.00 | bayes_proxy | 0.9417 | 1.0000 | -0.6330 |
| 0.00 | cad | 0.8335 | 1.0000 | -0.5110 |
| 0.00 | adacad | 0.8781 | 1.0000 | -0.5632 |
| 0.00 | self_rag | 0.8809 | 1.0000 | -0.5663 |
| 0.25 | bayes_proxy | 0.7851 | 1.0000 | -0.4510 |
| 0.25 | cad | 0.7174 | 1.0000 | -0.3610 |
| 0.25 | adacad | 0.7233 | 1.0000 | -0.3692 |
| 0.25 | self_rag | 0.6597 | 1.0000 | -0.2750 |
| 0.50 | bayes_proxy | 0.5788 | 1.0000 | -0.1443 |
| 0.50 | cad | 0.6123 | 1.0000 | -0.2027 |
| 0.50 | adacad | 0.5703 | 1.0000 | -0.1308 |
| 0.50 | self_rag | 0.4196 | 0.0000 | 0.1926 |
| 0.75 | bayes_proxy | 0.3812 | 0.0000 | 0.2896 |
| 0.75 | cad | 0.5177 | 1.0000 | -0.0349 |
| 0.75 | adacad | 0.4301 | 0.0000 | 0.1561 |
| 0.75 | self_rag | 0.2322 | 0.0000 | 0.8246 |
| 1.00 | bayes_proxy | 0.1838 | 0.0000 | 1.0117 |
| 1.00 | cad | 0.4327 | 0.0000 | 0.1445 |
| 1.00 | adacad | 0.2840 | 0.0000 | 0.5685 |
| 1.00 | self_rag | 0.0302 | 0.0000 | 2.9841 |

## Multi-Document Conflict Scaling

| Conflicting docs | Policy | Mean context weight | Accuracy | Mean regret |
|---:|---|---:|---:|---:|
| 2 | bayes_proxy | 0.3534 | 1.0000 | 0.4159 |
| 2 | cad | 0.6207 | 0.0000 | 0.9491 |
| 2 | adacad | 0.4329 | 1.0000 | 0.5471 |
| 2 | self_rag | 0.1210 | 1.0000 | 0.1088 |
| 4 | bayes_proxy | 0.3288 | 1.0000 | 0.3785 |
| 4 | cad | 0.6207 | 0.0000 | 0.9491 |
| 4 | adacad | 0.4169 | 1.0000 | 0.5192 |
| 4 | self_rag | 0.0885 | 1.0000 | 0.0725 |
| 8 | bayes_proxy | 0.2967 | 1.0000 | 0.3318 |
| 8 | cad | 0.6207 | 0.0000 | 0.9491 |
| 8 | adacad | 0.3953 | 1.0000 | 0.4827 |
| 8 | self_rag | 0.0560 | 1.0000 | 0.0374 |

## Read

- The poisoned-context slice is the safety-facing one: if Bayes proxy drops the context weight sharply on `conflict_context` while CAD stays high, that is the direct poisoned-retrieval story.
- The reliability-ablation slice is the T1-facing one: we want the Bayes weight to move monotonically with controlled context corruption rather than staying flat.
- The multi-document scaling slice is the production-shape one: it tests whether arbitration remains helpful as conflicting passages accumulate.
