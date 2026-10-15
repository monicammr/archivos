# SCT con datos reales y el modelo de 18 parámetros (evolución diferencial, ETCM 2025)

* θ₀ (semilla 1, reproduce la corrida original): R² = 0.8505. Otras semillas: R² = 0.8721, R² = 0.8722 con parámetros muy distintos (no identificabilidad).
* Parámetros sin efecto sobre x4 (sensibilidad nula): beta21, gamma64, tau1.
* κ (activos) = inf; VIF máx = inf; pares con cos ≥ 0,95: 23.
* Selección: Stage 2; S = gamma57, tau5; podados: —.
* ±5 %: cos Δ = 0.988, e_rel = 96.9 %, e_ajuste = 0.0 %; patrón A.
* e_ajuste por nivel: ±1 %: 0.0 %, ±5 %: 0.0 %, ±10 %: 0.0 %, ±20 %: 0.0 %, ±30 %: 0.0 %, ±40 %: 0.0 %, ±50 %: 0.1 %.
* Validación (entrenamiento días 1–24, prueba 25–31), χ²/n: reducido 1.87, completo 1.49, θ₀ 1.46; R² de prueba: reducido 0.771, completo 0.817.
