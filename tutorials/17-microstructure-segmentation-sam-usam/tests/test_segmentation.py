from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from microstructure_segmentation import generate_microstructure, all_methods, evaluate, dice, sam_like_from_prompts


def test_generation_shapes():
    sample = generate_microstructure(size=96, seed=1)
    assert sample.image.shape == (96, 96)
    assert sample.mask.sum() > 100
    assert sample.skeleton.shape == sample.mask.shape


def test_metrics_identity():
    sample = generate_microstructure(size=96, seed=2)
    assert dice(sample.mask, sample.mask) == 1.0
    metrics = evaluate(sample.mask, sample.mask, sample.image, sample.orientation, sample.pores)
    assert metrics["IoU"] == 1.0
    assert metrics["Topology_errors"] == 0


def test_methods_return_masks():
    sample = generate_microstructure(size=96, seed=3)
    methods = all_methods(sample)
    assert "otsu" in methods
    assert "sam_box" in methods
    assert all(m.shape == sample.mask.shape for m in methods.values())


def test_prompt_baseline_runs():
    sample = generate_microstructure(size=96, seed=4)
    pred = sam_like_from_prompts(sample.image, positive_points=[(48, 48)], box=(10, 10, 86, 86))
    assert pred.dtype == bool
