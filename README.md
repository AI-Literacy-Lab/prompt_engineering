# Prompt Engineering Sandbox

This project is a small prompt-engineering and evaluation setup for classifying customer support emails from an electronics retailer. It generates synthetic email examples, tests different prompt variants, and scores model output against expected labels.

## Purpose

The goal is to evaluate how well a local LLM can:

- extract order IDs from customer messages
- classify the issue category
- estimate urgency
- infer customer sentiment
- detect prompt-injection attempts and ignore malicious instructions

## Project structure

- `create_excel.py` — generates the Excel test dataset used for evaluation
- `TestData.xlsx` / `TestData_1.xlsx` — generated datasets with expected labels

- `prompting.py` and `prompting_version*.py` — iterative prompt experiments
- `prompts.yaml` — prompt templates used by the prompting scripts
- `scoring.py` — validation and scoring helpers used to parse answers and compare them with expected outputs

## Dataset format

The generated spreadsheet contains the following columns:

- `Email`
- `Expected_Order_ID`
- `Expected_Category`
- `Expected_Urgency`
- `Expected_Sentiment`
- `Must_Not_Contain`

The rows include normal support emails as well as adversarial cases such as prompt injection and malformed order references.

## Requirements

- Python 3.10+
- `openpyxl`
- `PyYAML`
- A local Ollama server with a model available, for example:

```bash
pip install openpyxl pyyaml
ollama pull gemma4:e4b
```

The scripts expect Ollama to be running at `http://localhost:11434/api/chat`.

## Quick start

1. Generate the Excel test file:

```bash
python create_excel.py
```

2. Run the scorecard or prompt experiments:

```bash
python prompt1.py
```

You can also run the individual prompting variants directly, for example:

```bash
python prompting.py
python prompting_version3.py
python prompting_version4.py
python prompting_version5.py
```

## Notes

- The project is intentionally lightweight and designed for experimentation.
- `prompts.yaml` makes it easy to edit the system messages and compare prompt quality.
- The dataset includes both ordinary support requests and intentionally tricky cases so prompt robustness can be measured.

## Typical workflow

1. Generate or update the dataset.
2. Adjust prompt wording in `prompts.yaml` or the versioned prompt files.
3. Run the model against the dataset.
4. Inspect the scorecard output to compare prompt quality and failure modes.
