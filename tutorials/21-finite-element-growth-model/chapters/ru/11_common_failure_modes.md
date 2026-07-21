# Типичные ошибки и failure modes


FE growth models могут ломаться несколькими способами. Первая ошибка — boundary-condition failure. Если rigid modes не устранены, система сингулярна. Если закреплений слишком много, модель создаёт искусственные напряжения. Tutorial использует минимальную опору, но exercises предлагают сравнить её с clamped и более свободными вариантами.

Вторая ошибка — неправильный знак. Growth strain должен уменьшать elastic strain, когда displacement согласует рост. Если знак equivalent growth load поменять, solution может выглядеть правдоподобно, но stress field будет иметь противоположную интерпретацию. Поэтому tutorial объясняет weak form и проверяет residual.

Третья ошибка — переинтерпретация small-strain model. Linearized growth полезен для обучения, но большой биологический рост требует finite kinematics. Когда growth variables становятся большими, small-strain approximation перестаёт быть корректным. В коде growth variables ограничены, чтобы demonstration оставалась в безопасном диапазоне.

Четвёртая ошибка — принимать feedback за calibration. Stress-driven update law может давать интересную динамику без экспериментальной идентификации. Tutorial явно маркирует закон как synthetic и pedagogical. В реальном tissue modeling turnover rates, stress targets и constituent-specific responses требуют независимого обоснования.

Пятая ошибка — игнорировать mesh dependence. CST mesh подходит для первой демонстрации, но не для количественных прогнозов. Mesh refinement, element choice и quadrature имеют значение. Tutorial 21 готовит основу для RVE и surrogate-modeling modules, где эти решения станут ещё важнее.
