from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from microstructure_segmentation import generate_microstructure, save_benchmark, plot_metrics
s=generate_microstructure(); rows=save_benchmark(s, ROOT/"data"/"segmentation_benchmark.csv"); plot_metrics(rows, ROOT/"figures"/"metrics_summary_ru.png", ru=True)
print("metrics written")
