from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from microstructure_segmentation import generate_microstructure, all_methods, plot_methods
s=generate_microstructure(); plot_methods(s, ROOT/"figures"/"method_comparison_ru.png", ru=True)
print(sorted(all_methods(s)))
