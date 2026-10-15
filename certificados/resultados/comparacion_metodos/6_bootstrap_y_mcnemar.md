# Estadística por sistema de la comparación de métodos

## Sintético: diferencia de la tasa de acierto (bootstrap por sistemas)

280 casos comunes con señal en 23 sistemas; se remuestrean sistemas completos (B = 10000). Diferencia > 0: nuestro método acierta más.

| Nuestro método contra | Tasa nuestra | Tasa del otro | Diferencia | IC 95 % | p (bootstrap) |
|---|---|---|---|---|---|
| QR pivotado | 54% | 34% | +19.6% | +6.5% a +32.5% | 0.003 |
| Brun | 54% | 55% | -1.1% | -7.6% a +3.5% | 0.82 |
| Morris | 54% | 48% | +6.1% | -3.2% a +15.4% | 0.21 |
| Verosimilitud perfilada | 54% | 39% | +15.0% | +4.3% a +26.5% | 0.0058 |

## Admisibilidad a ±5 % (McNemar exacto por sistema)

| Método | Admisibles |
|---|---|
| Nuestro método | 29 de 29 |
| QR pivotado | 13 de 29 |
| Brun | 24 de 29 |
| Morris | 21 de 29 |
| Verosimilitud perfilada | 17 de 26 |

| Nuestro método contra | Sistemas comparados | Sólo el nuestro admisible | Sólo el otro | p |
|---|---|---|---|---|
| QR pivotado | 29 | 16 | 0 | 3.1e-05 |
| Brun | 29 | 5 | 0 | 0.062 |
| Morris | 29 | 8 | 0 | 0.0078 |
| Verosimilitud perfilada | 26 | 9 | 0 | 0.0039 |

## Admisibilidad a ±20 % (McNemar exacto por sistema)

| Método | Admisibles |
|---|---|
| Nuestro método | 28 de 29 |
| QR pivotado | 14 de 29 |
| Brun | 23 de 29 |
| Morris | 21 de 29 |
| Verosimilitud perfilada | 17 de 26 |

| Nuestro método contra | Sistemas comparados | Sólo el nuestro admisible | Sólo el otro | p |
|---|---|---|---|---|
| QR pivotado | 29 | 14 | 0 | 0.00012 |
| Brun | 29 | 5 | 0 | 0.062 |
| Morris | 29 | 7 | 0 | 0.016 |
| Verosimilitud perfilada | 26 | 8 | 0 | 0.0078 |
