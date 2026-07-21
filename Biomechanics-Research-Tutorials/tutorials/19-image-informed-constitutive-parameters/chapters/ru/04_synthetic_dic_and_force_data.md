# 04 — Синтетические DIC и силовые данные

Синтетический эксперимент содержит несколько load cases:

- малое и большое одноосное растяжение по `x`;
- одноосное растяжение по `y`;
- biaxial loading;
- shear;
- spatially graded strain field.

Для каждого случая заданы full-field strain components:

```text
epsilon_xx(x), epsilon_yy(x), gamma_xy(x)
```

и глобальный reaction-like force vector, полученный усреднением напряжений по области ткани. К данным добавляется небольшой шум, имитирующий измерительную неопределённость.

Такая постановка отражает логику DIC-based mechanics: изображения дают displacement/strain field, а load cell даёт boundary force information. Обратная задача ищет параметры материала, которые согласуют оба источника данных.
