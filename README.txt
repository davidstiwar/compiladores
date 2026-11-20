# Proyecto de Compiladores: Inventario de tienda

## De qué trata

Inventario de tienda es un lenguaje creado para registrar productos y
controlar las existencias de una tienda. El proyecto está escrito en Python.
Lee programas del lenguaje, revisa su estructura y significado y, si no hay
errores, los ejecuta con un intérprete.

El proyecto no traduce el programa a Python ni genera un ejecutable. El
intérprete ejecuta directamente el árbol de instrucciones.

## Qué permite hacer el lenguaje

- Declarar variables de tipo `int`, `float`, `str` y `bool`.
- Hacer operaciones aritméticas y comparar valores.
- Tomar decisiones con `si` y `sino`.
- Repetir instrucciones con `repetir ... veces`.
- Mostrar datos y pedirlos con `mostrar()` y `leer()`.
- Registrar productos, recibir o retirar unidades, consultar y eliminar.

Todo programa comienza con `inicio{` y termina con `}fin`. No se usan puntos
y coma. También se permiten comentarios con `#`.

Ejemplo:

```text
inicio{
  int codigo = 101
  str nombre = "Arroz"
  int cantidad = 20
  float precio = 3500

  producto(codigo, nombre, cantidad, precio)
  entrada(codigo, 10)
  salida(codigo, 1)
  consultar(codigo)
  consultar valor()
}fin
```

## Reglas principales

- Declara cada variable antes de usarla y no repitas su nombre.
- El tipo de una variable no cambia. Un entero se puede asignar a un `float`.
- Los valores booleanos son `verdadero` y `falso`.
- No se admiten números negativos ni el operador menos unario.
- La condición de `si` debe producir un valor booleano.
- `repetir` necesita un entero no negativo.
- El código de cada producto debe ser único. Su nombre debe ser texto y su
  cantidad inicial y precio deben ser positivos.
- `entrada()` y `salida()` requieren cantidades enteras positivas. No se
  puede retirar más de lo que hay.
- `eliminar()` recibe el código entero del producto.
- `consultar todos()` muestra el inventario; `consultar valor()` muestra la
  cantidad de productos y el valor total.
- El inventario se guarda en memoria y se pierde al cerrar el programa.

## Cómo se procesa un programa

El recorrido va de un archivo al siguiente:

1. `main.py` lee el archivo en UTF-8. Si no se indica uno, usa su ejemplo
   integrado.
2. `lexico/tokenizer.py` separa el texto en tokens. Cada token usa la
   estructura de `lexico/token.py` y guarda tipo, valor, línea y columna.
3. `sintactico/parser.py` revisa el orden de los tokens y crea el árbol con
   las clases de `sintactico/nodos.py`.
4. `semantico/analizador.py` revisa variables, tipos y reglas del inventario.
   Usa `semantico/tabla_simbolos.py` para guardar las variables.
5. `interprete/ejecutor.py` recorre el árbol, ejecuta las instrucciones y
   muestra los resultados.
6. `errores.py` define los errores del compilador y del intérprete. Los
   mensajes incluyen la fase y la ubicación cuando corresponde.

## Comandos

Ejecutar el ejemplo principal:

```powershell
python main.py inventario.txt
```

Ejecutar un programa de prueba:

```powershell
python main.py programas_prueba\01_correcto_inventario.txt
```

Ejecutar las pruebas automáticas:

```powershell
python -m unittest discover -v
```

El archivo `inventario.txt` pide un entero no negativo cuando se ejecuta
`leer(llegada)`.

## Pruebas

La carpeta `programas_prueba` tiene seis programas:

- Tres programas correctos: inventario, variables y condiciones, y lectura
  con repetición.
- Tres programas con errores intencionales: léxico, sintáctico y semántico.

También hay 24 pruebas automáticas en `test_lexico.py`,
`test_semantico.py` y `test_sintactico.py`. Los resultados de los seis
programas y de la suite automática están en `resultados_pruebas.txt`.

La consigna también pide tres programas nuevos además de los seis anteriores.
Esos tres programas todavía no están en `programas_prueba`.

## Actividades del proyecto

### Actividad 3: Conceptualización

Se define el lenguaje Inventario de tienda, se explican sus instrucciones y
se presentan las fases del compilador. La guía del lenguaje y los seis
programas de ejemplo están incluidos en el proyecto.

### Actividad 5: Análisis léxico y sintáctico

El tokenizer reconoce palabras, números, cadenas y símbolos. `gramatica.docx`
contiene las reglas de sintaxis y el parser comprueba la estructura. Los
errores léxicos y sintácticos muestran su ubicación. Para completar la
cantidad de pruebas indicada en la consigna, faltan tres programas nuevos.

### Actividad 7: Trabajo final

El análisis semántico comprueba las variables, los tipos y reglas como las
cantidades y los códigos de productos. Después, el intérprete ejecuta el
árbol del programa.

La consigna menciona como resultado una lista de comandos o una traducción a
Python. La versión actual ejecuta directamente el árbol; no produce ninguno
de esos dos formatos.

## Archivos de documentación

- `README.txt`: descripción del lenguaje, sus reglas y cómo ejecutar el proyecto.
- `Inventario de tienda guía del lenguaje.docx`: reglas y ejemplos para
  escribir programas.
- `gramatica.docx`: reglas EBNF en un archivo de texto; no es un documento
  Word válido.
- `BITACORA.docx`: registro de decisiones y avances.
- `lexico\correcciones de la retroalimentacion.docx`: retroalimentación y
  correcciones.
- `programas_prueba\README.md`: descripción de los programas de prueba.
- `resultados_pruebas.txt`: salidas y resultados de las pruebas.

## Trabajo en grupo

Todos los integrantes deben conocer las fases y poder explicar el código.
El trabajo se guarda en el repositorio compartido; cada integrante hace sus
propios commits durante el avance y el grupo registra sus decisiones en la
bitácora.


Uso de la IA 

en la crean de los test y las pruebas y la convecion a python