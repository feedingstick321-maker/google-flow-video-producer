# Google Flow browser playbook

## Session rules

- Use a persistent headed Playwright session from the `playwright-interactive` skill.
- On Windows, use Google Chrome by default for Flow sign-in. Start a normal visible `chrome.exe` process with a dedicated Flow-only `--user-data-dir` and a local remote-debugging port, let the user sign in manually, and attach Playwright with `connectOverCDP` only after Chrome is running.
- Do not reuse the user's default Chrome profile for remote debugging. Keep the dedicated Flow profile so the authorized session can be reused for later production runs.
- Reuse one `browser`, `context`, and `page`; generation and downloads depend on session state.
- Prefer a controllable browser profile that the user has already authorized. If it is not signed in, let the user sign in manually in the visible browser.
- Never read or export cookies, local storage credentials, passwords, or OAuth tokens.
- Set `acceptDownloads: true` and a predictable project download directory.

## Google sign-in fallback

If Google shows `브라우저 또는 앱이 안전하지 않을 수 있습니다` or an equivalent unsafe-browser rejection:

1. Close the browser context launched directly by Playwright.
2. Start a normal visible Google Chrome process with a dedicated Flow-only profile and a local remote-debugging port. Do not add Playwright's automation launch flags.
3. Open Flow in that Chrome window and let the user complete sign-in manually.
4. Attach to the running browser with `chromium.connectOverCDP("http://127.0.0.1:<port>")`.
5. Reinspect the active page and continue in the attached session.

Do not attempt to bypass Google's sign-in security checks, and do not ask the user to provide credentials to Codex.

## Startup inventory

Record these checks before generation:

1. Flow home or project list is visible.
2. The intended Google account is active.
3. Remaining Flow credits are visible.
4. A new or selected project can be opened.
5. Frames-to-Video is available.
6. The requested model, aspect ratio, duration, and one-output setting are available.
7. The UI shows the expected per-generation credit cost.
8. A local first-frame file can be uploaded.

## Locator strategy

Inspect current roles and visible labels with `page.locator(...)`, `getByRole(...)`, and `getByText(...)`. Flow labels and layout change frequently and may be Korean or English.

Use this order:

1. accessible role and exact visible name;
2. label or placeholder;
3. text scoped to the active dialog or prompt panel;
4. a short stable attribute observed in the current DOM.

Avoid long CSS paths, `nth()` without a verified container, coordinates, and element handles retained across state changes.

## Per-shot transaction

1. Reinspect the active prompt panel.
2. Select Frames-to-Video.
   - Verify the Frames tab has the active/selected state; do not proceed from Assets mode.
3. Select the intended model and confirm Flow did not substitute another model.
4. Set landscape or portrait orientation, duration, and outputs=`1`.
5. Upload the canonical first-frame PNG.
   - Verify the selected media filename and natural dimensions match the source PNG.
6. Enter the shot prompt.
7. Read the displayed credit cost and compare it with the budget.
8. Submit once.
   - Confirm a progress/result card or a new project workflow record exists; prompt clearing alone is not proof.
9. Record the submission time and expected cost in `pipeline.json`.
10. Wait for the result card to complete; do not repeatedly click Generate.
    - Use project metadata to verify the completed media model code, duration, status, media ID, and image input when the card UI is ambiguous.
11. Inspect the result at normal playback speed.
12. Download the accepted clip and verify the file exists and is non-empty.
13. Record completion, actual cost, local path, and QA status.

## Failure handling

- If the prompt is rejected, record the reason and revise only the unsafe or ambiguous wording.
- If generation fails and Flow refunds the credit, wait until the restored balance is visible before recording net usage.
- If a result card remains pending, check notifications and wait; do not submit a duplicate request.
- Never classify an older result from the current creation-panel model label; that label reflects the next request, not necessarily the selected card's historical model.
- If Flow reports rate limiting or unusual activity, stop submissions and preserve state.
- If the selected model changes automatically, cancel before generation and choose a compatible mode or duration.
- If a download fails, retry the download action before regenerating the media.

## Visual QA

For every result, inspect at least three temporal positions and verify:

- storyboard composition remains recognizable;
- key characters and locked design details remain stable;
- motion follows one clear action;
- required text remains legible and unchanged;
- no extra characters, limbs, objects, or overlays appear;
- frame edges, aspect ratio, and playback are clean;
- audio is present and appropriate when requested.
