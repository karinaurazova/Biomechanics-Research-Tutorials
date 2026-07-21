import matplotlib.pyplot as plt
import numpy as np

from biomechanics_tutorials.mechanical_homeostasis import ConstituentTurnoverParameters, simulate_constituent_turnover, survival_fraction
from common import palette_cycle, save_figure, title, tr

time = np.linspace(0.0, 50.0, 1601)
error = 0.18 * np.exp(-((time - 12.0) / 8.0) ** 2)
constituents = [
    ConstituentTurnoverParameters("collagen", 0.60, 24.0, 1.7, 0.1, 1.08),
    ConstituentTurnoverParameters("smooth muscle", 0.28, 10.0, 1.2, 0.2, 1.05),
    ConstituentTurnoverParameters("ground matrix", 0.12, 4.0, 0.7, 0.3, 1.00),
]
result = simulate_constituent_turnover(time, error, constituents)
ages = np.linspace(0.0, 40.0, 400)

for language in ("en", "ru"):
    names_ru = {"collagen": "коллаген", "smooth muscle": "гладкие мышцы", "ground matrix": "основной матрикс"}
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    for color, row, name in zip(palette_cycle(), range(len(constituents)), result["names"], strict=False):
        label = name if language == "en" else names_ru[name]
        axes[0].plot(time, result["mass"][row], color=color, label=label)
        axes[1].plot(ages, survival_fraction(ages, constituents[row].half_life), color=color, label=label)
    axes[0].set_xlabel(tr("time", language))
    axes[0].set_ylabel(tr("mass", language))
    axes[1].set_xlabel("Constituent age" if language == "en" else "Возраст компонента")
    axes[1].set_ylabel("Survival fraction" if language == "en" else "Доля сохранившегося компонента")
    axes[0].legend(fontsize=8)
    axes[1].legend(fontsize=8)
    fig.suptitle(title("constituent_turnover", language))
    fig.tight_layout()
    save_figure(fig, "constituent_turnover", language)
