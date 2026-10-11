# SCT con datos reales y el modelo de Bandura de 22 parámetros (pipeline z-score)

* θ₀ (DE, semilla 2026, reproduce la corrida 1 del CSV original): R² = 0.8806.
* 100 corridas de DE: R² 0.8781–0.8843; 100 con R² ≥ 0,87. Rango de parámetros en ellas: beta14 [-1.49, 1.47]; beta21 [-1.49, 1.43]; beta25 [-1.46, 1.47]; beta31 [-1.48, 1.29]; beta34 [-1.47, 1.27]; beta42 [-1.43, 1.49]; beta43 [-0.508, 0.543]; beta45 [0.809, 1.5]; beta46 [-1.49, 1.46]; beta54 [-1.5, -0.561]; gamma33 [0.00653, 2.91]; gamma35 [0.000933, 2.98]; gamma36 [0.0126, 2.97]; gamma57 [1.08, 2.84]; gamma64 [0.0832, 3]; gamma68 [0.00602, 2.89]; tau1 [0.36, 11.5]; tau2 [0.469, 11.1]; tau3 [0.606, 12]; tau4 [0.308, 1.05]; tau5 [0.327, 1.03]; tau6 [0.609, 12].
* Cambian de signo entre corridas igual de buenas: beta14, beta21, beta25, beta31, beta34, beta42, beta43, beta46.
* Parámetros sin efecto sobre x4 (sensibilidad nula): —.
* κ (activos) = inf; VIF máx = 4.51e+15; pares con cos ≥ 0,95: 9.
* Selección: Stage 2; S = gamma57, beta45; podados: —.
* ±5 %: cos Δ = 0.942, e_rel = 50.1 %, e_ajuste = 11.4 %; patrón A.
* e_ajuste por nivel: ±1 %: 10.6 %, ±5 %: 11.4 %, ±10 %: 12.4 %, ±20 %: 14.9 %, ±30 %: 15.1 %, ±40 %: 14.4 %, ±50 %: 14.5 %.
* Validación (entrenamiento días 1–24, prueba 25–31), χ²/n: reducido 1.63, completo 3.44, θ₀ 1.43; R² de prueba: reducido 0.842, completo 0.666; estables: reducido True, completo True. Completo reajustado con la DE del pipeline (días 1–24): χ²/n de prueba 2.13, R² 0.793.
