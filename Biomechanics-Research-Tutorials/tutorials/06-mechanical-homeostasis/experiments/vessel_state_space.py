import matplotlib.pyplot as plt
import numpy as np

from biomechanics_tutorials.mechanical_homeostasis import VesselHomeostasisParameters, feedback_response, simulate_vessel_homeostasis, vessel_equilibrium, vessel_stimuli
from common import save_figure, title, tr

params = VesselHomeostasisParameters()
pressure = 1.30
flow = 1.55
r_values = np.linspace(0.75, 1.45, 20)
h_values = np.linspace(0.65, 1.75, 20)
R, H = np.meshgrid(r_values, h_values)
shear, wall = vessel_stimuli(pressure, flow, R, H, params)
U = params.radius_rate * R * feedback_response(shear - 1.0, response_limit=params.response_limit)
V = params.thickness_rate * H * feedback_response(wall - 1.0, response_limit=params.response_limit)
speed = np.sqrt(U**2 + V**2)
U_normalized = U / np.maximum(speed, 1.0e-12)
V_normalized = V / np.maximum(speed, 1.0e-12)
time = np.linspace(0.0, 60.0, 3001)
initial_states = [(0.82, 0.78), (1.35, 0.80), (0.90, 1.55), (1.38, 1.55)]
trajectories = [simulate_vessel_homeostasis(time, pressure, flow, r0, h0, params) for r0, h0 in initial_states]
equilibrium = vessel_equilibrium(pressure, flow, params)

for language in ("en", "ru"):
    fig, ax = plt.subplots(figsize=(7.2, 6.2))
    ax.quiver(R, H, U_normalized, V_normalized, speed, cmap="viridis", alpha=0.75)
    for trajectory in trajectories:
        ax.plot(trajectory["radius"], trajectory["thickness"], linewidth=2.2)
        ax.plot(trajectory["radius"][0], trajectory["thickness"][0], "o", markersize=5)
    ax.plot(*equilibrium, marker="*", markersize=16, label=tr("target", language))
    ax.set_xlabel(tr("radius", language))
    ax.set_ylabel(tr("thickness", language))
    ax.legend()
    ax.set_title(title("vessel_state_space", language))
    save_figure(fig, "vessel_state_space", language)
