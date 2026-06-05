# Example images

Sample camera trap images for BioDex demos and manual testing.

## Quick setup

```powershell
python scripts/fetch_examples.py
```

This downloads **6** MegaDetector demo images (~6 JPGs) into this folder. Images are **not** committed to git — only URLs and manifest metadata live in the repo.

| File | Description |
|------|-------------|
| `sample.jpg` | Ocelot — single-image **Try Demo** default |
| `channel_islands.jpg` | Channel Islands wildlife |
| `idaho.jpg` | Idaho camera traps |
| `nacti.jpg` | NACTI sample |
| `pheasant.jpg` | Pheasant / bird detection |
| `timelapse.jpg` | Timelapse recognition (dense detections) |

Together these images support the **LinkedIn batch demo** (`scripts/batch_smoke.py`) with aggregate stats across multiple animals.

## Manifest

See [`manifest.json`](manifest.json) for sample metadata used by the **Try Demo** and **Load sample image** buttons.

## Batch demo

```bash
python scripts/fetch_examples.py
python scripts/batch_smoke.py --species
```

## Guidelines

- Use JPG or PNG format
- Do not commit large image datasets to the repository
- Avoid images with identifiable people if sharing publicly
- Camera trap images from your own field work are ideal for realistic testing
