# Example images

Sample camera trap images for BioDex demos and manual testing.

## Quick setup

```powershell
python scripts/fetch_examples.py
```

This downloads the MegaDetector ocelot sample to `sample.jpg` — a known-good image for detection and species classification (~99% Ocelot).

## Manifest

See [`manifest.json`](manifest.json) for sample metadata used by the **Try Demo** and **Load sample image** buttons.

## Guidelines

- Use JPG or PNG format
- Do not commit large image datasets to the repository
- Avoid images with identifiable people if sharing publicly
- Camera trap images from your own field work are ideal for realistic testing
