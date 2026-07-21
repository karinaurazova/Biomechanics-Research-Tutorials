# Active learning


Active learning asks which expensive simulation should be run next.  The tutorial uses a simple strategy: train an ensemble, evaluate uncertainty on a candidate pool, and add the points with largest predicted uncertainty.

This is not the only possible acquisition rule.  Other strategies may target expected error reduction, diversity, or constraint satisfaction.  The simple rule is enough to show the workflow: the surrogate is not only a predictor but also a guide for future data generation.

For RVE homogenization this can save substantial time.  Instead of computing thousands of microstructure solves, one can focus on cases where the current surrogate is least reliable.
