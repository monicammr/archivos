# SCT Bandura con el método final (valores: etcm; entradas: seis)

Modelo lineal de 6 estados, 22 parámetros, 6 condiciones de entrada; salida medida y = x₄. Sin datos experimentales ni parámetros de calibración.

| Variante | Salidas | Sin efecto | κ (con efecto) | VIF máx (con efecto) | Pares con cos ≥ 0,95 | Etapa | S | e_rel ±5 % | e_ajuste ±5 % | Patrón |
|---|---|---|---|---|---|---|---|---|---|
| salida | 480 | — | inf | 1.54e+17 | 51 | Stage 2 | beta45, beta43 | 66.1 % | 10.8 % | A |
| estados | 2880 | — | 202 | 1.84e+03 | 9 | Stage 2 | beta45, beta14 | 53.0 % | 27.2 % | A |

## salida

* Etapa 1: beta45, beta43, tau5, beta46, gamma33, gamma36, gamma68, tau6 (R_var = 58.8 %).
* Antes de la poda: beta45, beta43; podados: —.
* Pares casi colineales (cos ≥ 0,95): beta14–beta31 (1.000), beta14–beta21 (1.000), beta21–beta31 (1.000), beta25–beta42 (1.000), beta31–beta34 (0.999), beta14–beta34 (0.999), beta21–beta34 (0.998), beta34–beta42 (0.997), beta25–tau2 (0.997), beta54–tau1 (0.997), beta54–tau2 (0.997), beta31–beta42 (0.996).
* Candidatos descartados por κ/VIF: beta54 (con beta45, cos = 0.993), gamma57 (con beta45, cos = 0.980), beta14 (con beta45, cos = 0.966), beta31 (con beta45, cos = 0.967), tau3 (con beta43, cos = 0.990), beta42 (con beta45, cos = 0.982), gamma35 (con beta43, cos = 0.616), tau4 (con beta45, cos = 0.941), beta25 (con beta45, cos = 0.985), tau2 (con beta45, cos = 0.994), beta34 (con beta45, cos = 0.977), tau1 (con beta45, cos = 0.992), gamma64 (con beta46, cos = 0.982), beta21 (con beta45, cos = 0.962), beta54 (con beta45, cos = 0.993).
* e_ajuste por nivel: ±1 %: 11.0 %, ±5 %: 10.8 %, ±10 %: 10.5 %, ±20 %: 10.1 %, ±30 %: 10.4 %, ±40 %: 10.7 %, ±50 %: 9.4 %.

## estados

* Etapa 1: beta45, beta14, beta43, beta31, beta25, tau1, gamma64, beta46, gamma33, gamma36, gamma68, tau6 (R_var = 57.4 %).
* Antes de la poda: beta45, beta14; podados: —.
* Pares casi colineales (cos ≥ 0,95): beta31–beta34 (0.999), beta25–tau2 (0.995), beta21–beta25 (0.989), beta42–beta45 (0.981), beta45–beta54 (0.975), beta21–tau2 (0.974), beta42–beta54 (0.969), tau4–tau5 (0.968), beta45–gamma57 (0.964).
* Candidatos descartados por κ/VIF: beta54 (con beta45, cos = 0.975), gamma57 (con beta45, cos = 0.964), tau3 (con beta31, cos = 0.897), gamma35 (con beta43, cos = 0.556), beta42 (con beta45, cos = 0.981), tau4 (con beta45, cos = 0.944), tau2 (con beta25, cos = 0.995), beta34 (con beta31, cos = 0.999), tau5 (con beta45, cos = 0.886), beta21 (con beta25, cos = 0.989), beta54 (con beta45, cos = 0.975), gamma57 (con beta45, cos = 0.964).
* e_ajuste por nivel: ±1 %: 26.8 %, ±5 %: 27.2 %, ±10 %: 27.8 %, ±20 %: 28.6 %, ±30 %: 26.5 %, ±40 %: 24.7 %, ±50 %: 25.4 %.
