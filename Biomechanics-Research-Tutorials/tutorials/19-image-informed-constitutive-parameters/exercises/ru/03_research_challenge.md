# Упражнение 03 — Исследовательское расширение

Расширьте модель в одном направлении:

1. Замените small-strain law на finite-strain hyperelastic fibre model.
2. Оценивайте spatially varying `fiber_scale(x)`, а не один глобальный параметр.
3. Добавьте segmentation-bias experiment, где маска завышает fibre fraction.
4. Свяжите модель с простым RVE solver.
5. Реализуйте простой Metropolis sampler и сравните его с Gaussian posterior.

Результат: мини-отчёт с предположениями, уравнениями, изменениями кода и ограничениями.
