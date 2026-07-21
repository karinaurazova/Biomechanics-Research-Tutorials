# Упражнения — Tutorial 25

## Explore

1. Измените диапазон `fibre_fraction` и заново запустите Monte Carlo. Какой интервал отклика изменился сильнее всего?
2. Увеличьте `boundary_compliance` и изучите reliability curve.
3. Сравните ranking tornado plot с ranking по total Sobol index.

## Experiment

1. Замените uniform prior для одного параметра на triangular или normal prior.
2. Добавьте корреляцию между `fibre_fraction` и `connectivity`.
3. Повторите Sobol analysis для `anisotropy_ratio` и сравните с `peak_stress`.

## Research challenge

Спроектируйте pipeline-level error budget, где ошибка сегментации меняет долю волокон, ошибка ориентации меняет `orientation_deg`, а шум DIC меняет loading scale. Сравните полученную неопределённость с parameter-level benchmark из tutorial.
