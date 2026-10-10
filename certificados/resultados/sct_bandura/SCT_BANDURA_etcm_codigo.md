# SCT Bandura con el método final (valores: etcm; entradas: codigo)

Modelo lineal de 6 estados, 22 parámetros, 3 condiciones de entrada; salida medida y = x₄. Sin datos experimentales ni parámetros de calibración.

| Variante | Salidas | Sin efecto | κ (con efecto) | VIF máx (con efecto) | Pares con cos ≥ 0,95 | Etapa | S | e_rel ±5 % | e_ajuste ±5 % | Patrón |
|---|---|---|---|---|---|---|---|---|---|
| salida | 240 | gamma35, gamma36, gamma57, gamma68 | inf | 1.97e+15 | 48 | Stage 2 | beta54, beta46 | 76.7 % | 9.9 % | A |
| estados | 1440 | gamma35, gamma36, gamma57, gamma68 | 2.32e+03 | 2.4e+05 | 8 | Stage 2 | beta54, gamma64 | 71.9 % | 30.3 % | A |

## salida

* Etapa 1: beta54, gamma64, tau4 (R_var = 46.8 %).
* Antes de la poda: beta54, beta46; podados: —.
* Pares casi colineales (cos ≥ 0,95): beta46–gamma64 (1.000), beta14–beta31 (1.000), beta31–beta42 (1.000), beta25–beta42 (1.000), beta45–beta54 (1.000), beta14–beta42 (1.000), beta14–beta21 (1.000), beta25–beta31 (1.000), beta21–beta31 (1.000), beta14–beta25 (1.000), beta21–beta42 (1.000), beta25–beta34 (0.999).
* Candidatos descartados por κ/VIF: beta45 (con beta54, cos = 1.000), beta46 (con gamma64, cos = 1.000), beta43 (con beta54, cos = 0.887), gamma33 (con beta54, cos = 0.517), tau3 (con beta54, cos = 0.901), beta14 (con beta54, cos = 0.985), beta31 (con beta54, cos = 0.986), beta42 (con beta54, cos = 0.987), beta34 (con beta54, cos = 0.993), beta25 (con beta54, cos = 0.989), tau2 (con beta54, cos = 0.996), tau1 (con beta54, cos = 0.997), tau5 (con tau4, cos = 0.996), beta21 (con beta54, cos = 0.982), tau6 (con tau4, cos = 0.719).
* e_ajuste por nivel: ±1 %: 10.4 %, ±5 %: 9.9 %, ±10 %: 9.3 %, ±20 %: 8.8 %, ±30 %: 8.4 %, ±40 %: 7.9 %, ±50 %: 7.5 %.

## estados

* Etapa 1: beta54, gamma64, beta46, beta14, gamma33, tau6 (R_var = 70.7 %).
* Antes de la poda: beta54, gamma64; podados: —.
* Pares casi colineales (cos ≥ 0,95): beta21–beta25 (0.999), beta31–beta34 (0.999), beta25–tau2 (0.995), beta21–tau2 (0.990), tau4–tau5 (0.986), beta42–beta45 (0.984), beta45–beta54 (0.980), beta42–beta54 (0.964).
* Candidatos descartados por κ/VIF: beta45 (con beta54, cos = 0.980), beta43 (con beta54, cos = 0.864), tau3 (con gamma33, cos = 0.824), beta31 (con beta54, cos = 0.825), tau4 (con beta54, cos = 0.910), beta34 (con beta54, cos = 0.837), beta25 (con beta54, cos = 0.757), beta42 (con beta54, cos = 0.964), tau2 (con beta54, cos = 0.779), tau1 (con beta14, cos = 0.933), beta21 (con beta54, cos = 0.743), tau5 (con beta54, cos = 0.928), beta45 (con beta54, cos = 0.980).
* e_ajuste por nivel: ±1 %: 29.8 %, ±5 %: 30.3 %, ±10 %: 30.3 %, ±20 %: 28.7 %, ±30 %: 27.2 %, ±40 %: 25.8 %, ±50 %: 24.5 %.
