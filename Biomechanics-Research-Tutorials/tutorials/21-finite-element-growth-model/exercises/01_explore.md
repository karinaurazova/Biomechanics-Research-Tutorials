# Exercise 1 — Explore the baseline finite-element solution

1. Run `reproduce.py` and open the saved figures.
2. Identify where growth magnitude is largest.
3. Identify where trace stress and fiber stress are largest.
4. Explain why these regions do not have to coincide.
5. Inspect `time_history_stress_feedback.csv` and report the final residual norm.

Expected discussion: growth is a local preferred change, while stress is the elastic mismatch left after compatibility, equilibrium and boundary conditions are enforced.
