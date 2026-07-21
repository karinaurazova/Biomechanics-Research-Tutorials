from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

from common import DATA, FIGURES, write_rows
from biomechanics_tutorials.image_informed_parameters import (
    PARAMETER_NAMES,
    build_synthetic_load_cases,
    build_synthetic_structural_fields,
    global_force_system,
    solve_nonnegative_least_squares,
    true_parameter_set,
)


def run_sensitivity() -> list[dict[str, float | int | str]]:
    rows = []
    structure = build_synthetic_structural_fields(seed=31)
    truth = true_parameter_set().as_vector()
    for noise in [0.0, 0.01, 0.02, 0.04, 0.08]:
        all_cases = build_synthetic_load_cases(structure, true_parameter_set(), noise_level=noise, seed=100 + int(noise * 1000))
        for n_cases in [2, 3, 4, 6]:
            cases = all_cases[:n_cases]
            A, y, _ = global_force_system(structure, cases)
            result = solve_nonnegative_least_squares(A, y, method='load_curve_only')
            rel_errors = 100.0 * (result.parameters - truth) / truth
            rows.append({
                'force_noise': noise,
                'n_load_cases': n_cases,
                'mean_abs_relative_error_percent': float(np.mean(np.abs(rel_errors))),
                'max_abs_relative_error_percent': float(np.max(np.abs(rel_errors))),
                'condition_number': result.condition_number,
                'residual_norm': result.residual_norm,
            })
            for name, err in zip(PARAMETER_NAMES, rel_errors):
                rows.append({
                    'force_noise': noise,
                    'n_load_cases': n_cases,
                    'parameter': name,
                    'relative_error_percent': float(err),
                    'condition_number': result.condition_number,
                    'residual_norm': result.residual_norm,
                })
    return rows


def save_sensitivity_figure(rows, language: str) -> None:
    summary = [row for row in rows if 'mean_abs_relative_error_percent' in row]
    fig, ax = plt.subplots(figsize=(11.5, 7.2), constrained_layout=True)
    for n_cases in sorted({int(row['n_load_cases']) for row in summary}):
        subset = [row for row in summary if int(row['n_load_cases']) == n_cases]
        x = [float(row['force_noise']) for row in subset]
        y = [float(row['mean_abs_relative_error_percent']) for row in subset]
        ax.plot(x, y, marker='o', label=f'{n_cases} load cases' if language == 'en' else f'{n_cases} режимов')
    ax.set_xlabel('force noise level' if language == 'en' else 'уровень шума силы')
    ax.set_ylabel('mean absolute parameter error, %' if language == 'en' else 'средняя абсолютная ошибка параметров, %')
    ax.set_title('Sensitivity of load-only identification' if language == 'en' else 'Чувствительность идентификации только по силе')
    ax.legend()
    suffix = '' if language == 'en' else '_ru'
    fig.savefig(FIGURES / f'sensitivity_sweep{suffix}.png', dpi=160)
    plt.close(fig)


def main() -> None:
    rows = run_sensitivity()
    normalized = []
    for row in rows:
        if 'parameter' not in row:
            normalized.append({
                'row_type': 'summary',
                'force_noise': row['force_noise'],
                'n_load_cases': row['n_load_cases'],
                'parameter': '',
                'relative_error_percent': '',
                'mean_abs_relative_error_percent': row['mean_abs_relative_error_percent'],
                'max_abs_relative_error_percent': row['max_abs_relative_error_percent'],
                'condition_number': row['condition_number'],
                'residual_norm': row['residual_norm'],
            })
        else:
            normalized.append({
                'row_type': 'parameter',
                'force_noise': row['force_noise'],
                'n_load_cases': row['n_load_cases'],
                'parameter': row['parameter'],
                'relative_error_percent': row['relative_error_percent'],
                'mean_abs_relative_error_percent': '',
                'max_abs_relative_error_percent': '',
                'condition_number': row['condition_number'],
                'residual_norm': row['residual_norm'],
            })
    write_rows(DATA / 'sensitivity_sweep.csv', normalized)
    for lang in ['en', 'ru']:
        save_sensitivity_figure(rows, lang)
    print('Tutorial 19 sensitivity sweep regenerated.')


if __name__ == '__main__':
    main()
