# Model Tier Map

| Tier | Model | Harness Role | Best Work | Default Complexity |
|---|---|---|---|---|
| T4 | Claude/GPT/Gemini Pro | mission architect | PDRs, mission packets, eval design, exception review | C3/C4 |
| T2 | Qwen Coder | local coder | bounded code edits, tests, refactors | C2/C3 |
| T1 | Hermes | local agentic worker | queue, handoff, mission packet execution, summaries | C1/C2 |
| T1 | Llama/Gemma | local support | docs, summaries, low-risk reasoning | C1/C2 |
| T0 | CI/tests/schemas | validation authority | pass/fail enforcement | all |

## Promotion Rule

A local model may move up only after eval evidence shows consistent pass rate, scope compliance, and CI success.
