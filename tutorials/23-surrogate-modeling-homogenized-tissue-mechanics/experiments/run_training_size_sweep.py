from pathlib import Path
import sys
ROOT = Path(__file__).resolve()
for p in [ROOT, *ROOT.parents]:
    if (p / 'src' / 'biomechanics_tutorials').exists():
        sys.path.insert(0, str(p / 'src'))
        break
from biomechanics_tutorials.surrogate_modeling import generate_surrogate_dataset, learning_curve

d = generate_surrogate_dataset(1200, seed=42)
print(learning_curve(d, train_sizes=(20,40,80,160,320,640)))
