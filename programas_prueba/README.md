# Programas de prueba

Hay seis ejemplos: tres programas válidos y tres con errores intencionales.

| Archivo | Qué comprueba |
| --- | --- |
| `01_correcto_inventario.txt` | Registro, entradas, salidas y valor total (`87500.00`). |
| `02_correcto_variables_y_condicion.txt` | Variables y condiciones; imprime `Hay stock`. |
| `03_correcto_leer_y_repetir.txt` | Lectura y repetición; con `5`, imprime `5`, `6` y `7`. |
| `04_error_lexico.txt` | Error léxico por el carácter `$`. |
| `05_error_sintactico.txt` | Error sintáctico por falta de `veces`. |
| `06_error_semantico.txt` | Error semántico por usar `total` sin declararla. |

Ejecuta un ejemplo desde la carpeta del proyecto:

```powershell
python main.py programas_prueba\01_correcto_inventario.txt
```

Al probar el tercero, escribe un entero no negativo cuando se solicite.
Los resultados completos están en
[resultados_pruebas.txt](../resultados_pruebas.txt).
