# Experimento sintético sin fuga: cinco métodos, 20 semillas (42–61)

Casos comunes a los cinco métodos y con señal (χ²/n de θ₀ ≥ 2): 282 (24 sistemas). Acierto: e_pred ≤ 0.436.

| Método | Aciertos | Mediana por semilla | Rango por semilla |
|---|---|---|---|
| Nuestro método | 158 de 282 (56%) | 59% | 29%–73% |
| QR pivotado | 96 de 282 (34%) | 36% | 7%–50% |
| Brun | 154 de 282 (55%) | 55% | 36%–75% |
| Morris | 134 de 282 (48%) | 47% | 28%–75% |
| Verosimilitud perfilada | 109 de 282 (39%) | 40% | 14%–67% |

## Acierto: casos en que sólo uno de los dos acierta (prueba binomial exacta)

Las 20 semillas de un mismo sistema no son independientes: estos valores de p son optimistas.

| Nuestro método contra | Sólo el nuestro acierta | Sólo el otro acierta | p |
|---|---|---|---|
| QR pivotado | 76 | 14 | 1.8e-11 |
| Brun | 13 | 9 | 0.52 |
| Morris | 38 | 14 | 0.0012 |
| Verosimilitud perfilada | 64 | 15 | 2.3e-08 |

## Error de predicción por sistema (Wilcoxon pareado)

Estadístico por sistema: mediana, sobre las semillas, de log(e_pred del otro / e_pred nuestro); todas las semillas con al menos 10 pares. Mayor que 0: nuestro método con menor error.

| Nuestro método contra | Sistemas | Nuestro mejor | Peor | Igual | Cociente mediano | p |
|---|---|---|---|---|---|---|
| QR pivotado | 28 | 16 | 10 | 2 | 1.03 | 0.075 |
| Brun | 28 | 10 | 10 | 8 | 1.00 | 0.37 |
| Morris | 28 | 12 | 9 | 7 | 1.00 | 0.29 |
| Verosimilitud perfilada | 27 | 16 | 7 | 4 | 1.04 | 0.23 |
