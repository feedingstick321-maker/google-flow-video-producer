# Flow model and credit reference

This reference reflects Google Flow documentation checked in August 2026. Treat the Flow UI as authoritative because models, duration support, and costs can change.

## Current subscription allocations

| Plan | Monthly Flow credits |
| --- | ---: |
| Google AI Plus | 200 |
| Google AI Pro | 1,000 |
| Google AI Ultra $100 tier | 10,000 |
| Google AI Ultra $200 tier | 25,000 |

Monthly subscription credits refresh at the billing-cycle boundary and do not roll over.

## Current video costs per generation

| Model/action | Duration | Ultra cost |
| --- | --- | ---: |
| Veo 3.1 Lite | 4s, 6s, or 8s | 5 |
| Veo 3.1 Fast | 4s, 6s, or 8s | 10 |
| Veo 3.1 Quality | 8s | 100 |
| Gemini Omni Flash | 4s | Verify in Flow UI |
| Gemini Omni Flash | 6s | 10 |
| Gemini Omni Flash | 8s | 12 |
| Gemini Omni Flash | 10s | 15 |
| Gemini Omni Flash video edit | any supported input | 40 |
| 1080p upscaling | subscriber | 0 |
| 4K upscaling | Ultra | 50 |

Costs apply per generated output, not per prompt request. A request that creates two outputs spends twice the listed amount.

The Gemini Omni Flash 6s/8s/10s figures above were verified directly in the Ultra Flow UI on 2026-08-02. Always recheck the visible price because promotional or model-rollout pricing can change independently of this file.

## Duration mapping

Use the user's target edit duration, not a blanket clip length.

| Target | Omni Flash generation | Veo Lite/Fast generation | Local edit |
| ---: | ---: | ---: | --- |
| 5s | 6s | 6s | Trim to 5s |
| 6s | 6s | 6s | None |
| 7s | 8s | 8s | Trim to 7s |
| 10s | 10s | 8s | Use a compatible extension when model fidelity permits; otherwise gently retime a slow continuous shot to 10s and disclose it |

## Budget formula

For each model:

```text
subtotal = sum(output_count × displayed_cost_for_that_shot)
expected_total = sum(model_subtotals)
retry_reserve = ceil(expected_total × 0.10)
```

Before submission, compare the calculated cost with the cost displayed in Flow settings. Use the displayed cost when they differ.

Official references:

- https://support.google.com/flow/answer/16526234
- https://support.google.com/flow/answer/16352836
- https://support.google.com/flow/answer/16353544
