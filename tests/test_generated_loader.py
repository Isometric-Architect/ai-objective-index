from pathlib import Path

import pytest

from ai_objective_index.generated_loader import (
    load_generated_objects,
    load_generated_source_traces,
)
from ai_objective_index.models import ObjectStatus


def test_loads_generated_objects() -> None:
    objects = load_generated_objects()

    assert len(objects) >= 3
    assert all(item.status == ObjectStatus.EXTRACTED_UNVERIFIED for item in objects)


def test_loads_generated_source_traces() -> None:
    traces = load_generated_source_traces()

    assert len(traces) > 0
    assert {trace.object_id for trace in traces}


def test_missing_generated_path_gives_clear_error() -> None:
    with pytest.raises(FileNotFoundError, match="Generated data file not found"):
        load_generated_objects(Path("data/generated/does_not_exist.json"))

