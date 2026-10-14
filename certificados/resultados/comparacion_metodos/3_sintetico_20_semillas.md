# Experimento sintético sin fuga: cinco métodos, 20 semillas (42–61)

Casos comunes a los cinco métodos y con señal (χ²/n de θ₀ ≥ 2): 280 (23 sistemas). Acierto: e_pred ≤ 0.436.

| Método | Aciertos | Mediana por semilla | Rango por semilla |
|---|---|---|---|
| Nuestro método | 151 de 280 (54%) | 57% | 21%–67% |
| QR pivotado | 96 de 280 (34%) | 36% | 7%–50% |
| Brun | 154 de 280 (55%) | 55% | 36%–75% |
| Morris | 134 de 280 (48%) | 48% | 28%–75% |
| Verosimilitud perfilada | 109 de 280 (39%) | 40% | 14%–67% |

## Acierto: casos en que sólo uno de los dos acierta (prueba binomial exacta)

Las 20 semillas de un mismo sistema no son independientes: estos valores de p son optimistas.

| Nuestro método contra | Sólo el nuestro acierta | Sólo el otro acierta | p |
|---|---|---|---|
| QR pivotado | 70 | 15 | 1.2e-09 |
| Brun | 13 | 16 | 0.71 |
| Morris | 38 | 21 | 0.036 |
| Verosimilitud perfilada | 58 | 16 | 9.7e-07 |

## Error de predicción por sistema (Wilcoxon pareado)

Estadístico por sistema: mediana, sobre las semillas, de log(e_pred del otro / e_pred nuestro); todas las semillas con al menos 10 pares. Mayor que 0: nuestro método con menor error.

| Nuestro método contra | Sistemas | Nuestro mejor | Peor | Igual | Cociente mediano | p |
|---|---|---|---|---|---|---|
| QR pivotado | 28 | 14 | 12 | 2 | 1.01 | 0.24 |
| Brun | 28 | 10 | 12 | 6 | 1.00 | 0.14 |
| Morris | 28 | 12 | 10 | 6 | 1.00 | 0.54 |
| Verosimilitud perfilada | 25 | 14 | 7 | 4 | 1.04 | 0.32 |
