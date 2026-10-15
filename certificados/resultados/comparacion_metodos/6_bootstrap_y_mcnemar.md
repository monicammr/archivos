# Estadística por sistema de la comparación de métodos

## Sintético: diferencia de la tasa de acierto (bootstrap por sistemas)

282 casos comunes con señal en 24 sistemas; se remuestrean sistemas completos (B = 10000). Diferencia > 0: nuestro método acierta más.

| Nuestro método contra | Tasa nuestra | Tasa del otro | Diferencia | IC 95 % | p (bootstrap) |
|---|---|---|---|---|---|
| QR pivotado | 56% | 34% | +22.0% | +10.2% a +33.8% | 0.0001 |
| Brun | 56% | 55% | +1.4% | -1.0% a +4.1% | 0.33 |
| Morris | 56% | 48% | +8.5% | +2.3% a +16.4% | 0.0038 |
| Verosimilitud perfilada | 56% | 39% | +17.4% | +7.6% a +27.9% | 0.0008 |

## Admisibilidad a ±5 % (McNemar exacto por sistema)

| Método | Admisibles |
|---|---|
| Nuestro método | 28 de 28 |
| QR pivotado | 14 de 28 |
| Brun | 26 de 28 |
| Morris | 23 de 28 |
| Verosimilitud perfilada | 18 de 27 |

| Nuestro método contra | Sistemas comparados | Sólo el nuestro admisible | Sólo el otro | p |
|---|---|---|---|---|
| QR pivotado | 28 | 14 | 0 | 0.00012 |
| Brun | 28 | 2 | 0 | 0.5 |
| Morris | 28 | 5 | 0 | 0.062 |
| Verosimilitud perfilada | 27 | 9 | 0 | 0.0039 |

## Admisibilidad a ±20 % (McNemar exacto por sistema)

| Método | Admisibles |
|---|---|
| Nuestro método | 27 de 28 |
| QR pivotado | 15 de 28 |
| Brun | 25 de 28 |
| Morris | 23 de 28 |
| Verosimilitud perfilada | 18 de 27 |

| Nuestro método contra | Sistemas comparados | Sólo el nuestro admisible | Sólo el otro | p |
|---|---|---|---|---|
| QR pivotado | 28 | 12 | 0 | 0.00049 |
| Brun | 28 | 2 | 0 | 0.5 |
| Morris | 28 | 4 | 0 | 0.12 |
| Verosimilitud perfilada | 27 | 8 | 0 | 0.0078 |
