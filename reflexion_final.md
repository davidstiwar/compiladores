# Reflexión sobre el proyecto

Una de las partes más difíciles fue organizarnos como grupo. Tuvimos que pensar
cómo repartir el trabajo y ponernos de acuerdo sobre quién se encargaría de
cada tarea. En algunos momentos discutimos esa distribución, y eso nos hizo
ver que planear el trabajo también requiere tiempo y comunicación.

También nos costó entender la ruta que sigue el lenguaje desde que se escribe
hasta que produce un resultado. Al comienzo era fácil confundir las fases,
pero al trabajar con el proyecto vimos cómo se conectan: el analizador léxico
separa el texto en tokens, el sintáctico comprueba su estructura y construye
el árbol, y el semántico revisa las variables, los tipos y las reglas del
inventario. Después, el programa puede ejecutarse con el intérprete.

Durante el desarrollo tomamos decisiones para mantener el lenguaje manejable:
usar comandos propios del inventario, definir tipos para las variables y
escribir los bloques con llaves. Acordamos que el programa comenzara con
`inicio` y terminara con `fin`, que `sino` fuera una sola palabra y que las
instrucciones no necesitaran punto y coma. También tuvimos que procurar que la
guía, la gramática y el código describieran las mismas reglas. Al principio el
intérprete ejecutaba directamente el árbol del programa. Para completar la
salida que pide la consigna, añadimos la opción de traducirlo a Python sin
quitar el modo de ejecución original.

El proyecto nos enseñó que no basta con programar cada parte por separado:
hay que coordinar el trabajo y comprobar que todas las fases formen un mismo
recorrido. La próxima vez repartiríamos las tareas desde el inicio y
revisaríamos juntos los avances con más frecuencia.
