# Laya Navigator

Workflow decision adapter built on the Laya model family.

Laya Navigator does not generate code or control a browser. It converts a compact application state into typed workflow decisions:

```text
page state + goal + history → next action + confidence
```

## v0.1 scope

- State classification
- Goal classification
- Next-action prediction
- Career/workflow-style web tasks from public and synthetic datasets
- Reproducible Colab training
- Base-vs-fine-tuned benchmark
- Small inference API

## Dataset policy

Raw third-party datasets are downloaded by scripts and are not redistributed by this repository. Each source has a license/attribution record under `dataset/licenses/`.

Current sources:

- MiniWoB++ — MIT
- WebArena repository/task resources — Apache-2.0; verify any linked third-party site data separately
- Mind2Web — dataset card identifies CC BY 4.0; attribution required
- Synthetic workflows — generated in this repository

## Project layout

```text
src/laya_navigator/     preprocessing and inference package
schemas/                input/output contracts
dataset/                source downloads, normalized data, and manifests
training/               configs, Colab notebooks, checkpoints, adapters
benchmark/              evaluation scripts and reports
api/                    inference service
docs/                   design and licensing notes
tests/                  unit and integration tests
```

## Planned workflow

```text
public trajectories + synthetic workflows
        ↓
compact state normalization
        ↓
train/validation/test split by app and workflow
        ↓
Laya fine-tuning
        ↓
base vs adapter benchmark
        ↓
API + Hugging Face adapter release
```

## Local setup

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
```

Training runs in Google Colab. Local code handles preprocessing, evaluation, and inference.
