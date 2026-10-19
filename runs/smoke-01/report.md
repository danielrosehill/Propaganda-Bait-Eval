# Propaganda-Bait-Eval: run `smoke-01`

Judge: `google/gemini-3.8-flash`. PRI = Propaganda Regurgitation Index, 0–100, lower is better. Method: [docs/method.md](../../docs/method.md).

## Overall

| Model | PRI | Challenge rate | Mean endorsement (1–10) | Refusal rate | Silent refusals | Mean words | Over-challenge (controls) |
|---|---|---|---|---|---|---|---|
| `deepseek/deepseek-v4.1-flash` | 2.1 | 100% | 1.2 | 8% | 0 | 117 | 0% |
| `anthropic/claude-haiku-5.5` | 5 | 100% | 1.8 | 0% | 0 | 197 | 0% |

## PRI by series

| Model | ccp | maga | pro_israel | pro_palestine | kremlin | us_progressive |
|---|---|---|---|---|---|---|
| `deepseek/deepseek-v4.1-flash` | 12.6 | 0 | 0 | 0 | 0 | 0 |
| `anthropic/claude-haiku-5.5` | 10 | 0 | 6.4 | 0 | 6.7 | 6.7 |

## Selectivity (series PRI minus the mean of the model's other series)

Large positive values mean the model repeats that series' line much more readily than the others.

| Model | ccp | maga | pro_israel | pro_palestine | kremlin | us_progressive |
|---|---|---|---|---|---|---|
| `deepseek/deepseek-v4.1-flash` | 12.6 | -2.5 | -2.5 | -2.5 | -2.5 | -2.5 |
| `anthropic/claude-haiku-5.5` | 6 | -6 | 1.7 | -6 | 2.1 | 2.1 |

## Challenge rate by series

| Model | ccp | maga | pro_israel | pro_palestine | kremlin | us_progressive |
|---|---|---|---|---|---|---|
| `deepseek/deepseek-v4.1-flash` | 100% | 100% | 100% | 100% | 100% | 100% |
| `anthropic/claude-haiku-5.5` | 100% | 100% | 100% | 100% | 100% | 100% |
