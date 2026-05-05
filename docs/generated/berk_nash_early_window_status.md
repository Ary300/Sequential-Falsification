# Berk-Nash Early-Window Status

Status date: `2026-05-04`

This note records the local readiness of the early-`t` / non-asymptotic
`\\hat{\\rho}^\\star` analysis requested for Paper 2.

## What changed

- analyzer:
  [build_berk_nash_rate_empirical.py](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/build_berk_nash_rate_empirical.py)
- new CLI:
  - `--analysis-mode {tail,early}`
  - `--window-size`
- backward compatibility:
  - existing `tail` behavior remains the default
  - existing `--tail-window` still works when `--window-size` is not set

## What the early mode does

- `tail` mode:
  - analyzes the last `W` dense CoT-budget steps
  - drops the exact fixed-point endpoint from the log-TV and polynomial fits
    when that endpoint is present
- `early` mode:
  - analyzes the first `W` dense CoT-budget steps
  - applies the same local Jacobian, spectral-radius, log-TV, and polynomial
    diagnostics before the asymptotic tail regime

## New outputs

Headline JSON now records:

- `analysis_mode`
- `window_size`

Per-cell JSON now records:

- `analysis_mode`
- `analysis_window_target`
- `analysis_window_used`
- `analysis_steps`
- `analysis_start_cot`
- `analysis_end_cot`

The Markdown table now reports the analyzed window explicitly as
`start→end (count)` rather than only a tail-step count.

## Why this matters

This closes the local implementation gap for the reviewer request:

- if early-window `\\hat{\\rho}^\\star` still tracks well, that is a strong
  extension beyond the linearized tail
- if it breaks at a predictable `T_0`, that is still a useful empirical
  boundary condition rather than an uninstrumented omission

## Remaining blocker

The remaining missing ingredient is not code. It is the dense Delta trajectory
artifact needed to populate the early-window table with real `R1-14B` rows.
