# Stress-driven обновление роста


После решения равновесия код вычисляет два stress stimuli. Первый — plane-stress mean stress proxy, равный половине sigma_xx plus sigma_yy. Второй — fiber stress sigma_ff, полученный проекцией тензора напряжений на локальное направление волокон. Это не единственные возможные биологические стимулы, но они понятны и легко вычисляются.

Update law явно меняет isotropic growth и fiber growth во времени. Напряжения сглаживаются по соседним элементам перед влиянием на рост. Это уменьшает нереалистичный checkerboard response и отражает идею, что biological remodeling не является бесконечно локальным.

В update law есть target values. Если текущий stress отличается от target, рост меняется. Поэтому модель является простой homeostatic feedback system. Feedback намеренно мягкий, ограниченный и explicit. Слишком большие gains могут вызвать oscillations или clipping. Это важный урок: growth laws — это динамические системы, а не простые алгебраические поправки.

Tutorial сравнивает frozen growth, full stress feedback и fiber-only feedback. Различия между сценариями показывают, какие части стрессового поля контролируются изотропным ростом, а какие — волоконным ростом. Они также показывают, что добавление feedback law не обязано улучшать каждую метрику.

В исследовательской модели update law должен быть связан с biological turnover, cell response, constituent deposition и degradation. Здесь он используется как controlled numerical mechanism для изучения FE pipeline.
