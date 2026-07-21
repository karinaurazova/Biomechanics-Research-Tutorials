from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from microstructure_segmentation import generate_microstructure, plot_usam_stack
s=generate_microstructure(); plot_usam_stack(s, ROOT/"figures"/"usam_stack_propagation_ru.png", ru=True)
print("µSAM-like stack propagation figure written")
