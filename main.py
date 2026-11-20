"""Punto de entrada del compilador."""
import sys

from errores import ErrorCompilador
from lexico.tokenizer import tokenizar
from sintactico.parser import analizar_sintaxis
from semantico.analizador import analizar_semantica
from interprete.ejecutor import ejecutar_programa

EJEMPLO = """inicio{
  producto(101, "Arroz", 20, 3500)
  entrada(101, 10)
  consultar valor()
}fin
"""


def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as f:
            codigo = f.read()
    else:
        codigo = EJEMPLO

    try:
        tokens = tokenizar(codigo)
        programa = analizar_sintaxis(tokens)
        tabla = analizar_semantica(programa)
        ejecutar_programa(programa, tabla)
    except ErrorCompilador as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()