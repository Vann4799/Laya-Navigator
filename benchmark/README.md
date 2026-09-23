# Benchmark

Keep benchmark data separate from training data. Report app-held-out and workflow-held-out results, not only random split accuracy.

## Initial local baseline

The first 10 synthetic records were run through `convaiinnovations/laya` on CPU. The observed smoke result was:

```text
page_state: 0.60
goal:       0.90
next_action:0.70
```

The Laya package also emitted a warning that one checkpoint temperature was outside its valid range and that affected confidence values should be treated as uncalibrated. Calibration is therefore a required benchmark step after fine-tuning.

## Mind2Web public baseline

On a 25-record smoke sample from normalized Mind2Web transitions, base Laya reached:

```text
next_action accuracy: 0.44 (11/25)
```

This is a smoke baseline, not a final benchmark. The public-data adapter should be evaluated on a larger app-held-out split after fine-tuning.
