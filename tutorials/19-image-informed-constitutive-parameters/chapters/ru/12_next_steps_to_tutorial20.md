# 12 — Переход к мультимодальному benchmark

Tutorial 19 идентифицирует image-informed constitutive parameters по синтетической структуре, DIC strain fields и force data. Tutorial 20 свяжет полную цепочку:

```text
ground-truth microstructure
-> SEM-like, polarization-like and fluorescence-like images
-> segmentation / SAM / μSAM
-> orientation and structure recovery
-> mechanical simulation
-> synthetic DIC images
-> recovered strain field
-> inverse parameter estimation
```

Такой финальный benchmark позволит проверить, как ошибка, появившаяся в начале imaging pipeline, распространяется до итоговой оценки механического параметра.

Главный методический вывод: verification требует известной истины на каждом этапе. Synthetic data позволяют это сделать до любых заявлений об experimental или clinical validity.
