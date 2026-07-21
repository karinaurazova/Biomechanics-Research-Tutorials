# 09 — Spatial material maps

После калибровки глобальных параметров image-derived поля превращают их в spatial maps:

```text
matrix_modulus(x) = p0 + p1 rho_f(x)
```

```text
fiber_modulus(x) = p2 rho_f(x) order(x) + p3 connectivity(x) order(x)
```

Эти карты не являются прямыми экспериментальными измерениями свойств материала. Это model-dependent fields, полученные в рамках выбранной конститутивной гипотезы.

Различие принципиально. Изображение задаёт spatial distribution, но механический эксперимент калибрует scale. Без force или displacement data яркая волоконная область может указывать на более сильный отклик, но сама по себе не определяет величину жёсткости.
