# 03 — Кинематика конечных деформаций

Градиент деформации:

\[
\mathbf F=\frac{\partial \mathbf x}{\partial \mathbf X},
\qquad J=\det\mathbf F>0.
\]

Правый тензор Коши–Грина:

\[
\mathbf C=\mathbf F^T\mathbf F.
\]

Для разделения изменения формы и объёма используется

\[
\bar{\mathbf C}=J^{-2/3}\mathbf C,
\]

с инвариантами

\[
\bar I_1=\operatorname{tr}\bar{\mathbf C},
\qquad
\bar I_2=\frac12\left[(\operatorname{tr}\bar{\mathbf C})^2-
\operatorname{tr}(\bar{\mathbf C}^2)\right].
\]

Изохорные главные удлинения удовлетворяют

\[
\bar\lambda_i=J^{-1/3}\lambda_i,
\qquad
\bar\lambda_1\bar\lambda_2\bar\lambda_3=1.
\]

## Пути нагружения

Реализованы:

- несжимаемое одноосное растяжение;
- равноосное двухосное растяжение;
- плоская деформация;
- простой сдвиг в плоскостях \(xy\), \(xz\) и \(yz\);
- объёмная дилатация.

Это не полные краевые задачи, а контролируемые кинематические тесты, выявляющие различия функций энергии.
