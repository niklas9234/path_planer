from __future__ import annotations

import pytest

from core.experiments.policy_factory import make_policy
from core.simulation import PeriodicReplanPolicy


def test_make_policy_periodic_with_interval() -> None:
    policy = make_policy("periodic", {"interval": 5})

    assert isinstance(policy, PeriodicReplanPolicy)
    assert policy.interval_ticks == 5


def test_make_policy_invalid_name_raises_clear_error() -> None:
    with pytest.raises(ValueError, match="Unknown policy 'invalid'.*event_based.*path_affected.*periodic.*static_once"):
        make_policy("invalid", {})
