# Методические заметки — Tutorial 21

Этот tutorial лучше проходить медленно. Студенты часто понимают growth laws как обычные time updates, но недооценивают шаг finite-element equilibrium. Важно постоянно разделять локально предпочитаемый рост и совместимое поле перемещений.

## Рекомендуемая логика занятия

1. Нарисовать одномерный стержень с нагретой средней областью как аналог eigenstrain.
2. Ввести двумерный patch и необходимость displacement field.
3. Разобрать weak form до кода.
4. Объяснить constant-strain triangle и convention для engineering shear.
5. Сначала запустить frozen-growth scenario.
6. Добавить feedback только после понимания equilibrium residual.
7. Сравнивать trace stress и fiber stress, а не один scalar stress measure.

## Частые заблуждения

- Growth не равен displacement.
- Большой growth field не означает автоматически большой stress.
- Гладкая картинка displacement не является verification test.
- Reactions на constrained DOFs не являются численной ошибкой.
- Small-strain model не означает, что мягкие ткани линейны.

## Идеи для контроля

Попросите студентов объяснить одну строку assembly code и одну строку metrics table. Это проверяет связь между equations, implementation и interpretation.
