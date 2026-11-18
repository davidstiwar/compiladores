"""Punto de entrada del compilador de Inventario de tienda.

Uso:
    python main.py programa.txt     # analiza el archivo indicado
    python main.py                  # analiza un programa de ejemplo
"""
import sys

from lexico.tokenizer import tokenizar, ErrorLexico

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
    except ErrorLexico as e:
        print(e)
        sys.exit(1)

    for t in tokens:
        if t.tipo != "NUEVA_LINEA":
            print(t)


if __name__ == "__main__":
    main()