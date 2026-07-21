# Расширения и исследовательские задания

Естественные расширения: коррелированные priors, hierarchical Bayesian calibration, неопределённость геометрии, mesh-dependent numerical error, uncertainty surrogate-модели и specimen-specific inverse problems. Exercises ведут от простых изменений параметров к research-level redesigns.

## Примечания к реализации

Соответствующий код находится в `src/biomechanics_tutorials/sensitivity_uncertainty.py`. Запустите `reproduce.py`, чтобы пересоздать таблицы, figures и GIF-анимации для этой главы. Главу нужно читать вместе с CSV-файлами из `data/`, потому что цель не только увидеть график, но и понять, какие assumptions его породили.

## Что проверить

- Насколько физически правдоподобны диапазоны параметров для учебной задачи?
- Неопределённость выхода определяется одним главным параметром или взаимодействиями?
- Изменится ли вывод, если поменять prior range или mechanical limit?
