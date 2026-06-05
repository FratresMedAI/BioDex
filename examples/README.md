# Example images

**Not the product demo.** Local users should use folder batch workflows. The files here are **smoke-test / spot-check thumbs only** (6 images).

Two tiers of local data:

| Location | Purpose | Size |
|----------|---------|------|
| `examples/` | UI spot-check + single-image smoke test | 6 MegaDetector thumbs |
| `~/.cache/biodex/channel-islands-demo/` | **Realistic batch** (LILA Channel Islands) | ~72 camera-trap frames |

## Realistic batch data (recommended for CLI and UI)

Not stored in git. Download once on any local machine:

```bash
python -m scripts.demo_batch --prepare-only
biodex batch ~/.cache/biodex/channel-islands-demo \
  -o ./results --classify-species --recursive
```

Example output (threshold 0.25): **~72 images**, **~237 animals**, **~47 frames with 2+ animals**, per-frame counts up to **16** in dense timelapse frames.

A few LILA metadata URLs 404; the downloader skips them and still delivers a full set.

Use this cache for **Load LILA cache** in the field-review UI, or point `biodex batch` at your own folder of JPG/PNG images.

## UI thumbs (`examples/`)

```bash
python scripts/fetch_examples.py
```

Downloads **6** MegaDetector demo JPGs for the collapsed **Single-image spot check** panel and `scripts/smoke_test.py`. These are **not** representative of batch volume — use the LILA cache above for that.

| File | Description |
|------|-------------|
| `sample.jpg` | Ocelot — single-image default |
| `channel_islands.jpg` | Channel Islands wildlife |
| `idaho.jpg` | Idaho camera traps |
| `nacti.jpg` | NACTI sample |
| `pheasant.jpg` | Pheasant / bird detection |
| `timelapse.jpg` | Timelapse recognition |

See [`manifest.json`](manifest.json) for UI sample metadata.

## Guidelines

- Use JPG or PNG format for your own folders
- Do not commit large image datasets to the repository
- Avoid images with identifiable people if sharing publicly
