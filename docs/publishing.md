# Publishing BioDex to PyPI

The `Release` workflow (`.github/workflows/release.yml`) builds the wheel + sdist on every
`v*` tag and publishes to PyPI using **Trusted Publishing** (OIDC) — no API tokens stored in
the repo.

## Why the v1.0.0 publish job failed

The first `v1.0.0` run built artifacts successfully but the `publish` job failed with:

```
Trusted publishing exchange failure:
* `invalid-publisher`: valid token, but no corresponding publisher
  (Publisher with matching claims was not found)
```

This is **not** a code or workflow bug. It means PyPI does not yet have a Trusted Publisher
registered that matches these OIDC claims from the workflow:

| Claim | Value |
|-------|-------|
| repository | `FratresMedAI/BioDex` |
| workflow | `release.yml` |
| environment | `pypi` |

Until that registration exists, the publish step cannot mint an upload token. The build and
GitHub Release steps are unaffected (artifacts are already attached to the GitHub Release).

## One-time fix: register the Trusted Publisher on PyPI

Do this once with the PyPI account that should own the `biodex` project.

### If the project does NOT exist on PyPI yet (pending publisher)

1. Sign in at https://pypi.org and go to **Your account → Publishing**.
2. Under **Add a new pending publisher**, fill in exactly:
   - **PyPI Project Name:** `biodex`
   - **Owner:** `FratresMedAI`
   - **Repository name:** `BioDex`
   - **Workflow name:** `release.yml`
   - **Environment name:** `pypi`
3. Save. The first successful tag push will create the project and publish.

### If the project already exists on PyPI

1. Go to `https://pypi.org/manage/project/biodex/settings/publishing/`.
2. **Add a new publisher** with the same five values listed above.

> The values must match the workflow exactly. The environment is `pypi` because the
> `publish` job declares `environment: pypi`.

## GitHub side (optional but recommended)

Create a GitHub Environment named `pypi` so deployments are gated/audited:

1. Repo **Settings → Environments → New environment → `pypi`**.
2. Optionally add required reviewers or a tag-pattern deployment branch rule (`v*`).

## Re-run the publish after registering

The workflow uses `skip-existing: true`, so it is safe to re-run.

```bash
# Re-run just the failed release workflow for the existing tag:
gh run rerun <run-id>            # find the id with: gh run list --workflow Release

# …or cut a patch release that re-triggers the whole pipeline:
#   bump BIODEX_VERSION in core/types.py, commit, then:
git tag -a v1.0.1 -m "BioDex v1.0.1" && git push origin v1.0.1
```

## Manual publish fallback (if you don't want OIDC)

You can publish from a local build with an API token instead:

```bash
python -m build
twine check dist/*
twine upload dist/*        # prompts for __token__ / pypi-... API token
```

Use this only as a stopgap; Trusted Publishing is the supported path and keeps no secrets in
the repo.
