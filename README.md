# Google Flow Video Producer

A Codex skill for producing storyboard-driven videos in the Google Flow web app through a logged-in Chrome session. It plans shots, preserves reference-frame continuity, tracks Flow credit usage, downloads results, and assembles/inspects MP4 outputs locally.

## What this is

This repository contains the custom Flow-specific orchestration skill. Browser control is provided by Playwright; Google Flow is operated through its web interface rather than an unofficial API.

## Safety

- Never include browser profiles, cookies, tokens, passwords, or downloaded media in this repository.
- Sign in manually in a dedicated Chrome profile and attach automation through CDP.
- Respect Flow quotas, rate limits, safety filters, and account controls.

## Install in Codex

Copy this directory into your Codex skills directory as `google-flow-video-producer`, then ensure the `playwright-interactive` skill is available for browser work.

## License

The custom skill instructions and scripts in this repository are released under the MIT License. Playwright remains separately licensed by Microsoft under Apache-2.0.
