# Theorem 3 Cross-Family Verdict

- DeepSeek `7B -> 14B` ConflictBank asymmetry replicates: `True`
- Qwen `7B -> 14B` ConflictBank asymmetry replicates: `False`
- Universal cross-family asymmetry holds: `False`
- Verdict: no universal cross-family `7B recovers / 14B saturates` law.
- Strongest theorem-3 statement: benchmark-dependent two-regime behavior.

## Key Rows

| Family | Benchmark | Size | `cot=0` gap | `cot=128` gap | `cot=1024` gap | `128->1024` delta | Shape |
|---|---|---:|---:|---:|---:|---:|---|
| DeepSeek-R1-Distill-Qwen | conflictbank | 7 | 0.5505 | 0.7531 | 0.5308 | -0.2223 | peak_then_full_recovery |
| DeepSeek-R1-Distill-Qwen | conflictbank | 14 | 0.5876 | 0.9449 | 0.9513 | 0.0064 | persistent_or_saturating |
| Qwen2.5 | conflictbank | 7 | 0.9856 | 0.9849 | 0.9693 | -0.0156 | monotone_improving |
| Qwen2.5 | conflictbank | 14 | 0.9776 | 0.9731 | 0.9584 | -0.0147 | monotone_improving |
| Qwen2.5 | wikicontradict | 32 | 0.0945 | 0.3520 | 0.2635 | -0.0885 | peak_then_partial_recovery |
