# Шум и ошибка модели

Physics-informed обучение не удаляет шум. Оно перераспределяет влияние шума через предположения модели. Это полезно, когда физика корректна, и опасно, когда физика неполна.

Разделяются observation noise, image-prior error и model-form error. Observation noise влияет на измеренные перемещения. Image-prior error влияет на `E(x)`. Model-form error возникает, когда уравнение или material law не соответствуют данным.

Поэтому benchmark выводит несколько diagnostics, а не только итоговую ошибку.
