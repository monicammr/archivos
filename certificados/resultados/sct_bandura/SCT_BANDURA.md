# SCT Bandura con el método final (valores: codigo; entradas: codigo)

Modelo lineal de 6 estados, 22 parámetros, 3 condiciones de entrada; salida medida y = x₄. Sin datos experimentales ni parámetros de calibración.

| Variante | Salidas | Sin efecto | κ (con efecto) | VIF máx (con efecto) | Pares con cos ≥ 0,95 | Etapa | S | e_rel ±5 % | e_ajuste ±5 % | Patrón |
|---|---|---|---|---|---|---|---|---|---|
| salida | 240 | gamma35, gamma36, gamma57, gamma68 | inf | 4.01e+14 | 55 | Stage 2 | beta43, tau4 | 61.9 % | 2.0 % | A |
| estados | 1440 | gamma35, gamma36, gamma57, gamma68 | 1.64e+04 | 1.88e+07 | 9 | Stage 1 | gamma33, beta43 | 20.2 % | 17.7 % | A |

## salida

* Etapa 1: beta43, tau4, gamma64, tau6 (R_var = 51.7 %).
* Antes de la poda: beta43, tau4; podados: —.
* Pares casi colineales (cos ≥ 0,95): beta46–gamma64 (1.000), beta25–beta42 (1.000), beta21–beta42 (1.000), beta21–beta25 (1.000), beta14–beta54 (1.000), tau1–tau5 (1.000), beta43–gamma33 (1.000), beta14–beta21 (1.000), beta14–beta42 (1.000), beta14–beta25 (1.000), beta21–beta54 (1.000), beta42–beta54 (1.000).
* Candidatos descartados por κ/VIF: gamma33 (con beta43, cos = 1.000), tau3 (con tau4, cos = 0.988), beta42 (con beta43, cos = 0.852), beta54 (con beta43, cos = 0.860), beta25 (con beta43, cos = 0.852), beta34 (con beta43, cos = 0.968), tau5 (con beta43, cos = 0.894), tau2 (con beta43, cos = 0.903), beta14 (con beta43, cos = 0.858), beta21 (con beta43, cos = 0.853), tau1 (con beta43, cos = 0.893), beta46 (con gamma64, cos = 1.000), beta45 (con beta43, cos = 0.916), beta31 (con beta43, cos = 0.888), gamma33 (con beta43, cos = 1.000).
* e_ajuste por nivel: ±1 %: 2.1 %, ±5 %: 2.0 %, ±10 %: 2.0 %, ±20 %: 1.8 %, ±30 %: 1.7 %, ±40 %: 1.5 %, ±50 %: 1.5 %.

## estados

* Etapa 1: gamma33, beta43 (R_var = 96.6 %).
* Antes de la poda: gamma33, beta43; podados: —.
* Pares casi colineales (cos ≥ 0,95): beta21–beta25 (1.000), beta54–tau5 (0.992), beta42–beta45 (0.987), beta14–tau1 (0.985), beta21–tau2 (0.983), beta25–tau2 (0.982), beta31–beta34 (0.959), beta34–gamma33 (0.954), tau2–tau5 (0.951).
* e_ajuste por nivel: ±1 %: 18.1 %, ±5 %: 17.7 %, ±10 %: 17.1 %, ±20 %: 15.9 %, ±30 %: 16.8 %, ±40 %: 18.3 %, ±50 %: 20.0 %.
