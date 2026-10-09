**Asunto:** Avance del paper: respuesta a los revisores y método final

Estimado/a [nombre del tutor]:

Le escribo para resumirle el trabajo realizado desde mi último correo. El objetivo principal fue responder a los tres revisores (ICSTCC 2026, envío 320). Le resumo los resultados por orden de importancia.

**1. Método final (cambio principal)**
A partir de los comentarios de los revisores, el método ahora:
- trabaja con las **mediciones experimentales reales** de PEtab (observables, condiciones, preequilibrio y ruido σ) en lugar de todas las variables internas del modelo;
- selecciona **solo parámetros biológicos**; los parámetros de calibración (escalas y offsets) se reestiman siempre;
- usa como criterio el error tras reestimar (e_ajuste ≤ 0,436, equivalente a cos Δ ≥ 0,9);
- añade un paso de **poda** que elimina los parámetros redundantes.

Al revisar el código original encontré y corregí dos errores en la simulación: condiciones iniciales que no se recalculaban y estados definidos por reglas que no se leían. Estos errores explicaban varios sistemas que antes salían como "técnicos".

**2. Resultados principales**
- **32 de 34** sistemas PEtab son admisibles, en la mayoría con **solo 2 parámetros biológicos**. No lo son Crauste (muy pocos datos) y Beer.
- **Validación externa:** al predecir condiciones experimentales no usadas en el ajuste, el modelo reducido predice **igual o mejor que el modelo completo en 22 de 25 sistemas** con datos reales.
- **Robustez:** los resultados casi no cambian al modificar δ, las tolerancias, el tamaño de las perturbaciones ni los umbrales de R_var, κ y VIF.
- **Costo:** crece linealmente con el número de parámetros. El sistema más grande, con 4 231 parámetros, tarda 2,6 h en 4 núcleos.

**3. Respaldo formal en Lean 4**
Añadí cuatro módulos nuevos, verificados y sin axiomas adicionales:
- la poda produce un subconjunto **mínimo por inclusión**;
- reestimar más parámetros nunca empeora el error, y e_ajuste ≤ e_rel;
- las cotas de error pasan de los estados a las **mediciones**, incluidas las transformaciones log y log10;
- se justifica la aproximación lineal usada en los sistemas grandes.

Con ello, cada paso del método tiene respaldo formal.

**4. Respuesta a cada revisor**
- **Revisor 4** (el más exigente): se atendieron todos los comentarios técnicos (mediciones, validación externa, minimalidad, robustez). Queda pendiente la redacción y la reproducibilidad.
- **Revisor 2:** pide claridad de notación y discutir el efecto de los parámetros de ajuste y el costo. Ya preparé la tabla de notación, el análisis de umbrales y la tabla de costo.
- **Revisor 3:** evaluación muy positiva. Pide explicitar los supuestos y las limitaciones, y la aplicabilidad a datos con ruido, que ya está cubierta.

**5. Hipótesis respaldada**
"En modelos de EDO de sistemas biológicos, el comportamiento observable en los datos depende de forma dominante de muy pocos parámetros biológicos. Reestimando solo ese subconjunto se reproducen las mediciones y se predicen condiciones no utilizadas con una precisión comparable o superior a la del modelo completo."

Se trata de una propiedad **local**, válida alrededor del punto nominal, y así se indicará en el texto.

**6. Próximos pasos**
- Reescribir el paper: título, resumen, método, resultados, limitaciones y conclusiones.
- Redactar la carta de respuesta a los revisores.
- Preparar un ejemplo reproducible y el depósito en Zenodo.

Todo el código, los resultados y las demostraciones están en el repositorio (rama `claude/ode-variable-reduction-papers-tv9zdf`).

Quedo atenta a sus comentarios.

Saludos cordiales,
Mónica Miranda
