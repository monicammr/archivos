# Datos reales: Wilcoxon pareado sobre el χ²/n de prueba

Estadístico por sistema: log(χ²_otro / χ²_nuestro). Empate: diferencia menor del 5 %. Cociente mediano menor que 1: el otro método tiene menor χ² (predice mejor). Todas las variantes salvo el anidado usan θ₀ (estimado con todos los datos) como ancla.

| Nuestro método contra | Sistemas | Nuestro mejor | Peor | Empate | Cociente mediano | p |
|---|---|---|---|---|---|---|
| QR pivotado | 28 | 2 | 10 | 16 | 0.99 | 0.026 |
| Brun | 28 | 3 | 5 | 20 | 1.00 | 0.27 |
| Morris | 28 | 4 | 6 | 18 | 1.00 | 0.46 |
| Verosimilitud perfilada | 27 | 7 | 9 | 11 | 1.00 | 0.44 |
| Subconjunto aleatorio (mediana de 20) | 28 | 3 | 9 | 16 | 1.00 | 0.27 |
| Conjunto vacío (sólo calibración) | 28 | 2 | 13 | 13 | 0.99 | 0.0027 |
| Modelo completo (entrenamiento) | 29 | 20 | 3 | 6 | 1.23 | 8.2e-05 |
| Reducido anidado (sin fuga) | 29 | 21 | 3 | 5 | 1.35 | 7.2e-05 |
| θ₀ publicado | 29 | 2 | 20 | 7 | 0.90 | 0.00022 |
