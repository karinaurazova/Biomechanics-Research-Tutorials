# The DIC measurement chain

The forward problem starts from a material point map $\boldsymbol{x}=\boldsymbol{X}+\boldsymbol{u}(\boldsymbol{X})$. A camera observes an intensity field rather than the displacement itself. The deformed image is therefore generated through inverse warping, interpolation, optical blur, intensity changes, sensor noise, and possible occlusion.

The inverse problem searches for parameters that make a deformed subset resemble its reference subset. Every stage introduces assumptions. A low residual does not by itself prove that the recovered displacement is physically correct, because model error, repetitive texture, out-of-plane motion, and discontinuities can produce misleading matches.
