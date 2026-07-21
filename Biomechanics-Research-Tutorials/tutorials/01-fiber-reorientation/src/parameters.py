"""Default parameters used by Tutorial 01 experiments."""

from dataclasses import dataclass


@dataclass(frozen=True)
class BaselineCase:
    initial_degrees: float = -50.0
    target_degrees: float = 30.0
    rate: float = 0.35
    duration: float = 20.0
    time_step: float = 0.01
