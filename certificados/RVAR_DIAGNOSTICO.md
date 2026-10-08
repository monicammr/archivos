# Diagnóstico de R_var (columna Var.% de la Tabla 1)

## Definición
`R_var(S) = Σ_{j∈S} ‖J_j‖² / Σ_j ‖J_j‖²`, con `J` la matriz de sensibilidad (ecuación 2 del paper).
El valor depende de si `J` es **absoluta** (∂x/∂θ, ecuación 1 del paper) o **relativa**
(θ·∂x/∂θ, sensibilidad logarítmica).

## Origen de los valores del paper
Los valores de Var.% no los genera ningún script del paquete de reproducción: están escritos a
mano en `05_figuras_paper/bc_energia_tabla.py`, y esa lista **no coincide** con la Tabla 1 del
PDF en varios sistemas (p. ej. Armistead 93,0 vs 99,9; Borghans 94,7 vs 91,4;
Giordano 43,1 vs 83,7; Lang 59,3 vs 89,1; Rahman 98,0 vs 44,5).

## Reproducción con el código del pipeline (`rvar_check.py`)
Usa las funciones de `01_pipeline_principal/petab_V9_todos35.py` (`load_parameters`,
`sensitivity_jacobian`, `variance_retention`) con cuatro variantes
(salida completa en `resultados/rvar_variantes_sneyd_elowitz_crauste.txt`):

| Sistema (subconjunto) | Tabla 1 | A: pipeline tal cual (abs, T=50, 200 pts, ε=1e-5) | B: pipeline, J relativa | C: ajustes del paper (abs, 60 pts, δ=0,01) | D: paper + J relativa |
|---|---|---|---|---|---|
| Sneyd {k1, k2} | 99,5 | 0,000 | 61,7 | 0,000 | 38,7 |
| Elowitz {tps_active, tau_prot} | 99,4 | 0,033 | 31,6 | 1,1 | 76,3 |
| Crauste {mu_N, rho_E} | 96,6 | 1,9 | 99,5 | 23,8 | 99,9 |

Con J absoluta (la que describe la ecuación 1 y usa el código: `USE_RELATIVE_SENSITIVITY =
False`), los subconjuntos de Sneyd y Elowitz **ni siquiera son los de mayor energía** (los
dominantes son `k_2`, `l_4` en Sneyd y `tps_repr`, `eff` en Elowitz), así que la regla de la
Etapa 1 (orden descendente de E_j) no los habría elegido. Crauste sí cuadra con J relativa.

## Comparación para todos los sistemas (`resultados/*.json`, 60 puntos, diferencias centradas)

| Sistema | Var.% (bc_energia_tabla.py) | R_var abs | R_var rel |
|---|---|---|---|
| Bachmann | 99,7 | 99,68 | 19,36 |
| Blasi | 100,0 | 99,95 | 94,35 |
| Boehm | 97,9 | 94,14 | 96,18 |
| Brannmark | 100,0 | 98,21 | 23,39 |
| Chen | 100,0 | 100,00 | 48,92 |
| Crauste | 96,6 | 6,27 | 99,91 |
| Elowitz | 99,4 | 1,02 | 76,24 |
| Fiedler | 100,0 | 100,00 | 26,20 |
| Raimundez | 99,9 | 0,00 | 0,08 |
| SalazarCavazos | 95,0 | 100,00 | 100,00 |
| Sneyd | 99,5 | 0,00 | 34,41 |
| Weber | 99,9 | 12,20 | 41,89 |
| Zheng | 96,3 | 25,76 | 81,55 |

Conclusión: la columna mezcla convenciones (algunos valores cuadran con J absoluta —Bachmann,
Blasi, Chen, Fiedler—, otros con J relativa —Crauste—) y otros no cuadran con ninguna
(Sneyd, Elowitz, Raimundez, Weber, Zheng). Recomendación: fijar una única convención,
documentarla en la ecuación (1) y recalcular la columna completa con un único script.
