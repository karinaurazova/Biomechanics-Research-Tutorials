from matplotlib import pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from common import palette_cycle, save_figure, title

for language in ("en", "ru"):
    fig, ax = plt.subplots(figsize=(12, 4.8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 4.5)
    ax.axis("off")
    labels = {
        "en": ["Mechanical load", "Mechanical stimulus", "Sensing and signaling", "Adaptation / turnover", "Tissue state"],
        "ru": ["Механическая нагрузка", "Механический стимул", "Восприятие и сигнал", "Адаптация / turnover", "Состояние ткани"],
    }[language]
    x_positions = [0.4, 2.8, 5.2, 7.6, 10.0]
    colors = palette_cycle()
    for x, label, color in zip(x_positions, labels, colors, strict=True):
        box = FancyBboxPatch((x, 2.0), 1.7, 1.0, boxstyle="round,pad=0.08", facecolor=color, alpha=0.20, edgecolor=color, linewidth=2)
        ax.add_patch(box)
        ax.text(x + 0.85, 2.5, label, ha="center", va="center", fontsize=10, wrap=True)
    for first, second in zip(x_positions[:-1], x_positions[1:], strict=True):
        ax.add_patch(FancyArrowPatch((first + 1.7, 2.5), (second, 2.5), arrowstyle="-|>", mutation_scale=16, linewidth=1.7))
    ax.add_patch(FancyArrowPatch((10.85, 1.95), (3.65, 1.15), connectionstyle="arc3,rad=-0.22", arrowstyle="-|>", mutation_scale=18, linewidth=2.0))
    feedback = "negative feedback" if language == "en" else "отрицательная обратная связь"
    ax.text(7.25, 0.75, feedback, ha="center", va="center", fontsize=12)
    disturbance = "disturbance" if language == "en" else "возмущение"
    ax.annotate(disturbance, xy=(1.25, 3.05), xytext=(1.25, 4.0), ha="center", arrowprops={"arrowstyle": "-|>"})
    ax.set_title(title("feedback_loop", language), pad=15)
    save_figure(fig, "feedback_loop", language)
