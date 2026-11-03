# Code for "Weight-space programming, reproduced"

- `apply_edit.py`: applies the final edit (`../data/edit_compact.json`, 47 KB) to `Qwen/Qwen3.5-0.8B`.
- `modal_app.py`: everything that ran on GPUs (Modal, H100): generation with vLLM using the MIT post's protocol, grading with math-verify, and the diagnosis passes that collect hidden states on the model's own traces. Entry points: `eval_edits`, `diag_main`, `diag_doubt`.
- `make_edit.py`: turns a diagnosis into an edit (contrast direction, attribution to MLP neurons, strength alpha) and its random-direction control.
- `compare.py`: accuracy table and exact McNemar tests between arms.

The final edit combines:
- `make_edit.py --pos onset --neg pre --res-layer 21 --alpha 8` (layers 15 and 19)
- `make_edit.py --pos doubt --neg progress --res-layer 19 --alpha 4` (layers 16 and 18)

Modal credentials are read from the environment (`MODAL_TOKEN_ID`, `MODAL_TOKEN_SECRET`). Nothing secret is stored in these files.
