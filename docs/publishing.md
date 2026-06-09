# Publishing BioDex to PyPI

The `Publish` workflow (`.github/workflows/publish.yml`) builds the wheel + sdist on every
`v*` tag and publishes to PyPI using **Trusted Publishing** (OIDC) — no API tokens stored in
the repo.

## Verify Trusted Publisher settings (checklist)

On **PyPI → biodex → Publishing**, the active GitHub publisher must match the workflow
**exactly**:

| Field | Required value | Common mistake |
|-------|----------------|----------------|
| **Owner** | `Fratres-X-Natura` | Old org `FratresMedAI` |
| **Repository name** | `BioDex` | `biodex` (wrong casing — must match GitHub repo name) |
| **Workflow name** | `publish.yml` | `release.yml` (old filename) |
| **Environment name** | `pypi` | `release` (that is not the environment name) |

GitHub side (already configured for this repo):

| Item | Required value |
|------|----------------|
| Actions variable | `PYPI_PUBLISH` = `true` |
| GitHub Environment | `pypi` (repo **Settings → Environments**) |

If any field is wrong, the `publish` job fails with `invalid-publisher`. Remove the bad
publisher on PyPI and re-add with the table above.

Print the expected values locally:

```bash
python scripts/verify_pypi_publisher.py
```

## Register the Trusted Publisher on PyPI

1. Go to `https://pypi.org/manage/project/biodex/settings/publishing/`.
2. **Add a new publisher** (or remove and re-add if correcting a mistake):

   - **Owner:** `Fratres-X-Natura`
   - **Repository name:** `BioDex`
   - **Workflow name:** `publish.yml`
   - **Environment name:** `pypi`

> The environment is `pypi` because the `publish` job declares `environment: pypi` in
> `.github/workflows/publish.yml`.

## Enable the publish job

The `publish` job runs when **both** are true:

1. The push is a `v*` tag, and
2. The repository variable `PYPI_PUBLISH` is set to `true`.

## Re-run publish after fixing PyPI

The workflow uses `skip-existing: true`, so it is safe to re-run.

```bash
gh run list --workflow publish.yml --limit 1
gh run rerun <run-id>
```

## Manual publish fallback

```bash
python -m build
twine check dist/*
twine upload dist/*
```
