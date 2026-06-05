# BioDex demo guide

A short script for demonstrating BioDex to conservation researchers, land managers, or collaborators.

---

## Before the demo (5 minutes)

```powershell
cd BioDex
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python scripts/fetch_examples.py
python app.py
```

Open **http://127.0.0.1:7860**

> First run downloads MegaDetector weights (~280 MB). Species classification downloads SpeciesNet (~214 MB) when first enabled.

---

## One-click demo (30 seconds)

1. Click **Run Demo** on the **Demo Mode** tab (first tab).
2. BioDex loads the bundled ocelot sample, enables species classification, and runs analysis.
3. Point out:
   - **Original vs annotated** side-by-side view
   - Green animal box with readable label and legend
   - Stat cards (1 animal, not blank)
   - Species result: **Ocelot** at high confidence
   - Export buttons (PNG, CSV, JSON, ZIP)

**Talking point:** Everything ran locally — no cloud API, images never left the machine.

---

## Manual walkthrough (2 minutes)

1. Click **Load sample image** instead of Try Demo.
2. Explain the shared **Analysis settings** panel (threshold + species toggle).
3. Enable **species classification** and click **Analyze Image**.
4. Show the **Tier** column in the detections table (`high`, `borderline`, `uncertain`).
5. Download **Download All (ZIP)** and open the bundle.

---

## Batch demo (3 minutes)

### CLI — LinkedIn screenshot demo

```bash
python scripts/fetch_examples.py
python scripts/batch_smoke.py --species
ls -lh /tmp/biodex-batch-demo/
```

Capture the terminal block between `=== BioDex Batch Demo Summary ===` and `=== END ===`. Expected: **6 images**, **6+ animals** total, species counts, per-image animal counts, and paths to:

- `batch_summary.csv` — master detections table
- `batch_summary.json` — structured batch payload
- `batch_annotated.zip` — annotated PNGs per image

On RunPod: `bash scripts/runpod_setup.sh` runs fetch + batch smoke on GPU after install.

### UI — Batch Folder tab

1. Switch to **Batch Folder**.
2. Upload the `examples/*.jpg` set (or 3–5 local camera trap images).
3. Use the same threshold and species settings from the top panel.
4. Click **Analyze Batch**.
5. Show the per-image summary table, stat cards, and **Master CSV** / ZIP exports.

### Screenshot checklist (LinkedIn / social)

- [ ] Terminal summary with aggregate animal count and species breakdown
- [ ] `batch_summary.csv` open in a spreadsheet (filename + species columns)
- [ ] One annotated image from `batch_annotated.zip`
- [ ] Optional: Gradio batch stats panel side-by-side with terminal output

---

## Expected results (ocelot sample)

| Field | Typical value |
|-------|----------------|
| Detections | 1 animal |
| Species | Ocelot |
| Species confidence | ~0.95–0.99 |
| Tier | high |
| Blank | No |

SpeciesNet accuracy varies by region — always frame species output as a **suggestion for expert review**.

---

## Screenshot tips

1. Use the **Single Image** tab with species enabled for the most impressive annotated output.
2. Capture at least:
   - Full UI with welcome panel and Try Demo button
   - Annotated image close-up (zoom browser if needed)
   - Detections table with species tier column
3. Save PNGs to `docs/screenshots/` for README use.
4. Avoid images with identifiable people if sharing publicly.

---

## Troubleshooting during a demo

| Issue | Fix |
|-------|-----|
| Sample not found | Run `python scripts/fetch_examples.py` |
| Slow first analysis | Model weights downloading — wait and retry |
| Species disabled message | Check species toggle in Analysis settings |
| Wrong species label | Explain regional limitation; show alternatives for borderline tiers |

---

## Privacy framing (recommended closing)

BioDex is built for **biodiversity monitoring and conservation research** — defensive, protective use of AI. It helps teams triage camera trap data locally without sending sensitive field locations or imagery to the cloud.
