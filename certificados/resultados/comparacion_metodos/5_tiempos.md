# Tiempo de cómputo (segundos de reloj)

Servidor de 128 núcleos, compartido por varios cálculos a la vez (los tiempos están inflados, nunca subestimados). Nuestro método completo = selección + admisibilidad + poda, desde cero.

Los 8 sistemas linealizados se repitieron con el código corregido (columnas de calibración en J); la última columna indica si esa corrida reproduce la selección publicada.

| Sistema | p | Nuestro método, paralelo | Nuestro método, 1 núcleo | Verosimilitud perfilada (1.ª ronda, 120 núcleos) | ¿Misma selección que el artículo? (código anterior) | Código corregido |
|---|---|---|---|---|---|---|
| Alkan | 44 | 24 | 46 | 1.65e+03 | sí | sí (25.4 s) |
| Armistead | 14 | 6.8 | 5.9 | 2.7 | sí | – |
| Bachmann | 113 | 23.1 | 27.2 | – | **no** | sí (9.7 s) |
| Beer | 72 | 211 | 309 | – | sí | sí (197 s) |
| Bertozzi | 8 | 3.2 | 4.3 | 0.5 | sí | – |
| Blasi | 9 | 4.5 | 4.5 | – | sí | – |
| Boehm | 9 | 4.5 | 3.4 | 0.2 | sí | – |
| Borghans | 23 | 17.9 | 37.1 | 30.7 | sí | – |
| Brannmark | 22 | 27.1 | 37.1 | 13.2 | sí | – |
| Bruno | 13 | 23.2 | 33.8 | 2.3 | sí | – |
| Chen | 155 | 3.61e+03 | – | – | **no** | sí (1.96e+03 s) |
| Crauste | 12 | 36.4 | 51.1 | – | sí | – |
| Elowitz | 21 | 11.5 | 8.7 | 9.6 | sí | – |
| Fiedler | 22 | 17 | 12.1 | 0.6 | sí | – |
| Fujita | 19 | 77.8 | 78.8 | 25.9 | sí | – |
| Giordano | 50 | 12.5 | 16.9 | 123 | sí | – |
| Isensee | 46 | 741 | 1.41e+03 | 4.45e+03 | **no** | sí (584 s) |
| Lang | 294 | 411 | – | – | **no** | sí (199 s) |
| Laske | 13 | 26.9 | 28.1 | 5.3 | sí | – |
| Liu | 9 | 4.2 | 6.3 | 1.1 | sí | – |
| Lucarelli | 84 | 61.9 | 75.1 | – | sí | sí (34.7 s) |
| Okuonghae | 16 | 3.4 | 5.7 | 6.8 | sí | – |
| Oliveira | 12 | 5 | 10.9 | 5.1 | sí | – |
| Perelson | 3 | 2.1 | 2.7 | 0.4 | sí | – |
| Rahman | 9 | 2.9 | 4.2 | 2.1 | sí | – |
| Raia | 39 | 30.5 | 49.2 | 14.1 | sí | – |
| Raimundez | 136 | 173 | 306 | – | **no** | sí (120 s) |
| SalazarCavazos | 6 | 67.5 | 37.6 | 13.9 | sí | – |
| Schwen | 30 | 92.9 | 147 | 110 | sí | – |
| Smith | 25 | 1.14e+03 | 1.7e+03 | 854 | sí | – |
| Sneyd | 15 | 20.7 | 17.6 | 4 | sí | – |
| Weber | 36 | 17.6 | 23.1 | 120 | sí | – |
| Zhao | 28 | 7.5 | 21.8 | 20.5 | sí | – |
| Zheng | 46 | 13.9 | 17 | 287 | sí | – |

Los tiempos de la verosimilitud perfilada no incluyen el primer ajuste completo de los sistemas que ya lo tenían de un intento anterior ni las rondas de corrección del mínimo.
