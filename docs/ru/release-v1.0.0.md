# Заметки к релизу — v1.0.0

**Biomechanics Research Tutorials v1.0.0** — первый полный релиз репозитория из 25 учебно-исследовательских модулей.

## Что входит

- **25 воспроизводимых туториалов** по вычислительной биомеханике.
- Двуязычные материалы на английском и русском.
- Только синтетические датасеты и benchmarks для verification-ready сценариев, обучения и сравнения методов.
- Исходные модули в `src/biomechanics_tutorials/`.
- `reproduce.py` в каждом tutorial.
- Рисунки, GIF-анимации, notebooks, exercises, instructor notes и references.
- Публичная документация: индекс tutorials, визуальная галерея, языковая политика, методические рекомендации и материалы мастер-классов.

## Блоки релиза

| Диапазон | Блок | Описание |
|---|---|---|
| 01–05 | Основы | fiber mechanics, structure tensors, active/passive stress |
| 06–12 | Рост и ремоделирование | homeostasis, growth tensors, ECM turnover, residual stress |
| 13–20 | Image-informed и экспериментальная механика | synthetic microscopy, DIC, segmentation, multimodal benchmarks |
| 21–25 | Продвинутые вычислительные методы | FE growth, RVE, surrogates, physics-informed learning, UQ |


## Статистика релиза

- Туториалов: **25**
- PNG-рисунков: **674**
- GIF-анимаций: **72**
- Глав на английском: **359**
- Глав на русском: **359**

## Позиция по данным

Этот релиз **не заявляет экспериментальную валидацию**. Все данные синтетические, воспроизводимые и предназначены для verification-ready workflow, сравнения методов и обучения.

## Первые команды

```bash
python scripts/diagnose_environment.py
python scripts/verify_repository.py
python tutorials/25-sensitivity-analysis-uncertainty-quantification/reproduce.py
```

## Ограничения

- Полный `pytest` может идти долго, потому что многие tutorials пересоздают рисунки и синтетические данные.
- SAM и μSAM представлены через benchmark-логику, prompts и абстракции failure cases; репозиторий не требует больших внешних весов моделей.
- FE, RVE, PINN-like и UQ модули являются учебными реализациями, а не production-солверами.
