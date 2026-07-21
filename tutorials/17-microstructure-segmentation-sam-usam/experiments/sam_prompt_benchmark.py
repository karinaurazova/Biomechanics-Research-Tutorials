from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from microstructure_segmentation import generate_microstructure, save_benchmark
s=generate_microstructure(); rows=save_benchmark(s, ROOT/"data"/"segmentation_benchmark.csv")
print([r["method"] for r in rows if r["method"].startswith("sam")])
