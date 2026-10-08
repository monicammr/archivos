# Cómo correr el ajuste (e_ajuste) de Froehlich, Lang y Chen en tu computadora

Estos tres sistemas son grandes (Froehlich: 1228 especies y 4088 parámetros; Lang: 76
parámetros seleccionados; Chen: 500 especies), así que el ajuste por mínimos cuadrados tarda
mucho. Los programas son los mismos que se usaron para los demás sistemas.

## 1. Preparar Python (una sola vez)

Necesitas Python 3.10 o más reciente. En una terminal (en Windows: "Anaconda Prompt" o
PowerShell):

```
pip install numpy scipy pandas libroadrunner
```

## 2. Descargar el repositorio y el benchmark de PEtab (una sola vez)

```
git clone -b claude/ode-variable-reduction-papers-tv9zdf https://github.com/monicammr/archivos.git
cd archivos/certificados
git clone https://github.com/Benchmarking-Initiative/Benchmark-Models-PEtab.git bench
cd bench
git checkout fcbddf1b900efabdfbdc2b58452c89556e63f1ce
cd ..
```

(El commit `fcbddf1` es la misma versión del benchmark que se usó en todos los cálculos.
Si ya tienes el benchmark en otra carpeta, no hace falta clonarlo: usa `--bench RUTA` abajo,
con RUTA = la carpeta `problems` de tu copia.)

## 3. Froehlich: primero la selección de parámetros

Chen y Lang ya tienen su subconjunto en `resultados/reclasificacion_v2/`. Froehlich lo tendrá
cuando termine el cálculo en curso; si al bajar el repositorio todavía no está
`resultados/reclasificacion_v2/Froehlich_CellSystems2018.json`, genéralo así (tarda horas):

```
python stage_reclass.py --v2 Froehlich_CellSystems2018
```

## 4. Correr el ajuste

Desde la carpeta `archivos/certificados`:

```
python refit_systems.py Chen_MSB2009
python refit_systems.py Lang_PLOSComputBiol2024
python refit_systems.py Froehlich_CellSystems2018
```

Con el benchmark en otra carpeta:

```
python refit_systems.py --bench C:\ruta\Benchmark-Models-PEtab\problems Chen_MSB2009
```

Si tarda demasiado, puedes reducir el trabajo (y anotarlo en el paper):

* `--escenarios 5`: usa sólo los primeros 5 de los 15 escenarios.
* `--max-nfev 200`: limita las simulaciones por ajuste.

Ejemplo: `python refit_systems.py --escenarios 5 --max-nfev 200 Froehlich_CellSystems2018`

## 5. Dónde quedan los resultados

En `resultados/ajuste/`:

* `<sistema>.json`: resumen (mediana de cos Δ, e_rel y e_ajuste, y cuántos escenarios
  cumplen e_ajuste ≤ 0,10 y ≤ 0,436).
* `<sistema>_escenarios.csv`: los valores de cada escenario.

Para que se incluyan en la tabla y la figura, súbelos al repositorio (`git add`, `git commit`,
`git push`) o envíamelos.

## Qué hace el programa (resumen)

Para cada escenario (±5 %, semilla 42): simula el modelo completo con todos los parámetros
perturbados; fija los parámetros descartados en su valor nominal; reestima los seleccionados
con mínimos cuadrados no lineales (`scipy.optimize.least_squares`, método `trf`, en escala
logarítmica, límites [θ₀/10, 10·θ₀], dos puntos de partida), y mide

e_ajuste = ‖y_completo − y_ajustado‖ / ‖y_completo − y_nominal‖.
