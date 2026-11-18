from .token import Token

PALABRAS_RESERVADAS = {
    # Programa
    "inicio": "INICIO",
    "fin": "FIN",
    # Tipos de datos
    "int": "INT",
    "float": "FLOAT",
    "str": "STR",
    "bool": "BOOL",
    # Decidir y repetir
    "si": "SI",
    "sino": "SINO",
    "repetir": "REPETIR",
    "veces": "VECES",
    # Valores especiales
    "verdadero": "VERDADERO",
    "falso": "FALSO",
    "null": "NULL",
    # Entrada y salida
    "mostrar": "MOSTRAR",
    "leer": "LEER",
    # Inventario
    "producto": "PRODUCTO",
    "entrada": "ENTRADA",
    "salida": "SALIDA",
    "consultar": "CONSULTAR",
    "eliminar": "ELIMINAR",
    # Consultas generales
    "todos": "TODOS",
    "valor": "VALOR",
}

LLAVES = {"{": "LLAVE_ABRE", "}": "LLAVE_CIERRA"}

# Operadores y símbolos (primero los de dos caracteres)
OPERADORES_DOBLES = {
    "==": "IGUAL_IGUAL", "!=": "DIFERENTE", ">=": "MAYOR_IGUAL", "<=": "MENOR_IGUAL",
    "&&": "Y", "||": "O",
    "+=": "MAS_IGUAL", "-=": "MENOS_IGUAL", "*=": "POR_IGUAL", "/=": "DIV_IGUAL",
}
SIMBOLOS = {
    "+": "MAS", "-": "MENOS", "*": "POR", "/": "DIVIDIR", "=": "ASIGNAR",
    ">": "MAYOR", "<": "MENOR", "!": "NO",
    "(": "PAREN_ABRE", ")": "PAREN_CIERRA", ",": "COMA",
}


class ErrorLexico(Exception):
    def __init__(self, mensaje, linea, columna):
        self.mensaje, self.linea, self.columna = mensaje, linea, columna
        super().__init__(f"Error léxico (línea {linea}, columna {columna}): {mensaje}")


def tokenizar(texto):
    """Recorre el texto y devuelve la lista de tokens.
    Se detiene en el primer error léxico (lanza ErrorLexico)."""
    tokens = []
    i, linea, col = 0, 1, 1
    n = len(texto)

    def avanzar(k=1):
        nonlocal i, linea, col
        for _ in range(k):
            if texto[i] == "\n":
                linea += 1
                col = 1
            else:
                col += 1
            i += 1

    while i < n:
        c = texto[i]

        if c == "\n":
            tokens.append(Token("NUEVA_LINEA", "\\n", linea, col))
            avanzar()
        elif c in " \t\r":
            avanzar()
        elif c == "#":  # comentario hasta el final de la línea
            while i < n and texto[i] != "\n":
                avanzar()
        elif c.isalpha() or c == "_":
            ini, c0 = i, col
            while i < n and (texto[i].isalnum() or texto[i] == "_"):
                avanzar()
            palabra = texto[ini:i]
            tipo = PALABRAS_RESERVADAS.get(palabra, "IDENTIFICADOR")
            tokens.append(Token(tipo, palabra, linea, c0))
        elif c.isdigit():
            ini, c0 = i, col
            while i < n and texto[i].isdigit():
                avanzar()
            tipo = "ENTERO"
            if i + 1 < n and texto[i] == "." and texto[i + 1].isdigit():
                tipo = "DECIMAL"
                avanzar()
                while i < n and texto[i].isdigit():
                    avanzar()
            tokens.append(Token(tipo, texto[ini:i], linea, c0))
        elif c in "\"'":
            comilla, l0, c0 = c, linea, col
            avanzar()
            ini = i
            while i < n and texto[i] != comilla and texto[i] != "\n":
                avanzar()
            if i >= n or texto[i] != comilla:
                raise ErrorLexico(f"texto sin cerrar (falta la comilla {comilla})", l0, c0)
            tokens.append(Token("TEXTO", texto[ini:i], l0, c0))
            avanzar()  # comilla de cierre
        elif c in LLAVES:
            tokens.append(Token(LLAVES[c], c, linea, col))
            avanzar()
        elif texto[i:i + 2] in OPERADORES_DOBLES:
            tokens.append(Token(OPERADORES_DOBLES[texto[i:i + 2]], texto[i:i + 2], linea, col))
            avanzar(2)
        elif c in SIMBOLOS:
            tokens.append(Token(SIMBOLOS[c], c, linea, col))
            avanzar()
        else:
            raise ErrorLexico(f"carácter no reconocido {c!r}", linea, col)

    tokens.append(Token("EOF", "", linea, col))
    return tokens