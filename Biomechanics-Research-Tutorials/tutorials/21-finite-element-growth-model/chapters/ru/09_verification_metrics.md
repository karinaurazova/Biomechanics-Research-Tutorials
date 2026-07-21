# Метрики проверки


Tutorial сохраняет несколько scalar diagnostics для каждого шага. Residual norm проверяет корректность решения линейной системы равновесия. Reaction norm показывает силу, необходимую для поддержания boundary conditions. Mean energy density суммирует elastic accommodation. Mean growth magnitude и elastic mismatch показывают, сколько роста задано и какая часть не согласована без напряжений.

Stress statistics не являются validation metrics. Это internal consistency metrics. Они помогают сравнивать сценарии и находить ошибки. Например, если frozen growth и stress feedback дают одинаковые histories, update law фактически не применяется. Если residual norm велик, equilibrium solve нельзя считать надёжным. Если stress values взрываются, gains или boundary conditions выбраны неудачно.

Tutorial также вычисляет простую identifiability-style table. Она анализирует singular values элементной strain design matrix. Это ещё не полная inverse problem, а мост к будущим модулям: механические параметры нельзя идентифицировать из неинформативных strain states. Если поле деформаций бедное, разные комбинации параметров могут объяснять одни и те же данные.

Verification намеренно отделена от interpretation. Simulation может быть численно корректной и биологически грубой. И наоборот, биологически красивая идея может быть реализована неправильно. Workflow tutorial требует сначала доказать численную корректность, а уже потом делать mechanobiological conclusions.

CSV-файлы делают проверки воспроизводимыми. Их можно читать без notebook, сравнивать между запусками и использовать в continuous integration.
