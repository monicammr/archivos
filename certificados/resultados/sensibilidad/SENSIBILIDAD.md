# Sensibilidad a las decisiones técnicas (comentario 6)

Cada fila resume una variante frente a la configuración del artículo (δ = 1 %, tolerancias 1e-7/1e-10, perturbación ±5 %, malla de 60 puntos en [0, T]).

| Variante | Sobre | Sistemas | Mismo S | Jaccard medio | Misma etapa | Misma decisión de admisibilidad |
|---|---|---|---|---|---|---|
| δ = 0,1 % | salidas | 26 | 26/26 | 1.00 | 26/26 | 26/26 |
| δ = 5 % | salidas | 15 | 15/15 | 1.00 | 15/15 | 15/15 |
| tolerancias 1e-9 / 1e-12 | salidas | 2 | 2/2 | 1.00 | 2/2 | 2/2 |
| perturbación ±1 % | salidas | 26 | 26/26 | 1.00 | 25/26 | 25/26 |
| perturbación ±10 % | salidas | 15 | 15/15 | 1.00 | 15/15 | 15/15 |
| malla de 30 puntos | estados | 15 | 13/15 | 0.93 | 15/15 | 15/15 |

## Sistemas cuya decisión de admisibilidad cambia

| Variante | Sistema | Base | Variante | e_ajuste base | e_ajuste variante |
|---|---|---|---|---|---|
| perturbación ±1 % | Perelson_Science1996 | ✓ | ✗ | 0.0 % | — |
