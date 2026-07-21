# Связь с конечной кинематикой роста


Finite-strain growth framework использует F = Fe Fg. Growth tensor Fg переводит локальную reference neighborhood в grown natural configuration. Elastic tensor Fe переводит эту выросшую локальную конфигурацию в текущую совместимую конфигурацию. Stress выводится из elastic part, а не из total deformation.

Small-strain model в tutorial — линейный аналог этой идеи. Total strain epsilon(u) раскладывается на elastic strain и growth strain. Stress использует только elastic difference. Поэтому код полезен как bridge: он сохраняет conceptual separation, но не требует nonlinear solve machinery.

Переход к finite-strain implementation потребует нескольких изменений. Displacement gradient должен быть заменён deformation gradient. Constitutive law должен задаваться через strain-energy function. Residual станет нелинейным по displacement. Потребуются Newton iterations и consistent tangent matrices. Для incompressibility могут понадобиться mixed displacement-pressure elements или stabilization.

Boundary conditions и growth laws также станут тоньше. Порядок tensor multiplication имеет значение. Fiber growth, volume growth и remodeling of structural directions могут не коммутировать. Обновление Fg должно сохранять physical constraints, например positive determinant и meaningful fiber architecture.

Поэтому tutorial останавливается на linearized model, но точно показывает, где входит finite-strain generalization. После него должна быть понятна карта перехода: FE pipeline остаётся, а strain measure, constitutive law, residual и solver становятся nonlinear.
