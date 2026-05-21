from __future__ import annotations

import re
import shutil
from pathlib import Path

import pytest


@pytest.fixture
def tmp_path(request):
    """Workspace-local temp fixture for this Windows repo.

    The default user temp root can inherit restrictive ACLs in this desktop
    environment, so tests use an ignored workspace folder instead.
    """

    root = Path("aoi_test_tmp")
    root.mkdir(exist_ok=True)
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", request.node.nodeid)[-120:]
    target = root / safe_name
    resolved_root = root.resolve()
    resolved_target = target.resolve() if target.exists() else (root / safe_name).absolute()
    if target.exists() and resolved_root in resolved_target.parents:
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)
    return target
