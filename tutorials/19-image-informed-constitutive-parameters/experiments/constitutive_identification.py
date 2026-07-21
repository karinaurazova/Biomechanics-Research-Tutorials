from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

from common import DATA, FIGURES, write_rows
from biomechanics_tutorials.image_informed_parameters import (
    PARAMETER_NAMES,
    benchmark_calibration,
    build_synthetic_load_cases,
    build_synthetic_structural_fields,
    global_force_system,
    parameter_maps,
    solve_nonnegative_least_squares,
    structural_order_from_kappa,
    true_parameter_set,
    virtual_field_weights,
)


def _imshow(ax, image, title, label):
    im = ax.imshow(image, origin='lower')
    ax.set_title(title, fontsize=11)
    ax.set_xticks([])
    ax.set_yticks([])
    cbar = ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label(label, fontsize=9)
    return im


def save_pipeline_figure(bundle, language: str) -> None:
    structure = bundle['structure']
    first_case = bundle['load_cases'][0]
    order = structural_order_from_kappa(structure.kappa)
    titles = {
        'en': ['Fibre fraction proxy', 'Axial orientation θ', 'Concentration/order', 'DIC strain εxx'],
        'ru': ['Proxy доли волокон', 'Осевая ориентация θ', 'Концентрация / порядок', 'DIC-деформация εxx'],
    }[language]
    labels = {
        'en': ['ρf', 'radians', 'order', 'strain'],
        'ru': ['ρf', 'радианы', 'порядок', 'деформация'],
    }[language]
    fig, axes = plt.subplots(2, 2, figsize=(11.5, 8.4), constrained_layout=True)
    _imshow(axes[0, 0], structure.rho_f, titles[0], labels[0])
    _imshow(axes[0, 1], structure.theta, titles[1], labels[1])
    _imshow(axes[1, 0], order, titles[2], labels[2])
    _imshow(axes[1, 1], first_case.exx, titles[3], labels[3])
    suptitle = 'Image-derived structure becomes mechanical-model input' if language == 'en' else 'Структура из изображения становится входом механической модели'
    fig.suptitle(suptitle, fontsize=15)
    suffix = '' if language == 'en' else '_ru'
    fig.savefig(FIGURES / f'image_to_parameters_pipeline{suffix}.png', dpi=160)
    plt.close(fig)


def save_synthetic_experiment_figure(bundle, language: str) -> None:
    cases = bundle['load_cases'][:4]
    component = [case.exx for case in cases]
    titles_en = [case.name.replace('_', ' ') for case in cases]
    titles_ru = ['одноосное x, малое', 'одноосное x, большое', 'одноосное y', 'двухосное']
    titles = titles_en if language == 'en' else titles_ru
    fig, axes = plt.subplots(2, 2, figsize=(11.5, 8.4), constrained_layout=True)
    for ax, image, title in zip(axes.ravel(), component, titles):
        _imshow(ax, image, title, 'strain' if language == 'en' else 'деформация')
    fig.suptitle('Synthetic DIC strain fields for different load cases' if language == 'en' else 'Синтетические DIC-поля деформаций для разных режимов нагружения', fontsize=15)
    suffix = '' if language == 'en' else '_ru'
    fig.savefig(FIGURES / f'synthetic_experiment_fields{suffix}.png', dpi=160)
    plt.close(fig)


def save_identification_figure(bundle, language: str) -> None:
    truth = bundle['truth'].as_vector()
    results = bundle['results']
    x = np.arange(len(PARAMETER_NAMES))
    width = 0.16
    fig, ax = plt.subplots(figsize=(12.5, 7.4), constrained_layout=True)
    ax.bar(x - 2 * width, truth, width, label='truth' if language == 'en' else 'истина')
    for shift, result in zip([-width, 0.0, width, 2 * width], results):
        ax.bar(x + shift, result.parameters, width, label=result.method)
    ax.set_xticks(x)
    ax.set_xticklabels(PARAMETER_NAMES, rotation=18, ha='right')
    ax.set_ylabel('parameter value, kPa-like units' if language == 'en' else 'значение параметра, условные кПа')
    ax.set_title('Parameter recovery by different inverse workflows' if language == 'en' else 'Восстановление параметров разными обратными workflow')
    ax.legend(fontsize=9)
    suffix = '' if language == 'en' else '_ru'
    fig.savefig(FIGURES / f'inverse_identification_results{suffix}.png', dpi=160)
    plt.close(fig)


def save_parameter_maps_figure(bundle, language: str) -> None:
    maps = bundle['maps_joint']
    names = ['matrix_modulus', 'fiber_modulus', 'anisotropy_index', 'total_stiffness_index']
    titles = {
        'en': ['Matrix modulus map', 'Fibre modulus map', 'Anisotropy index', 'Total stiffness index'],
        'ru': ['Карта матричного модуля', 'Карта волоконного модуля', 'Индекс анизотропии', 'Суммарный индекс жёсткости'],
    }[language]
    fig, axes = plt.subplots(2, 2, figsize=(11.8, 8.8), constrained_layout=True)
    for ax, key, title in zip(axes.ravel(), names, titles):
        _imshow(ax, maps[key], title, 'value' if language == 'en' else 'значение')
    fig.suptitle('Spatial material maps reconstructed from image-informed parameters' if language == 'en' else 'Пространственные карты материала, восстановленные из image-informed параметров', fontsize=15)
    suffix = '' if language == 'en' else '_ru'
    fig.savefig(FIGURES / f'parameter_maps{suffix}.png', dpi=160)
    plt.close(fig)


def save_bayesian_figure(bundle, language: str) -> None:
    posterior = bundle['posterior']
    truth = bundle['truth'].as_vector()
    mean = posterior['mean']
    std = posterior['std']
    x = np.arange(len(PARAMETER_NAMES))
    fig, ax = plt.subplots(figsize=(11.5, 7.0), constrained_layout=True)
    ax.errorbar(x, mean, yerr=1.96 * std, fmt='o', capsize=6, label='posterior 95% interval' if language == 'en' else 'posterior 95% interval')
    ax.scatter(x, truth, marker='x', s=90, label='truth' if language == 'en' else 'истина')
    ax.set_xticks(x)
    ax.set_xticklabels(PARAMETER_NAMES, rotation=18, ha='right')
    ax.set_ylabel('parameter value' if language == 'en' else 'значение параметра')
    ax.set_title('Bayesian posterior uncertainty' if language == 'en' else 'Байесовская неопределённость параметров')
    ax.legend()
    suffix = '' if language == 'en' else '_ru'
    fig.savefig(FIGURES / f'bayesian_posterior_uncertainty{suffix}.png', dpi=160)
    plt.close(fig)


def save_virtual_fields_figure(bundle, language: str) -> None:
    structure = bundle['structure']
    weights = virtual_field_weights(structure)
    singular = bundle['identifiability']['singular_values']
    fig, axes = plt.subplots(2, 3, figsize=(13.2, 8.4), constrained_layout=True)
    for ax, (name, weight) in zip(axes.ravel()[:5], weights.items()):
        _imshow(ax, weight, name, 'weight' if language == 'en' else 'вес')
    ax = axes.ravel()[5]
    ax.semilogy(np.arange(1, len(singular) + 1), singular, marker='o')
    ax.set_xlabel('index' if language == 'en' else 'номер')
    ax.set_ylabel('singular value' if language == 'en' else 'сингулярное число')
    ax.set_title('Identifiability spectrum' if language == 'en' else 'Спектр идентифицируемости')
    fig.suptitle('Virtual fields and inverse-problem identifiability' if language == 'en' else 'Virtual fields и идентифицируемость обратной задачи', fontsize=15)
    suffix = '' if language == 'en' else '_ru'
    fig.savefig(FIGURES / f'virtual_fields_and_identifiability{suffix}.png', dpi=160)
    plt.close(fig)


def save_tables(bundle) -> None:
    structure = bundle['structure']
    load_cases = bundle['load_cases']
    truth = bundle['truth'].as_vector()
    np.savez_compressed(
        DATA / 'image_informed_calibration_dataset.npz',
        theta=structure.theta,
        kappa=structure.kappa,
        rho_f=structure.rho_f,
        connectivity=structure.connectivity,
        mask=structure.mask,
        x=structure.x,
        y=structure.y,
        exx=np.stack([case.exx for case in load_cases]),
        eyy=np.stack([case.eyy for case in load_cases]),
        gxy=np.stack([case.gxy for case in load_cases]),
        measured_force=np.stack([case.measured_force for case in load_cases]),
        true_force=np.stack([case.true_force for case in load_cases]),
        load_case_names=np.array([case.name for case in load_cases]),
        true_parameters=truth,
        parameter_names=np.array(PARAMETER_NAMES),
    )

    rows = []
    for result in bundle['results']:
        for name, true_value, estimate in zip(PARAMETER_NAMES, truth, result.parameters):
            rows.append({
                'method': result.method,
                'parameter': name,
                'true_value': true_value,
                'estimate': float(estimate),
                'relative_error_percent': float(100.0 * (estimate - true_value) / true_value),
                'residual_norm': result.residual_norm,
                'condition_number': result.condition_number,
            })
    write_rows(DATA / 'parameter_estimates.csv', rows)

    posterior = bundle['posterior']
    rows = []
    for name, true_value, mean, std in zip(PARAMETER_NAMES, truth, posterior['mean'], posterior['std']):
        rows.append({
            'parameter': name,
            'true_value': true_value,
            'posterior_mean': float(mean),
            'posterior_std': float(std),
            'lower_95': float(mean - 1.96 * std),
            'upper_95': float(mean + 1.96 * std),
        })
    write_rows(DATA / 'bayesian_posterior.csv', rows)

    singular = bundle['identifiability']['singular_values']
    rows = []
    for idx, value in enumerate(singular, start=1):
        rows.append({
            'index': idx,
            'singular_value': float(value),
            'condition_number': float(bundle['identifiability']['condition_number']),
        })
    write_rows(DATA / 'identifiability.csv', rows)

    summary_true = bundle['maps_true']
    summary_joint = bundle['maps_joint']
    from biomechanics_tutorials.image_informed_parameters import summarize_parameter_maps
    rows = []
    for label, maps in [('true', summary_true), ('joint_estimate', summary_joint)]:
        row = {'map_set': label}
        row.update(summarize_parameter_maps(structure, maps))
        rows.append(row)
    write_rows(DATA / 'spatial_parameter_summary.csv', rows)

    force_rows = []
    for case in load_cases:
        force_rows.append({
            'load_case': case.name,
            'true_Fx': float(case.true_force[0]),
            'true_Fy': float(case.true_force[1]),
            'true_Fxy': float(case.true_force[2]),
            'measured_Fx': float(case.measured_force[0]),
            'measured_Fy': float(case.measured_force[1]),
            'measured_Fxy': float(case.measured_force[2]),
        })
    write_rows(DATA / 'load_cases.csv', force_rows)


def main() -> None:
    bundle = benchmark_calibration(seed=19, force_noise=0.015)
    save_tables(bundle)
    for lang in ['en', 'ru']:
        save_pipeline_figure(bundle, lang)
        save_synthetic_experiment_figure(bundle, lang)
        save_identification_figure(bundle, lang)
        save_parameter_maps_figure(bundle, lang)
        save_bayesian_figure(bundle, lang)
        save_virtual_fields_figure(bundle, lang)
    print('Tutorial 19 calibration benchmark regenerated.')


if __name__ == '__main__':
    main()
