# Заметки для преподавателя

Этот tutorial связывает inverse mechanics и PINNs. Начинайте с data-only case и спросите студентов, почему кривая перемещений может выглядеть хорошо, а поле деформаций быть ненадёжным. Затем введите PDE residual как механический регуляризатор. Random-feature реализация менее модная, чем deep-learning framework, но гораздо прозрачнее для проверки.

План занятия на 90 минут:

1. 15 мин: равновесие 1D стержня и boundary conditions.
2. 20 мин: dataset и stiffness prior.
3. 20 мин: вывод block least-squares системы.
4. 20 мин: запуск case suite и интерпретация residual fields.
5. 15 мин: inverse calibration и identifiability.

Важно подчеркнуть: малая physics residual не является experimental validation. Она означает только согласованность с выбранной физической моделью.
