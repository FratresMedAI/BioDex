# BioDex

**Local AI for wildlife camera traps.** Detect animals, filter blanks, identify species, export results — on your machine, not in the cloud.

---

## Run locally (do this)

**Mac / Linux**

```bash
git clone https://github.com/FratresMedAI/BioDex.git
cd BioDex
./run_biodex.sh
```

**Windows**

```bat
git clone https://github.com/FratresMedAI/BioDex.git
cd BioDex
run_biodex.bat
```

Your browser opens **http://127.0.0.1:7860**. Upload a folder of images → **Process Folder**.

First analysis downloads models once (~500 MB). After that, everything stays offline on your computer.

---

## Try online (limited preview)

**[Open the demo on Hugging Face](https://huggingface.co/spaces/Fratres-X-AI/BioDex)** — quick look in your browser only.

- Max **30 images** per batch
- **No** ZIP export
- Runs on shared servers — **not private**

For real work with your own data, use **Run locally** above.

---

<details>
<summary><strong>Power users — batch CLI</strong></summary>

For large folders (100+ images), no browser:

```bash
./run_biodex.sh   # install once, then in another terminal:
source .venv/bin/activate
biodex batch /path/to/images -o ./results --classify-species --recursive
```

</details>

<details>
<summary><strong>Developers</strong></summary>

```bash
pip install -e ".[ui,models,dev]"
pytest tests/ -v -m "not slow"
ruff check core app.py ui demo
```

</details>

<details>
<summary><strong>Problems?</strong></summary>

| Problem | Fix |
|---------|-----|
| Script won't run (Mac/Linux) | `chmod +x run_biodex.sh` then try again |
| Python not found | Install Python 3.10–3.12 from python.org |
| Install fails | Delete `.venv` folder and run the script again |

</details>

---

MIT License. Uses [MegaDetector](https://github.com/agentmorris/MegaDetector) and [SpeciesNet](https://github.com/google/cameratrapai).
