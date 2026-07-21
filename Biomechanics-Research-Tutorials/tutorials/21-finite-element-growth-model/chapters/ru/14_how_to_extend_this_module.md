# Как развивать этот модуль


Первое расширение — mesh refinement. Увеличьте nx и ny, перезапустите benchmark и сравните stress statistics, energy density и residuals. Если выводы сильно меняются, coarse baseline нельзя использовать для количественной интерпретации.

Второе расширение — nonlinear material response. Можно заменить plane-stress matrix на hyperelastic law и решать nonlinear residual методом Newton. Это большой шаг, но текущий код уже даёт skeleton для assembly и boundary-condition logic.

Третье расширение — coupling to image-informed structure. Tutorial 18 оценивает orientation и concentration fields. Tutorial 19 связывает image-derived descriptors с constitutive parameters. Tutorial 21 может принимать такие поля как spatial inputs, заменяя синтетические orientation и growth patterns.

Четвёртое расширение — inverse growth identification. Вместо prescribing growth and computing stress можно искать growth field, которое объясняет observed residual stress, opening angle, DIC strain или shape change. Такая задача обычно ill-posed и требует regularization.

Пятое расширение — uncertainty analysis. Growth parameters, material constants, boundary conditions и fiber orientations неопределённы. Один deterministic simulation должен стать ансамблем. Это напрямую связано с Tutorial 25, где sensitivity and uncertainty станут главным предметом.
