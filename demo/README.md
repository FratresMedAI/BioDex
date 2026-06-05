---
title: BioDex Demo
emoji: 🦊
colorFrom: red
colorTo: red
sdk: gradio
sdk_version: 5.0.0
app_file: app.py
pinned: false
license: mit
---

# LIMITED DEMO — not the full app

**Max 30 images · No ZIP · Not private · [Run locally on GitHub](https://github.com/FratresMedAI/BioDex)**

---

## Deploy to Hugging Face (3 steps)

1. **New Space** → Gradio → connect repo `FratresMedAI/BioDex`
2. **Settings → Repository → Subdirectory:** `demo`
3. **Save** — Space builds from `requirements.txt` automatically

Turn on **Auto-sync from GitHub** so future pushes to `demo/` update the Space.

First boot downloads models (~500 MB) — cold start can take 5–15 minutes.

---

## Test locally

From repo root (after `./run_biodex.sh` once):

```bash
./demo/run_demo.sh
```

Windows: `demo\run_demo.bat`
