# Методические заметки — Tutorial 19

Рекомендуемый ход занятия:

1. Начать с вопроса, почему точная сегментация всё равно может быть механически недостаточной.
2. Разобрать различие между structural, mechanical и joint identification.
3. Вывести на доске linear-in-parameters stress basis.
4. Запустить baseline script и посмотреть `parameter_estimates.csv`.
5. Сравнить load-only и virtual-field-style systems через singular values.
6. Обсудить, почему Bayesian posterior не является украшением: он показывает, что данные не смогли идентифицировать.
7. Завершить связью с Tutorial 20 и идеей propagation of errors through the full pipeline.

Типичное заблуждение: студенты могут воспринимать image-derived stiffness maps как напрямую измеренные свойства материала. Важно подчеркнуть, что это model-dependent maps, калиброванные механическими данными.
