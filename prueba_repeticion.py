
from lexico.tokenizer import tokenizar
from sintactico.parser import analizar_sintaxis
from interprete.ejecutor import ejecutar_programa

codigo = """
inicio {
    int contador = 1

    repetir 3 veces {
        mostrar contador
        contador = contador + 1
    }
}
"""

tokens = tokenizar(codigo)
arbol = analizar_sintaxis(tokens)
ejecutar_programa(arbol)
