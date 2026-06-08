# BioDex demo guide (v1.0)

## Quick start

```bash
./run_biodex.sh          # Mac/Linux
run_biodex.bat           # Windows
```

Opens **http://127.0.0.1:7860** with tabbed UI.

## Recommended demo flow

1. **Dashboard** — read How It Works
2. **Batch** — click **Load LILA cache**, then **Quick demo** (~10 frames, species on)
3. Click a row in the frame table to review detections
4. **Export** — Master CSV, Wildlife Insights, or EcoSentinel JSON
5. **Analytics** — Refresh from last batch for diversity metrics
6. **Video** (optional) — upload a short MP4; requires `pip install biodex[video]`

## CLI batch demo

```bash
biodex batch examples/ -o ./demo-out --classify-species --recursive
biodex video clip.mp4 -o ./video-out --fps 1
```

## Screenshots

Add captures to `docs/screenshots/` for README and LinkedIn posts.
