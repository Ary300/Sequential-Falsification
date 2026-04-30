# Theorem 3 Trace-Separation Check

This note operationalizes Assumption 3.2 by comparing the log-likelihood of an observed reasoning trace under the model's generated answer state versus the strongest competing answer state.

- Model: `deepseek-ai/DeepSeek-R1-Distill-Qwen-14B`
- Benchmark: `conflictbank`
- Condition: `conflict_context`
- CoT length: `1024`
- Scored examples: `100`

## Headline

- Fraction where current answer state beats the strongest competing state: `0.81`
- Mean margin: `10.751257705688477`
- Median margin: `8.456539154052734`
- Mean positive margin: `13.982866828824267`
- Mean non-positive margin: `-3.025602240311472`
- Correct-example win fraction: `1.0`
- Incorrect-example win fraction: `0.8080808080808081`

## Interpretation

- A value comfortably above `0.5` means observed traces are self-confirming under the currently selected answer state more often than not.
- Positive margins indicate the generated trace is more likely under the current answer state than under the strongest competing answer state.
- The incorrect-example win fraction staying high (`0.8081`) means the mechanism is answer-state self-confirmation rather than truth-tracking.
