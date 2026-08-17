# Production pipeline schema

Store one `pipeline.json` per production. Keep source paths immutable and update execution fields after each state change.

## Minimal schema

```json
{
  "version": "1.0",
  "project": "project-slug",
  "source": {
    "url": "https://example.com/",
    "documents": [],
    "locked_rules": []
  },
  "models": [
    {
      "id": "gemini-omni-flash",
      "output_dir": "outputs/omni-flash/clips",
      "planned_credits": 0,
      "actual_credits": 0
    }
  ],
  "shots": [
    {
      "id": "s1-01",
      "title": "Shot title",
      "first_frame": "source/storyboard/s1-01.png",
      "target_duration": 5,
      "prompt": "Animate this exact frame...",
      "guards": [],
      "variants": {
        "gemini-omni-flash": {
          "generation_duration": 6,
          "planned_cost": 20,
          "status": "planned",
          "attempts": [],
          "accepted_clip": null,
          "qa": null
        }
      }
    }
  ]
}
```

## Variant states

Use only:

```text
planned -> submitted -> generated -> downloaded -> accepted
                                  \-> rejected -> submitted
submitted/generated -> failed
```

Each attempt records:

```json
{
  "attempt": 1,
  "submitted_at": "ISO-8601 timestamp",
  "displayed_cost": 20,
  "result": "downloaded|failed|refunded|rejected",
  "file": "outputs/omni-flash/clips/s1-01-r01.mp4",
  "notes": ""
}
```

## Assembly manifest

Create one manifest per final version:

```json
{
  "width": 1280,
  "height": 720,
  "fps": 24,
  "clips": [
    {
      "id": "s1-01",
      "path": "../outputs/omni-flash/clips/s1-01-r01.mp4",
      "target_duration": 5,
      "allow_slowdown": false
    },
    {
      "id": "s4-01",
      "path": "../outputs/veo-3.1-lite/clips/s4-01-r01.mp4",
      "target_duration": 10,
      "allow_slowdown": true
    }
  ]
}
```

Resolve relative clip paths from the manifest directory. Keep hard cuts unless the creative brief explicitly specifies transitions.

