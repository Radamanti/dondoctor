# Declaración de uso de herramientas de IA

Durante el desarrollo de la prueba técnica se utilizaron herramientas de
inteligencia artificial como apoyo puntual para consultar conceptos,
contrastar alternativas técnicas y revisar algunas decisiones de
implementación.

El uso de estas herramientas tuvo principalmente un carácter de consulta
y acompañamiento, especialmente en temas como:

-   conceptos relacionados con arquitecturas de datos y procesamiento
    por capas;
-   alternativas para realizar consultas analíticas sobre archivos
    Parquet;
-   apoyo para documentar de forma clara algunos componentes de la
    solución.

Las respuestas obtenidas fueron utilizadas como referencia y
contrastadas con el contexto de la prueba y el código
desarrollado

## Casos contradictorios

Durante el desarrollo surgieron algunas situaciones en las que la
recomendación inicial de la herramienta no coincidía completamente con
el enfoque que se decidió implementar.

Por ejemplo, se plantearon alternativas para incorporar DuckDB de una
forma más central dentro del flujo. Finalmente se optó por mantener
Parquet como formato principal de persistencia y utilizar DuckDB
principalmente como herramienta de consulta y análisis sobre los datos,
ya que esto mantenía más simple el pipeline y permitía separar
transformación, almacenamiento y explotación.

También se plantearon diferentes formas de organizar las capas y los
artefactos generados, en lugar de modificar la estructura existente cada
vez que aparecía una alternativa, se decidió conservar una separación
clara entre Bronze, Silver y Gold y realizar ajustes únicamente cuando
aportaban valor al flujo de la prueba.

En otros casos, algunas sugerencias de implementación fueron descartadas
porque podían resolver un problema puntual, pero introducían complejidad
innecesaria para el alcance de la solución.

Estos casos fueron útiles para contrastar alternativas, pero la decisión
final se tomó considerando el objetivo de la prueba, la mantenibilidad y
la facilidad de ejecución de la solución.

## Consideración final

La IA fue utilizada como herramienta de consulta y apoyo técnico, no
como sustituto del análisis requerido para la prueba. La implementación
final corresponde a las decisiones adoptadas durante el desarrollo y a
la validación realizada sobre los datos y el funcionamiento del
pipeline.
