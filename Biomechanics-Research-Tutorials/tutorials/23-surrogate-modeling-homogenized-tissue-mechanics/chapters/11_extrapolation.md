# Extrapolation and trust regions


A surrogate can be accurate inside the training cloud and unreliable outside it.  This tutorial makes that visible by plotting errors over an extended grid.  The resulting map should be read as a trust-region diagnostic, not just a performance figure.

In practice, every surrogate should be accompanied by input bounds, sampling plots and warnings about unsupported regions.  This is particularly important when the surrogate is later embedded inside inverse identification or optimization, because optimizers often exploit extrapolation artifacts.

A safe workflow clips inputs, rejects unsupported predictions, or triggers a new expensive simulation when uncertainty is high.
