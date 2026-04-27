import pytest
from openharness.src.framework.harness import ValidationHarness

def test_harness_initialization():
    harness = ValidationHarness()
    assert isinstance(harness, ValidationHarness)
