"""BioDex top-level package shim.

The implementation lives in the ``core``, ``ui``, and ``desktop`` packages.
This thin namespace re-exports the stable public surface and the version so
that ``import biodex`` and ``python -m biodex`` behave as users expect.
"""

from __future__ import annotations

from core.cli import main
from core.types import BIODEX_VERSION

__version__ = BIODEX_VERSION
__all__ = ["main", "__version__"]
