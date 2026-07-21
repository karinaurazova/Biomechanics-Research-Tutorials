# Происхождение рисунков — Tutorial 03

Каждый сохранённый рисунок строится по синтетическим параметрам отдельным сценарием.

| Файл | Генерирующий сценарий |
|---|---|
| `model_catalog.png`, `model_catalog_ru.png` | `experiments/model_catalog.py` |
| `isotropic_uniaxial.png`, `isotropic_uniaxial_ru.png` | `experiments/isotropic_uniaxial.py` |
| `deformation_modes.png`, `deformation_modes_ru.png` | `experiments/deformation_modes.py` |
| `limiting_chain.png`, `limiting_chain_ru.png` | `experiments/limiting_chain.py` |
| `ogden_exponents.png`, `ogden_exponents_ru.png` | `experiments/ogden_exponents.py` |
| `calibration_nonuniqueness.png`, `calibration_nonuniqueness_ru.png` | `experiments/calibration_nonuniqueness.py` |
| `volumetric_penalties.png`, `volumetric_penalties_ru.png` | `experiments/volumetric_penalties.py` |
| `fiber_angle.png`, `fiber_angle_ru.png` | `experiments/fiber_angle.py` |
| `fiber_angle_map.png`, `fiber_angle_map_ru.png` | `experiments/fiber_angle_map.py` |
| `hgo_goh_dispersion.png`, `hgo_goh_dispersion_ru.png` | `experiments/hgo_goh_dispersion.py` |
| `myocardium_shear_modes.png`, `myocardium_shear_modes_ru.png` | `experiments/myocardium_shear_modes.py` |
| `derivative_verification.png`, `derivative_verification_ru.png` | `experiments/derivative_verification.py` |
| `objectivity_check.png`, `objectivity_check_ru.png` | `experiments/objectivity_check.py` |

Полное воспроизведение:

```bash
python tutorials/03-hyperelastic-constitutive-models/reproduce.py
```
