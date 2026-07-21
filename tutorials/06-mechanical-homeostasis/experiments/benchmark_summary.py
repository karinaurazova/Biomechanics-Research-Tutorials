import csv
import matplotlib.pyplot as plt
import numpy as np

from biomechanics_tutorials.mechanical_homeostasis import HomeostasisParameters, generate_load_protocol, homeostasis_metrics, simulate_scalar_homeostasis
from common import DATA_DIRECTORY, save_figure, title

time = np.linspace(0.0, 30.0, 3001)
load = generate_load_protocol(time, "step", amplitude=0.50, onset=3.0)
cases = [
    ("baseline", HomeostasisParameters(adaptation_rate=0.30)),
    ("slow", HomeostasisParameters(adaptation_rate=0.10)),
    ("dead_zone", HomeostasisParameters(adaptation_rate=0.30, dead_zone=0.10)),
    ("saturated", HomeostasisParameters(adaptation_rate=0.30, response_limit=0.16)),
    ("delay", HomeostasisParameters(adaptation_rate=0.55, delay=2.0)),
    ("sensor_bias", HomeostasisParameters(adaptation_rate=0.30, sensor_bias=0.10)),
    ("capacity_limit", HomeostasisParameters(adaptation_rate=0.30, capacity_max=1.30)),
]
rows = []
for name, params in cases:
    result = simulate_scalar_homeostasis(time, load, parameters=params)
    active = time >= 3.0
    metrics = homeostasis_metrics(time[active], result["true_error"][active])
    rows.append({"scenario": name, **metrics})
DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)
with (DATA_DIRECTORY / "homeostasis_benchmark.csv").open("w", newline="", encoding="utf-8") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)

for language in ("en", "ru"):
    labels_ru = {"baseline": "база", "slow": "медленно", "dead_zone": "мёртвая зона", "saturated": "насыщение", "delay": "задержка", "sensor_bias": "ошибка сенсора", "capacity_limit": "предел"}
    labels = [row["scenario"] if language == "en" else labels_ru[row["scenario"]] for row in rows]
    x = np.arange(len(rows))
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))
    axes[0].bar(x, [row["iae"] for row in rows])
    axes[0].set_xticks(x, labels, rotation=30, ha="right")
    axes[0].set_ylabel("Integrated absolute error" if language == "en" else "Интегральная абсолютная ошибка")
    axes[1].bar(x, [row["final_abs_error"] for row in rows])
    axes[1].set_xticks(x, labels, rotation=30, ha="right")
    axes[1].set_ylabel("Final absolute error" if language == "en" else "Конечная абсолютная ошибка")
    fig.suptitle(title("benchmark_summary", language))
    fig.tight_layout()
    save_figure(fig, "benchmark_summary", language)
