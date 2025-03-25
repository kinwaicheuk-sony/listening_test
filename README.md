## Overview
Given the folders `SteerEdit_demo_flac` and `SteerMusic_demo_flac` containing the audio examples.

The audio filename itself indicates the model that it is generated, such as `dds.flac`, `ZETA.flac`, and `musicmagus.flac`.

`generate_test_questions*.py` generates the questions based on the folders, and save the questions in `audio_questions*.json`.

Then the questions are manually copied to `audio_questions.json`.

`listening_app.py` load the questions from `audio_questions.json`.

The collected responses will be saved in `user_ratings`.

The answer can be analyzed by `result_analysis.py`.

## Question generator

`generate_test_questions*.py` supports question shuffling based on `shuffled_question_numbers`.

It also supports questions exclusion based on `exclude_samples`.

`selection_control` shuffles the answer order per question. It is based on the following two variables.

```python
AUDIO_TYPE_MAP = {
    "dds": 0,
    "ddim": 1,
    "musicmagus": 2,
    "sdedit": 3,
    "zeta": 4,
}

selection_control = [[0, 2], [4, 0]]
```

In this case, it means the first questions will have (`dds`, `musicmagus`) as the answers and (`zeta`, `dds`) as the answer.

## Result analysis

`result_analysis.py` parases the ground truths from `audio_questions*.json` and returns the perference (in %) to the proposed method over the two selected baselines.

`ground_truth_extractor*.py` are created before question shuffling, so they might not be useful in the latest version.

## Hosting
```bash
streamlit run listening_app.py --server.port 8502
```