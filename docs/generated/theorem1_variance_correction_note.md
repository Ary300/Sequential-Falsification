# Theorem 1 Variance-Correction Note

This note estimates the empirical size of theorem-1's posterior-variance correction on benchmark-conditioned conflict slices.
Because the public benchmark rows do not expose a directly observed posterior over retrieval reliability, the estimate uses the benchmark-conditioned synthetic scaffold with a fixed reference model and computes the correction in absolute KL units.

## Headline

- Reference model: `Qwen/Qwen2.5-14B-Instruct`
- Max examples per benchmark: `512`
- Score bins per benchmark: `4`
- Mean empirical correction KL: `1e-06` nat
- Max empirical correction KL: `1.4e-05` nat
- All bins below `0.02` nat: `True`
- All bins below `0.10` nat: `True`

## conflictbank

- Mean empirical correction KL: `0.0` nat
- Max empirical correction KL: `0.0` nat
- Mean second-order proxy: `0.001668` nat
- Max `Var(r|c)` across score bins: `0.005661`

| Bin | Examples | Mean score | Mean `r` | `Var(r|c)` | Mean logit-gap^2 | Second-order proxy (nat) | Empirical correction KL (nat) |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 128 | 0.4661 | 0.6760 | 0.003404 | 0.1025 | 0.000175 | 0.000000 |
| 2 | 128 | 0.7009 | 0.7342 | 0.005661 | 0.2695 | 0.000763 | 0.000000 |
| 3 | 128 | 0.8397 | 0.7844 | 0.004194 | 1.0161 | 0.002131 | 0.000000 |
| 4 | 128 | 0.9396 | 0.8405 | 0.002120 | 3.3974 | 0.003601 | 0.000000 |

## faitheval

- Mean empirical correction KL: `0.0` nat
- Max empirical correction KL: `1e-06` nat
- Mean second-order proxy: `0.001239` nat
- Max `Var(r|c)` across score bins: `0.006333`

| Bin | Examples | Mean score | Mean `r` | `Var(r|c)` | Mean logit-gap^2 | Second-order proxy (nat) | Empirical correction KL (nat) |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 128 | 0.1428 | 0.6209 | 0.004432 | 1.6094 | 0.003566 | 0.000001 |
| 2 | 128 | 0.3422 | 0.6612 | 0.006333 | 0.1793 | 0.000568 | 0.000000 |
| 3 | 128 | 0.5295 | 0.7194 | 0.004835 | 0.0280 | 0.000068 | 0.000000 |
| 4 | 128 | 0.7500 | 0.7776 | 0.002408 | 0.6261 | 0.000754 | 0.000000 |

## memotrap

- Mean empirical correction KL: `0.0` nat
- Max empirical correction KL: `0.0` nat
- Mean second-order proxy: `0.000874` nat
- Max `Var(r|c)` across score bins: `0.004266`

| Bin | Examples | Mean score | Mean `r` | `Var(r|c)` | Mean logit-gap^2 | Second-order proxy (nat) | Empirical correction KL (nat) |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 128 | 0.3186 | 0.6797 | 0.003687 | 0.3394 | 0.000626 | 0.000000 |
| 2 | 128 | 0.5583 | 0.7066 | 0.004249 | 0.0389 | 0.000083 | 0.000000 |
| 3 | 128 | 0.7366 | 0.7636 | 0.004266 | 0.4030 | 0.000860 | 0.000000 |
| 4 | 128 | 0.8946 | 0.8306 | 0.001847 | 2.0876 | 0.001928 | 0.000000 |

## nq_swap

- Mean empirical correction KL: `3e-06` nat
- Max empirical correction KL: `1.4e-05` nat
- Mean second-order proxy: `0.003412` nat
- Max `Var(r|c)` across score bins: `0.005859`

| Bin | Examples | Mean score | Mean `r` | `Var(r|c)` | Mean logit-gap^2 | Second-order proxy (nat) | Empirical correction KL (nat) |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 128 | 0.0987 | 0.6670 | 0.005445 | 4.0855 | 0.011124 | 0.000014 |
| 2 | 128 | 0.2752 | 0.6960 | 0.005859 | 0.3686 | 0.001080 | 0.000000 |
| 3 | 128 | 0.4615 | 0.7374 | 0.004758 | 0.0265 | 0.000063 | 0.000000 |
| 4 | 128 | 0.7330 | 0.7973 | 0.003917 | 0.7051 | 0.001381 | 0.000000 |

## wikicontradict

- Mean empirical correction KL: `0.0` nat
- Max empirical correction KL: `0.0` nat
- Mean second-order proxy: `0.001361` nat
- Max `Var(r|c)` across score bins: `0.004965`

| Bin | Examples | Mean score | Mean `r` | `Var(r|c)` | Mean logit-gap^2 | Second-order proxy (nat) | Empirical correction KL (nat) |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 128 | 0.3596 | 0.7093 | 0.004615 | 0.2643 | 0.000610 | 0.000000 |
| 2 | 128 | 0.6199 | 0.7507 | 0.004692 | 0.1000 | 0.000235 | 0.000000 |
| 3 | 128 | 0.7949 | 0.7998 | 0.004965 | 0.6919 | 0.001718 | 0.000000 |
| 4 | 128 | 0.9363 | 0.8793 | 0.001522 | 3.7845 | 0.002881 | 0.000000 |

## Read

- On this benchmark-conditioned conflict scaffold, the variance correction is tiny in absolute KL units.
- That is the empirically relevant answer for the abstract claim: the exact theorem lives in the log-linear family, but the correction term is far below the scale that would force a body-level qualifier here.
- This does not make the exactness assumption magically true outside the family. It does show that the empirically induced gap from collapsing `r` to its mean is negligible on the conflict slices we actually care about.
