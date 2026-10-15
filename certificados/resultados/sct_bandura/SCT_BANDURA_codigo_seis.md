# SCT Bandura con el método final (valores: codigo; entradas: seis)

Modelo lineal de 6 estados, 22 parámetros, 3 condiciones de entrada; salida medida y = x₄. Sin datos experimentales ni parámetros de calibración.

| Variante | Salidas | Sin efecto | κ (con efecto) | VIF máx (con efecto) | Pares con cos ≥ 0,95 | Etapa | S | e_rel ±5 % | e_ajuste ±5 % | Patrón |
|---|---|---|---|---|---|---|---|---|---|
| salida | 480 | — | inf | 3.35e+15 | 28 | Stage 2 | gamma57, beta43 | 88.4 % | 16.5 % | A |
| estados | 2880 | — | 67.3 | 250 | 7 | Stage 2 | gamma57, gamma33, beta42 | 70.5 % | 41.4 % | B |

## salida

* Etapa 1: gamma57, beta43, gamma33, tau4, gamma36, beta46, gamma64, tau6 (R_var = 44.3 %).
* Antes de la poda: gamma57, beta43; podados: —.
* Pares casi colineales (cos ≥ 0,95): beta14–beta54 (1.000), beta25–beta42 (1.000), beta14–beta21 (1.000), beta21–beta54 (1.000), beta31–tau1 (1.000), beta25–gamma57 (0.999), beta42–gamma57 (0.999), tau2–tau5 (0.998), beta45–tau5 (0.998), beta31–beta54 (0.997), beta14–beta31 (0.997), beta45–tau2 (0.997).
* Candidatos descartados por κ/VIF: beta42 (con gamma57, cos = 0.999), beta25 (con gamma57, cos = 0.999), tau5 (con gamma57, cos = 0.991), tau2 (con gamma57, cos = 0.982), gamma35 (con beta43, cos = 0.461), beta45 (con gamma57, cos = 0.988), tau3 (con beta43, cos = 0.614), beta54 (con beta43, cos = 0.669), beta34 (con gamma57, cos = 0.769), beta14 (con beta43, cos = 0.669), beta21 (con beta43, cos = 0.669), tau1 (con gamma57, cos = 0.667), gamma68 (con beta46, cos = 0.703), beta31 (con beta43, cos = 0.666), beta42 (con gamma57, cos = 0.999).
* e_ajuste por nivel: ±1 %: 17.0 %, ±5 %: 16.5 %, ±10 %: 15.9 %, ±20 %: 14.6 %, ±30 %: 14.7 %, ±40 %: 13.8 %, ±50 %: 11.8 %.

## estados

* Etapa 1: gamma57, gamma33, tau2, beta42, gamma35, beta43, tau3, tau4, beta54, beta34, beta14, gamma36, gamma64, gamma68, beta46, tau6 (R_var = 55.7 %).
* Antes de la poda: gamma57, gamma33, tau2, beta42; podados: tau2.
* Pares casi colineales (cos ≥ 0,95): beta14–tau1 (0.990), gamma57–tau5 (0.986), beta42–beta45 (0.984), beta25–tau2 (0.968), beta31–beta34 (0.967), tau2–tau5 (0.958), beta25–gamma57 (0.954).
* Candidatos descartados por κ/VIF: beta25 (con gamma57, cos = 0.954), tau5 (con gamma57, cos = 0.986), beta45 (con beta42, cos = 0.984), beta21 (con beta54, cos = 0.932), tau1 (con beta14, cos = 0.990), beta31 (con beta34, cos = 0.967), beta25 (con gamma57, cos = 0.954), tau5 (con gamma57, cos = 0.986).
* e_ajuste por nivel: ±1 %: 41.1 %, ±5 %: 41.4 %, ±10 %: 41.8 %, ±20 %: 42.0 %, ±30 %: 42.7 %, ±40 %: 44.1 %, ±50 %: 44.7 %.
