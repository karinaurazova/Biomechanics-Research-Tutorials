# Noise and model error

Physics-informed learning does not remove measurement noise. It redistributes the effect of noise through the model assumptions. This can be beneficial when the physics is correct, but harmful when the physics is incomplete.

The tutorial distinguishes observation noise, image-prior error and model-form error. Observation noise affects measured displacement values. Image-prior error affects `E(x)`. Model-form error appears when the governing equation or material law is not the one that generated the data.

Reporting only final test error hides these mechanisms. The benchmark tables therefore include several diagnostics.
