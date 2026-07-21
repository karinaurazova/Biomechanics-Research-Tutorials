# Assembly и решение линейной системы


Global assembly идёт циклом по элементам. Для каждого треугольника вычисляются B matrix, area, element stiffness и equivalent growth load. Локальные степени свободы элемента отображаются в глобальную матрицу. Это стандартный паттерн finite-element assembly.

Так как модель линейна по displacement при фиксированном growth state, каждый шаг равновесия требует одного linear solve. В коде используются dense arrays ради читаемости. Для маленькой учебной сетки это нормально. Для больших сеток нужны sparse matrices и sparse solvers.

Displacement field хранится в узлах, а strain, growth strain и stress — по элементам. Это важно различать. Constant-strain triangles дают постоянные strain и stress внутри каждого элемента. При визуализации элементных полей код использует структурированное хранение двух треугольников на ячейку. При визуализации узловых полей используется nodal displacement или усреднение элементных величин.

Equilibrium residual вычисляется после восстановления полного вектора перемещений. Residual на free DOF должен быть близок к machine precision относительно правой части. Residual на fixed DOF интерпретируется как reaction force, необходимая для выполнения constraints.

Красивая картинка displacement field сама по себе недостаточна. Неверный знак growth load тоже может дать гладкую картину, но стресс будет интерпретироваться неправильно. Поэтому verification metrics являются частью результата, а не второстепенным debugging output.
