from .token import Token
from errores import ErrorLexico


PALABRAS_RESERVADAS = {
    "inicio": "INICIO",
    "fin": "FIN",
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
    """Separa el código en tokens y guarda la ubicación de cada uno."""
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

            # Si hay una barra invertida, se avanza también sobre el carácter escapado.
            while posicion < len(codigo) and codigo[posicion] != comilla:
                if codigo[posicion] == "\n":
                    raise ErrorLexico(
                        "Texto sin cerrar",
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
                    "Texto sin cerrar",
                    linea,
                    columna_inicio
                )

            posicion += 1
            columna += 1
            # Se conservan las comillas; el parser las quita al crear el valor de texto.
            tokens.append(
                Token("CADENA", codigo[inicio:posicion], linea, columna_inicio)
            )
            continue

        if caracter.isdigit():
            inicio = posicion
            columna_inicio = columna

            while posicion < len(codigo) and codigo[posicion].isdigit():
                posicion += 1
                columna += 1

            tipo = "ENTERO"
            # Solo se considera decimal si después del punto viene al menos un dígito.
            if (
                posicion + 1 < len(codigo)
                and codigo[posicion] == "."
                and codigo[posicion + 1].isdigit()
            ):
                tipo = "DECIMAL"
                posicion += 1
                columna += 1
                while posicion < len(codigo) and codigo[posicion].isdigit():
                    posicion += 1
                    columna += 1

            tokens.append(
                Token(tipo, codigo[inicio:posicion], linea, columna_inicio)
            )
            continue

        # Un signo menos después de un valor es resta; en otro caso, puede ser un negativo.
        if caracter == "-":
            siguiente = posicion + 1
            while siguiente < len(codigo) and codigo[siguiente] in " \t\r":
                siguiente += 1

            if siguiente < len(codigo) and codigo[siguiente].isdigit():
                ultimo_token = tokens[-1] if tokens else None
                tipos_que_terminan_expresion = {
                    "ENTERO", "DECIMAL", "CADENA", "IDENTIFICADOR",
                    "VERDADERO", "FALSO", "NULL", "PARENTESIS_CIERRA",
                }

                if (
                    ultimo_token is None
                    or ultimo_token.tipo not in tipos_que_terminan_expresion
                ):
                    raise ErrorLexico(
                        "No se admiten números negativos",
                        linea,
                        columna
                    )

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

        # Se prueba primero el símbolo de dos caracteres, como >=, para no partirlo.
        operador = codigo[posicion:posicion + 2]
        if operador not in OPERADORES:
            operador = caracter

        if operador in OPERADORES:
            tokens.append(Token(OPERADORES[operador], operador, linea, columna))
            posicion += len(operador)
            columna += len(operador)
            continue

        raise ErrorLexico(
            f"Carácter no reconocido {caracter!r}",
            linea,
            columna
        )

    tokens.append(Token("EOF", "", linea, columna))
    return tokens
