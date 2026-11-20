"""Punto de entrada del compilador."""
import sys

from errores import ErrorCompilador
from lexico.tokenizer import tokenizar
from sintactico.parser import analizar_sintaxis
from semantico.analizador import analizar_semantica
from interprete.ejecutor import ejecutar_programa
from generador_python import generar_python

EJEMPLO = """inicio{
  producto(101, "Arroz", 20, 3500)
  entrada(101, 10)
  consultar valor()
}fin
"""


def main():
    argumentos = sys.argv[1:]
    traducir_a_python = argumentos[:1] == ["--python"]
    if traducir_a_python:
        argumentos = argumentos[1:]

    max_argumentos = 2 if traducir_a_python else 1
    if len(argumentos) > max_argumentos:
        print("Uso: python main.py [archivo]")
        print("     python main.py --python [archivo]")
        print("     python main.py --python archivo salida.py")
        sys.exit(2)

    if argumentos:
        with open(argumentos[0], encoding="utf-8") as f:
            codigo = f.read()
    else:
        codigo = EJEMPLO

    try:
        tokens = tokenizar(codigo)
        programa = analizar_sintaxis(tokens)
        tabla = analizar_semantica(programa)
        if traducir_a_python:
            traduccion = generar_python(programa)
            if len(argumentos) == 2:
                with open(argumentos[1], "w", encoding="utf-8") as f:
                    f.write(traduccion)
                print(f"Traducción guardada en: {argumentos[1]}")
            else:
                print(traduccion, end="")
        else:
            ejecutar_programa(programa, tabla)
    except ErrorCompilador as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()