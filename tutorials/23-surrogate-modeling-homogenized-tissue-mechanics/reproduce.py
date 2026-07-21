from __future__ import annotations

import csv
import json
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import PillowWriter, FuncAnimation


def _find_repository_root(start: Path) -> Path:
    current = start.resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "src" / "biomechanics_tutorials").exists():
            return candidate
    raise RuntimeError("Could not locate repository root containing src/biomechanics_tutorials.")


REPOSITORY_ROOT = _find_repository_root(Path(__file__))
SOURCE_DIRECTORY = REPOSITORY_ROOT / "src"
if str(SOURCE_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIRECTORY))

from biomechanics_tutorials.surrogate_modeling import (  # noqa: E402
    active_learning_trace,
    bootstrap_ensemble,
    ensemble_predict,
    extrapolation_grid,
    fit_ridge_surrogate,
    generate_surrogate_dataset,
    learning_curve,
    predict,
    regression_metrics,
    structural_to_stiffness,
    train_test_split,
)

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
FIGURES = HERE / "figures"
ANIMATIONS = HERE / "animations"
for p in [DATA, FIGURES, ANIMATIONS]:
    p.mkdir(exist_ok=True)


def save_csv(path: Path, header: list[str], rows: np.ndarray) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows.tolist())


def labels(lang: str) -> dict[str, str]:
    if lang == "ru":
        return {
            "pipeline": "Surrogate pipeline для гомогенизированной механики",
            "design": "Design space",
            "parity": "Parity plot: predicted vs true",
            "true": "Истинное значение",
            "pred": "Прогноз",
            "residual": "Абсолютная ошибка по stiffness",
            "rho": "Доля волокон",
            "por": "Пористость",
            "error": "Ошибка",
            "learning": "Learning curve",
            "ntrain": "Число обучающих симуляций",
            "rmse": "RMSE",
            "active": "Active learning trace",
            "step": "Шаг",
            "r2": "R²",
            "uncertainty": "Bootstrap uncertainty",
            "surface": "Surrogate surface: C11",
            "value": "Значение",
        }
    return {
        "pipeline": "Surrogate pipeline for homogenized mechanics",
        "design": "Design space",
        "parity": "Parity plot: predicted vs true",
        "true": "True value",
        "pred": "Prediction",
        "residual": "Absolute stiffness error",
        "rho": "Fiber fraction",
        "por": "Porosity",
        "error": "Error",
        "learning": "Learning curve",
        "ntrain": "Number of training simulations",
        "rmse": "RMSE",
        "active": "Active learning trace",
        "step": "Step",
        "r2": "R²",
        "uncertainty": "Bootstrap uncertainty",
        "surface": "Surrogate surface: C11",
        "value": "Value",
    }


def plot_pipeline(lang: str) -> None:
    lab = labels(lang)
    suffix = "_ru" if lang == "ru" else ""
    fig, ax = plt.subplots(figsize=(11.5, 4.2))
    ax.axis("off")
    steps = [
        "microstructure\nfeatures" if lang == "en" else "признаки\nмикроструктуры",
        "expensive\nRVE/FE solve" if lang == "en" else "дорогой\nRVE/FE расчёт",
        "training\ndataset" if lang == "en" else "обучающая\nвыборка",
        "surrogate\nmodel" if lang == "en" else "surrogate\nмодель",
        "fast stress /\nstiffness prediction" if lang == "en" else "быстрый прогноз\nжёсткости/напряжений",
    ]
    xs = np.linspace(0.08, 0.92, len(steps))
    for x, s in zip(xs, steps):
        ax.add_patch(plt.Rectangle((x-0.075,0.42),0.15,0.24,fill=False,lw=2))
        ax.text(x,0.54,s,ha="center",va="center",fontsize=10)
    for a,b in zip(xs[:-1], xs[1:]):
        ax.annotate("", xy=(b-0.085,0.54), xytext=(a+0.085,0.54), arrowprops=dict(arrowstyle="->", lw=2))
    ax.set_title(lab["pipeline"], fontsize=14)
    fig.tight_layout()
    fig.savefig(FIGURES / f"surrogate_pipeline{suffix}.png", dpi=180)
    plt.close(fig)


def plot_design(dataset) -> None:
    for lang in ["en", "ru"]:
        lab = labels(lang); suffix = "_ru" if lang == "ru" else ""
        fig, ax = plt.subplots(figsize=(6.2, 5.0))
        sc = ax.scatter(dataset.features[:,2], dataset.features[:,3], c=dataset.features[:,1], s=18, alpha=0.75)
        ax.set_xlabel(lab["rho"]); ax.set_ylabel(lab["por"]); ax.set_title(lab["design"])
        cb=fig.colorbar(sc, ax=ax); cb.set_label("kappa" if lang=="en" else "kappa")
        fig.tight_layout(); fig.savefig(FIGURES / f"design_space{suffix}.png", dpi=180); plt.close(fig)


def plot_parity(y_true, predictions: dict[str, np.ndarray]) -> None:
    for lang in ["en", "ru"]:
        lab = labels(lang); suffix = "_ru" if lang == "ru" else ""
        fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.2))
        targets = [(0, "C11"), (3, "C66"), (6, "sxx")]
        for ax, (j, name) in zip(axes, targets):
            for model_name, pred in predictions.items():
                ax.scatter(y_true[:,j], pred[:,j], s=12, alpha=0.55, label=model_name)
            mn = min(y_true[:,j].min(), *(p[:,j].min() for p in predictions.values()))
            mx = max(y_true[:,j].max(), *(p[:,j].max() for p in predictions.values()))
            ax.plot([mn,mx],[mn,mx], lw=1.5)
            ax.set_title(name); ax.set_xlabel(lab["true"]); ax.set_ylabel(lab["pred"])
        axes[0].legend(fontsize=8)
        fig.suptitle(lab["parity"])
        fig.tight_layout(); fig.savefig(FIGURES / f"parity_and_error_summary{suffix}.png", dpi=180); plt.close(fig)


def plot_error_surface(model) -> None:
    xg = extrapolation_grid(n=65)
    true = structural_to_stiffness(xg[:,:5])[:,0]
    pred = predict(model, xg)[:,0]
    err = np.abs(pred - true).reshape(65,65)
    value = pred.reshape(65,65)
    rho = xg[:,2].reshape(65,65); por = xg[:,3].reshape(65,65)
    for lang in ["en", "ru"]:
        lab = labels(lang); suffix = "_ru" if lang == "ru" else ""
        fig, axes = plt.subplots(1,2,figsize=(11,4.6))
        im0=axes[0].imshow(value, origin='lower', aspect='auto', extent=[rho.min(),rho.max(),por.min(),por.max()])
        axes[0].set_title(lab["surface"]); axes[0].set_xlabel(lab["rho"]); axes[0].set_ylabel(lab["por"]); fig.colorbar(im0,ax=axes[0])
        im1=axes[1].imshow(err, origin='lower', aspect='auto', extent=[rho.min(),rho.max(),por.min(),por.max()])
        axes[1].set_title(lab["residual"]); axes[1].set_xlabel(lab["rho"]); axes[1].set_ylabel(lab["por"]); fig.colorbar(im1,ax=axes[1])
        fig.tight_layout(); fig.savefig(FIGURES / f"surrogate_surface_and_error{suffix}.png", dpi=180); plt.close(fig)


def plot_learning_and_active(curve, active) -> None:
    for lang in ["en", "ru"]:
        lab = labels(lang); suffix = "_ru" if lang == "ru" else ""
        fig, ax = plt.subplots(figsize=(6.5,4.5))
        ax.plot(curve[:,0], curve[:,1], marker='o')
        ax.set_xlabel(lab["ntrain"]); ax.set_ylabel(lab["rmse"]); ax.set_title(lab["learning"]); ax.grid(True, alpha=0.3)
        fig.tight_layout(); fig.savefig(FIGURES / f"learning_curve{suffix}.png", dpi=180); plt.close(fig)
        fig, ax = plt.subplots(figsize=(6.5,4.5))
        ax.plot(active[:,0], active[:,2], marker='o', label='RMSE')
        ax2 = ax.twinx(); ax2.plot(active[:,0], active[:,3], marker='s', label='R2')
        ax.set_xlabel(lab["step"]); ax.set_ylabel('RMSE'); ax2.set_ylabel(lab["r2"]); ax.set_title(lab["active"]); ax.grid(True, alpha=0.3)
        fig.tight_layout(); fig.savefig(FIGURES / f"active_learning_trace{suffix}.png", dpi=180); plt.close(fig)


def plot_uncertainty(x_test, mean, sd) -> None:
    for lang in ["en", "ru"]:
        lab=labels(lang); suffix="_ru" if lang=="ru" else ""
        fig, axes=plt.subplots(1,2,figsize=(11,4.3))
        sc=axes[0].scatter(x_test[:,2], x_test[:,3], c=sd[:,0], s=18)
        axes[0].set_xlabel(lab['rho']); axes[0].set_ylabel(lab['por']); axes[0].set_title(lab['uncertainty'] + ' C11'); fig.colorbar(sc, ax=axes[0])
        sc2=axes[1].scatter(x_test[:,0]*180/np.pi, x_test[:,1], c=sd[:,6], s=18)
        axes[1].set_xlabel('theta, deg' if lang=='en' else 'theta, град'); axes[1].set_ylabel('kappa'); axes[1].set_title(lab['uncertainty'] + ' sxx'); fig.colorbar(sc2, ax=axes[1])
        fig.tight_layout(); fig.savefig(FIGURES / f"bootstrap_uncertainty{suffix}.png", dpi=180); plt.close(fig)


def make_gifs(curve, active) -> None:
    fig, ax = plt.subplots(figsize=(6,4))
    def update(i):
        ax.clear(); ax.plot(curve[:i+1,0], curve[:i+1,1], marker='o'); ax.set_xlim(curve[:,0].min()*0.9, curve[:,0].max()*1.05); ax.set_ylim(0, curve[:,1].max()*1.15); ax.set_xlabel('training simulations'); ax.set_ylabel('RMSE'); ax.set_title('Surrogate learning curve'); ax.grid(True, alpha=0.3)
    anim=FuncAnimation(fig, update, frames=len(curve), interval=450)
    anim.save(ANIMATIONS/'surrogate_learning_curve.gif', writer=PillowWriter(fps=2))
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(6,4))
    def update2(i):
        ax.clear(); ax.plot(active[:i+1,1], active[:i+1,2], marker='o'); ax.set_xlim(active[:,1].min()*0.9, active[:,1].max()*1.05); ax.set_ylim(0, active[:,2].max()*1.15); ax.set_xlabel('selected expensive simulations'); ax.set_ylabel('holdout RMSE'); ax.set_title('Active learning uncertainty loop'); ax.grid(True, alpha=0.3)
    anim=FuncAnimation(fig, update2, frames=len(active), interval=450)
    anim.save(ANIMATIONS/'active_learning_uncertainty.gif', writer=PillowWriter(fps=2))
    plt.close(fig)


def main() -> None:
    dataset = generate_surrogate_dataset(950, seed=23, noise_level=0.0015)
    np.savez(DATA / 'surrogate_modeling_dataset.npz', features=dataset.features, targets=dataset.targets, feature_names=np.array(dataset.feature_names), target_names=np.array(dataset.target_names))
    train_idx, test_idx = train_test_split(dataset.features.shape[0], train_fraction=0.72, seed=2)
    models = {
        'linear': fit_ridge_surrogate(dataset.features[train_idx], dataset.targets[train_idx], basis='linear', ridge=1e-5),
        'quadratic': fit_ridge_surrogate(dataset.features[train_idx], dataset.targets[train_idx], basis='quadratic', ridge=3e-5),
        'random-features': fit_ridge_surrogate(dataset.features[train_idx], dataset.targets[train_idx], basis='random-features', ridge=8e-5),
    }
    rows=[]; predictions={}
    for name, model in models.items():
        pred = predict(model, dataset.features[test_idx]); predictions[name]=pred
        m = regression_metrics(dataset.targets[test_idx], pred)
        rows.append([name, m['rmse'], m['mae'], m['r2'], m['mean_relative_error']])
    with (DATA/'model_metrics.csv').open('w', newline='', encoding='utf-8') as f:
        writer=csv.writer(f); writer.writerow(['model','rmse','mae','r2','mean_relative_error']); writer.writerows(rows)
    curve = learning_curve(dataset, basis='quadratic')
    save_csv(DATA/'learning_curve.csv', ['n_train','rmse','mae','r2','mean_relative_error'], curve)
    active = active_learning_trace(dataset.features, dataset.targets)
    save_csv(DATA/'active_learning_trace.csv', ['step','n_selected','rmse','r2'], active)
    ens = bootstrap_ensemble(dataset.features[train_idx], dataset.targets[train_idx], n_models=14, seed=8)
    mean, sd = ensemble_predict(ens, dataset.features[test_idx])
    save_csv(DATA/'bootstrap_uncertainty_summary.csv', ['mean_sd_C11','mean_sd_C22','mean_sd_C12','mean_sd_C66','mean_sd_C16','mean_sd_C26','mean_sd_sxx','mean_sd_syy','mean_sd_sxy'], np.mean(sd, axis=0, keepdims=True))
    for lang in ['en','ru']:
        plot_pipeline(lang)
    plot_design(dataset)
    plot_parity(dataset.targets[test_idx], predictions)
    plot_error_surface(models['quadratic'])
    plot_learning_and_active(curve, active)
    plot_uncertainty(dataset.features[test_idx], mean, sd)
    make_gifs(curve, active)
    summary = {'tutorial': 23, 'n_samples': int(dataset.features.shape[0]), 'best_model_by_rmse': min(rows, key=lambda r: r[1])[0], 'targeted_outputs': list(dataset.target_names)}
    (DATA/'benchmark_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2))

if __name__ == '__main__':
    main()
