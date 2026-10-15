# Preliminary analysis (kept for provenance)

`certify_systems.py` belongs to an earlier version of the analysis, on the state trajectories of the
models (60 time points) and with the subsets of that version. It evaluated the explicit
finite-perturbation certificates of cos(Delta) proved in Lean (`CertifiedFiniteODE.certified_cos_ode`,
`ExactLinearCertificate`), with lower bounds of the constants M1, M2 estimated from the vector fields.
Its output is `results/preliminary/finite_certificates.md` (and `.csv`), quoted in the Supplementary
Note "Logical sequence of the formal proofs": the resulting constants L_c range from about 1e2 to
1e24 and no scenario at +-5 % can be certified, which is why the method relies on the local results
and on the numerical admissibility test instead.

It is not used by any other result of the paper, is not maintained, and its comments are in Spanish.
The row of the SCT model in that table was computed by a companion script for an earlier version of
the SCT model, which is not included. `certify_systems.py` reads the benchmark from `bench/problems` next to it (create a link to
`data/Benchmark-Models-PEtab/problems`) and writes to `resultados/`.
