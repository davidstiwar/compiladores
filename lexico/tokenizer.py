
import re

from .token import Token
from errores import ErrorLexico


PALABRAS_RESERVADAS = {
    "inicio": "INICIO",
    "int": "INT",
    "float": "FLOAT",
    "str": "STR",
    "bool": "BOOL",
    "si": "SI",
    "sino": "SINO",
    "repetir": "REPETIR",
    "veces": "VECES",
    "verdadero": "VERDADERO",
    "falso": "FALSO",
    "null": "NULL",
    "mostrar": "MOSTRAR",
    "leer": "LEER",
    "producto": "PRODUCTO",
    "entrada": "ENTRADA",
    "salida": "SALIDA",
    "consultar": "CONSULTAR",
    "eliminar": "ELIMINAR",
    "todos": "TODOS",
    "valor": "VALOR",
}


OPERADORES = {
    "+=": "SUMA_ASIGNACION",
    "-=": "RESTA_ASIGNACION",
    "*=": "MULTIPLICACION_ASIGNACION",
    "/=": "DIVISION_ASIGNACION",
    "==": "IGUAL_IGUAL",
    "!=": "DIFERENTE",
    ">=": "MAYOR_IGUAL",
    "<=": "MENOR_IGUAL",
    "&&": "AND",
    "||": "OR",
    "+": "MAS",
    "-": "MENOS",
    "*": "MULTIPLICACION",
    "/": "DIVISION",
    "=": "ASIGNACION",
    ">": "MAYOR",
    "<": "MENOR",
    "!": "NOT",
    "{": "LLAVE_ABRE",
    "}": "LLAVE_CIERRA",
    "(": "PARENTESIS_ABRE",
    ")": "PARENTESIS_CIERRA",
    ",": "COMA",
}


def tokenizar(codigo):
    tokens = []
    linea = 1
    columna = 1
    posicion = 0

    while posicion < len(codigo):
        caracter = codigo[posicion]

        if caracter in " \t\r":
            posicion += 1
            columna += 1
            continue

        if caracter == "\n":
            tokens.append(Token("NUEVA_LINEA", "\\n", linea, columna))
            posicion += 1
            linea += 1
            columna = 1
            continue

        if caracter == "#":
            while posicion < len(codigo) and codigo[posicion] != "\n":
                posicion += 1
                columna += 1
            continue

        if caracter in ("'", '"'):
            comilla = caracter
            inicio = posicion
            columna_inicio = columna
            posicion += 1
            columna += 1

            while posicion < len(codigo) and codigo[posicion] != comilla:
                if codigo[posicion] == "\n":
                    raise ErrorLexico(
                        "Error léxico: texto sin cerrar",
                        linea,
                        columna_inicio
                    )
                if codigo[posicion] == "\\" and posicion + 1 < len(codigo):
                    posicion += 1
                    columna += 1
                posicion += 1
                columna += 1

            if posicion >= len(codigo):
                raise ErrorLexico(
                    "Error léxico: texto sin cerrar",
                    linea,
                    columna_inicio
                )

            posicion += 1
            columna += 1
            valor = codigo[inicio:posicion]

            tokens.append(Token("CADENA", valor, linea, columna_inicio))
            continue

        if caracter.isdigit():
            inicio = posicion
            columna_inicio = columna

            while posicion < len(codigo) and codigo[posicion].isdigit():
                posicion += 1
                columna += 1

            tipo = "ENTERO"

            if posicion < len(codigo) and codigo[posicion] == ".":
                if posicion + 1 < len(codigo) and codigo[posicion + 1].isdigit():
                    tipo = "DECIMAL"
                    posicion += 1
                    columna += 1

                    while posicion < len(codigo) and codigo[posicion].isdigit():
                        posicion += 1
                        columna += 1

            valor = codigo[inicio:posicion]
            tokens.append(Token(tipo, valor, linea, columna_inicio))
            continue

        if caracter.isalpha() or caracter == "_":
            inicio = posicion
            columna_inicio = columna

            while posicion < len(codigo) and (
                codigo[posicion].isalnum() or codigo[posicion] == "_"
            ):
                posicion += 1
                columna += 1

            valor = codigo[inicio:posicion]
            tipo = PALABRAS_RESERVADAS.get(valor, "IDENTIFICADOR")

            tokens.append(Token(tipo, valor, linea, columna_inicio))
            continue

        operador_encontrado = None

        for longitud in (2, 1):
            posible = codigo[posicion:posicion + longitud]

            if posible in OPERADORES:
                operador_encontrado = posible
                break

        if operador_encontrado is not None:
            tokens.append(
                Token(
                    OPERADORES[operador_encontrado],
                    operador_encontrado,
                    linea,
                    columna
                )
            )
            posicion += len(operador_encontrado)
            columna += len(operador_encontrado)
            continue

        raise ErrorLexico(
            f"Error léxico: carácter no reconocido '{caracter}'",
            linea,
            columna
        )

    tokens.append(Token("EOF", "", linea, columna))

    return tokens
