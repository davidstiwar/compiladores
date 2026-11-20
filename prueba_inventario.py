
from lexico.tokenizer import tokenizar
from sintactico.parser import analizar_sintaxis
from interprete.ejecutor import ejecutar_programa

codigo = """
inicio {
    producto(101, "Arroz", 20, 3500)
    producto(102, "Azucar", 15, 4200)

    entrada(101, 10)
    salida(101, 5)

    consultar(101)
    consultar("Azucar")
    consultar todos()
    consultar valor()

    eliminar(102)
    consultar todos()
}
"""

tokens = tokenizar(codigo)
arbol = analizar_sintaxis(tokens)
ejecutar_programa(arbol)
