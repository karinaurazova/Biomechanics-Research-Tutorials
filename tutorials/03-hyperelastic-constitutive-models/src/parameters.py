"""Synthetic parameter catalog used by Tutorial 03."""

from biomechanics_tutorials.hyperelasticity import MODEL_DEFINITIONS

SYNTHETIC_MODEL_PARAMETERS = {
    key: dict(definition.parameters) for key, definition in MODEL_DEFINITIONS.items()
}
