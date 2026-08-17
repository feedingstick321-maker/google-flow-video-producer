---
name: google-flow-video-producer
description: Produce complete videos in the Google Flow web app from storyboards, reference frames, websites, scripts, or creative briefs. Use when Codex must plan shots, adapt image-to-video prompts, control a logged-in Flow session, budget Google AI credits, generate clips with Gemini Omni Flash or Veo models, preserve character continuity, download results, assemble MP4 files with audio, or compare multiple Flow models.
---

# Google Flow Video Producer

Create a traceable, credit-aware video pipeline around the Google Flow web app. Use one persistent browser session for all Flow work and deterministic local scripts for assembly and inspection.

## Load prerequisites

1. Read and follow the installed `playwright-interactive` skill before browser work.
2. Read [references/browser-playbook.md](references/browser-playbook.md) before interacting with Flow.
3. Read [references/flow-models.md](references/flow-models.md) before estimating credits or selecting a model.
4. Read [references/pipeline-schema.md](references/pipeline-schema.md) when creating or resuming a production.

Never call Gemini API or Vertex AI when the user asks to spend subscription Flow credits. Those APIs use separate billing.

## Production workflow

### 1. Establish the source of truth

- Read every supplied brief, prompt document, storyboard caption, and locked visual rule.
- Treat canonical storyboard images as immutable first frames unless the user asks to revise them.
- Preserve supplied wording for non-negotiable character, object, text, and color constraints.
- Record source URLs and local paths in `pipeline.json`.
- When a source already contains per-shot prompts, adapt them minimally instead of rewriting the creative intent.

### 2. Create the production package

Create a dedicated project directory with:

```text
project/
  source/
    storyboard/
    assets/
    documents/
  production/
    pipeline.json
    prompts.md
    credit-budget.json
    qa-report.md
  outputs/
    <model>/clips/
    <model>/final.mp4
```

Use the schema and state transitions in [references/pipeline-schema.md](references/pipeline-schema.md). Never overwrite a downloaded source clip; retries receive `-r02`, `-r03`, and so on.

### 3. Plan shots and model variants

- Keep one shot per generation. Do not ask Flow for a multi-shot video when a storyboard defines individual cuts.
- Use Frames-to-Video with the storyboard PNG as the first frame.
- Match the requested target duration to the model's supported duration. Generate the next longer supported duration and trim locally when needed.
- For a target longer than the model supports, prefer a model-supported extension. If extension would change the requested model comparison, generate the longest native clip and apply a restrained editorial retime only to slow, continuous shots.
- Set outputs per prompt to `1` unless the user explicitly budgets variants.
- Keep prompts in English for model reliability, but preserve required visible Korean text exactly and include a non-mutation guard.

### 4. Gate credit spending

Before the first paid generation:

1. Open Flow with the intended Google account.
2. Read the visible remaining credit balance.
3. Open generation settings and read the current per-generation cost for the selected model and duration.
4. Compute the model-by-model subtotal, expected total, and retry reserve.
5. Show the user the balance and estimate if they have not already approved the same model, shot count, duration plan, and expected total.

Treat an explicit request made after seeing the estimate as approval. Reconfirm if the current Flow UI cost is higher, the output count changes, or expected usage exceeds the approved total by more than 10%.

### 5. Operate Flow

- Keep one headed Playwright browser/context/page alive for the entire production.
- On Windows, prefer Google Chrome for Flow authentication and production. Launch a normal Chrome process with a dedicated persistent profile, then attach Playwright over CDP; this avoids the Google sign-in rejection sometimes triggered by browsers launched directly through automation.
- Never extract, print, copy, or persist passwords, session cookies, or tokens.
- If sign-in is required, pause and let the user complete it manually.
- Confirm the active account and credit balance without exposing unrelated account details.
- Use semantic locators based on current visible labels and roles. Reinspect after every UI transition; do not rely on stale element references or locale-specific hardcoded selectors.
- Select the mode, model, aspect ratio, duration, and output count before every batch or whenever Flow changes a compatible model automatically.
- Confirm that the Frames tab itself is active; an attached image in Assets mode is not an immutable first frame.
- Upload the exact first-frame file and verify its filename and natural pixel dimensions against the canonical source before generating.
- Enter the approved prompt, verify the cost shown by Flow, then generate.
- Treat a cleared prompt editor as insufficient proof of submission. Require a queued/progress card or a new backend workflow record before recording the request as submitted.
- Wait for a completed result card. Download the chosen result and rename it to the shot ID plus attempt number.
- When a result card's model label is ambiguous, verify the historical model, duration, status, media ID, and image input in Flow project metadata. Never infer the result's model from the current creation-panel default.
- Update `pipeline.json` immediately after submission, completion, download, rejection, or failure.

### 6. Review every clip

Check the first, middle, and last frames of every output. Reject or flag clips with:

- character duplication, face drift, costume drift, or changed props;
- broken anatomy, split bodies, unexpected limbs, or unintended subjects;
- mutated required text or additional text overlays;
- a different camera action from the prompt;
- a visible jump, frozen tail, corrupted frame, watermark issue, or wrong aspect ratio;
- missing or unusable audio when audio was requested.

Retry only the failed shot. Keep the original prompt and add one short correction that names the observed defect. Do not silently consume repeated retries.

### 7. Assemble and inspect

Run:

```bash
python <skill-dir>/scripts/assemble_video.py --manifest <project>/production/assemble-<model>.json --output <project>/outputs/<model>/final.mp4
python <skill-dir>/scripts/inspect_video.py <project>/outputs/<model>/final.mp4
```

The assembly script preserves audio, adds silence only for clips without audio, normalizes to H.264/AAC stereo, trims requested durations, and can gently slow a shorter continuous clip to its target duration. Use hard cuts by default for storyboard montage continuity.

Complete `qa-report.md` with shot coverage, rejected attempts, actual credit use, final duration, resolution, frame rate, audio stream status, and any intentional deviations.

## Safety and reliability rules

- Do not bypass Flow quotas, rate limits, safety filters, or account controls.
- Stop repeated automation when Flow reports unusual activity or rate limiting; preserve pipeline state and resume later.
- Do not run parallel browser agents against the same Flow account or project.
- Do not delete Flow projects, assets, source files, or failed attempts unless the user explicitly asks.
- Keep a 10% credit reserve when the user has not specified another retry budget.
- Report partial completion honestly when Flow, the network, or the account prevents finishing all shots.
