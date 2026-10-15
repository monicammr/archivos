# Error relativo e_rel junto a cos Δ (perturbación ±5 %)

Script: `erel_systems.py` (mismos escenarios que la validación de cos Δ: semilla 42, 15
escenarios, 60 puntos, θ = θ₀(1 + 0,05·d)). Datos por escenario y por nivel (±1, 5, 10, 20,
50 %) en `resultados/erel/`.

* cos Δ = ⟨Δx_full, Δx_sel⟩ / (‖Δx_full‖ ‖Δx_sel‖): mide sólo la **dirección**.
* e_rel = ‖Δx_full − Δx_sel‖ / ‖Δx_full‖: mide dirección **y tamaño**.
* Lean (`CosineCertificate.cos_lower_of_rel_error`): e_rel ≤ ε ⇒ cos Δ ≥ √(1 − ε²); con
  ε = 0,436 se garantiza cos Δ ≥ 0,90. Lo contrario **no** vale.

Grupos: **A** e_rel ≤ 0,10; **B** 0,10 < e_rel ≤ 0,436; **C** cos Δ ≥ 0,90 pero e_rel > 0,436;
**D** cos Δ < 0,90.

| Sistema | Etapa | \|S\| | cos Δ (mediana) | e_rel (mediana) | e_rel (p90) | ‖Δx_sel‖/‖Δx_full‖ | e_rel ≤ 0,10 | e_rel ≤ 0,436 | grupo |
|---|---|---|---|---|---|---|---|---|---|
| Crauste | FIM | 2 | 1.000 | 0.031 | 0.081 | 1.001 | 14/15 | 15/15 | A |
| Armistead | FIM | 2 | 1.000 | 0.065 | 0.143 | 1.059 | 11/15 | 15/15 | A |
| Boehm | SCAN | 3 | 0.991 | 0.165 | 0.522 | 1.009 | 5/15 | 12/15 | B |
| Borghans | FIM | 7 | 0.975 | 0.237 | 0.686 | 1.021 | 1/15 | 13/15 | B |
| Lang | SCAN | 6 | 0.982 | 0.243 | 0.246 | 0.832 | 0/15 | 15/15 | B |
| Giordano | SCAN | 6 | 0.993 | 0.253 | 1.414 | 1.001 | 0/15 | 12/15 | B |
| Blasi | FIM | 2 | 0.973 | 0.256 | 0.706 | 0.998 | 2/15 | 11/15 | B |
| Okuonghae | FIM | 6 | 0.994 | 0.257 | 0.588 | 0.954 | 2/15 | 10/15 | B |
| Froehlich | FIM | 22 | 0.942 | 0.336 | 0.446 | 0.933 | 0/15 | 13/15 | B |
| Rahman | SCAN | 3 | 0.990 | 0.445 | 7.529 | 0.871 | 1/15 | 7/15 | C |
| Chen | FIM | 2 | 0.998 | 0.526 | 1.665 | 0.583 | 0/15 | 5/15 | C |
| Zhao | SCAN | 1 | 0.994 | 0.574 | 2.614 | 0.777 | 0/15 | 6/15 | C |
| Smith | SCAN | 2 | 0.997 | 0.606 | 1.838 | 0.501 | 1/15 | 3/15 | C |
| Raia | SCAN | 1 | 1.000 | 0.676 | 2.670 | 0.829 | 1/15 | 5/15 | C |
| Sneyd | FIM | 2 | 0.998 | 0.678 | 2.166 | 0.585 | 0/13 | 4/13 | C |
| Raimundez | FIM | 1 | 1.000 | 0.996 | 0.996 | 0.004 | 0/15 | 0/15 | C |
| Elowitz | FIM | 2 | 0.784 | 0.620 | 0.925 | 0.784 | 0/15 | 3/15 | D |
| Bachmann | FIM | 2 | 0.822 | 0.692 | 1.517 | 0.668 | 0/15 | 5/15 | D |
| Zheng | FIM | 4 | 0.831 | 0.703 | 1.041 | 0.951 | 0/15 | 4/15 | D |
| Weber | SCAN | 4 | 0.809 | 0.724 | 1.783 | 0.709 | 1/15 | 4/15 | D |
| Brannmark | SCAN | 6 | 0.688 | 0.868 | 1.335 | 0.552 | 0/15 | 0/15 | D |
| Fiedler | FIM | 2 | 0.794 | 0.885 | 1.220 | 0.574 | 0/15 | 0/15 | D |

SalazarCavazos no aparece: con T = 0,01 la respuesta a la perturbación es menor que el umbral
numérico (‖Δx_full‖ < 10⁻⁶) en todos los escenarios, igual que en la validación de cos Δ.

## Lectura

* **A** (Crauste, Armistead): el modelo reducido reproduce la respuesta con error ≤ 10 %.
* **B**: error moderado (16–34 %), pero suficiente para garantizar cos Δ ≥ 0,90.
* **C**: el ejemplo de ChatGPT ocurre de verdad. Raimundez tiene cos Δ = 1,000 pero la
  respuesta reducida es el **0,4 %** de la completa (e_rel = 0,996): la dirección es la misma
  pero el tamaño no. Chen, Sneyd, Smith, Raia y Zhao: cos Δ ≥ 0,99 con la respuesta reducida
  a 50–83 % del tamaño de la completa.
* **D**: cos Δ ya es < 0,90 al ±5 % (patrones B–D del artículo).

Recomendación para el artículo: informar e_rel junto a cos Δ y no presentar cos Δ ≥ 0,90 como
"fidelidad de trayectoria"; cos Δ certifica la dirección de la respuesta, e_rel su tamaño.
