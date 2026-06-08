# Contributing to BioDex

Thanks for helping improve BioDex.

## Development setup

```bash
pip install -e ".[ui,models,dev]"
pre-commit install
```

## Quality gates (must pass)

```bash
ruff check core app.py ui desktop tests
mypy core app.py ui
pytest tests/ -v -m "not slow"
python -c "from app import build_app; build_app(); print('app ok')"
```

## Scope and standards

- Keep BioDex local-first and privacy-preserving by default.
- Preserve public API compatibility (`core/__init__.py`, CLI behavior, `build_app()` / `launch_app()`).
- Add/maintain docstrings and explicit error handling.
- Include tests for behavior changes.

## Pull request checklist

- [ ] Added or updated tests
- [ ] Updated docs/CHANGELOG when user-facing behavior changed
- [ ] Ran all quality gates locally
- [ ] Avoided unrelated refactors
