# Интерпретация сценариев


Frozen-growth scenario — baseline. Он отвечает на вопрос: какое stress field создаёт исходное несовместимое поле роста при выбранных boundary conditions? Поскольку рост не обновляется, time history должен оставаться практически постоянным. Это проверяет детерминированность solver.

Stress-feedback scenario разрешает эволюцию isotropic и fiber growth. При умеренных gains response меняется плавно. Некоторые stress measures могут приближаться к targets, а другие — нет. Это ожидаемо: один feedback law не может независимо контролировать каждую локальную компоненту stress.

Fiber-only scenario изолирует эффект anisotropic growth. Он меняет growth strain главным образом вдоль локального направления волокон. Это может снижать или перераспределять fiber stress, но оставлять mean stress или boundary reactions высокими. Сравнение показывает, почему isotropic и anisotropic remodeling нельзя сводить к одной scalar variable.

Интерпретировать figures нужно через сравнение полей. Growth magnitude, displacement magnitude, trace stress, fiber stress и energy density отвечают на разные вопросы. Область большого displacement может иметь низкий stress, если она свободно перемещается. Область с малым displacement около support может хранить большую elastic energy.

Главный концептуальный вывод: growth не равен deformation. Deformation — compatible displacement solution. Growth — локально предпочитаемое изменение. Stress измеряет mismatch между ними после выполнения equilibrium.
