# Colab notebooks

The first notebook will:

1. install the official Laya training dependencies;
2. load normalized workflow records;
3. run the base-model baseline;
4. fine-tune the supported typed-decision adapter;
5. evaluate base vs adapter;
6. save the adapter and benchmark report.

## Official Laya training reference

Use the official browser-agent fine-tuning path as the implementation reference:

https://github.com/NandhaKishorM/laya/blob/main/docs/finetune_browser_agent.md

Important constraints:

- Laya is a typed-decision encoder, not a generic causal chat model.
- Browser-agent training predicts an operation plus a target element using typed choices.
- Do not assume a generic QLoRA/Llama recipe applies.
- The official reference reports single-GPU training on a 16 GB card and a separate 2x T4 notebook; a single Colab Free T4 may require the smaller multilingual checkpoint, fewer candidates, shorter sequences, or a reduced experiment.
- Keep calibration and app-held-out evaluation in the notebook.
