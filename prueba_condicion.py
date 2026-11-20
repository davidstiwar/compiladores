
from lexico.tokenizer import tokenizar
from sintactico.parser import analizar_sintaxis
from interprete.ejecutor import ejecutar_programa

codigo = """
inicio {
    int cantidad = 10

    si cantidad > 5 {
        mostrar "Hay suficiente cantidad"
    } sino {
        mostrar "Cantidad insuficiente"
    }
}
"""

tokens = tokenizar(codigo)
arbol = analizar_sintaxis(tokens)
ejecutar_programa(arbol)
