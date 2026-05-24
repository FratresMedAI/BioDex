# Example images

Place 2–3 sample camera trap images in this folder for manual testing with BioDex.

## Suggested test image

You can download a known-good sample from the MegaDetector project:

https://github.com/agentmorris/MegaDetector/raw/main/images/orinoquia-thumb-web.jpg

This image contains one animal and is useful for verifying that detection and bounding boxes work correctly.

## Guidelines

- Use JPG or PNG format
- Do not commit large image datasets to the repository
- Avoid images with identifiable people if sharing the repo publicly
- Camera trap images from your own field work are ideal for realistic testing

## What to check

After placing images here, run `python app.py` from the project root and upload each image to confirm:

1. Animals are detected with reasonable bounding boxes
2. Blank/empty images are flagged correctly
3. CSV and annotated PNG exports download successfully
