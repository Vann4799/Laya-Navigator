# Training Plan

## v0.1 tasks

1. Page state classification
2. Goal classification
3. Next-action prediction

## Data target

Start with 5,000 train, 1,000 validation, and 1,000 test records. Expand only after the end-to-end pipeline and benchmark are reproducible.

## Split policy

Use app/workflow holdouts where possible. Do not rely only on random splits because repeated web templates and syndicated trajectories can leak across splits.

## Model policy

Use the official Laya typed-decision fine-tuning path. Do not assume a generic causal-LLM QLoRA recipe applies to Laya's encoder/typed-decision architecture.

## Benchmark

Compare the unfine-tuned base model against the adapter on:

- macro-F1 for page state
- macro-F1 for goal
- top-1 next-action accuracy
- calibration/confidence
- latency
- abstention/error cases
