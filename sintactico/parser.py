from .nodos import (
    Programa, Declaracion, Asignacion, Mostrar, Leer,
    Operacion, OperacionUnaria, Literal, Variable, Condicion,
    Repeticion, Producto, Entrada, Salida, Consultar, Eliminar
)
from errores import ErrorSintactico


class Parser:
    TIPOS_DECLARACION = {"INT", "FLOAT", "STR", "BOOL"}
    OPERADORES_ASIGNACION = {
        "ASIGNACION": "=",
        "SUMA_ASIGNACION": "+=",
        "RESTA_ASIGNACION": "-=",
        "MULTIPLICACION_ASIGNACION": "*=",
        "DIVISION_ASIGNACION": "/=",
    }

    def __init__(self, tokens):
        self.tokens = tokens
        self.posicion = 0

    def actual(self):
        while (
            self.posicion < len(self.tokens) - 1
            and self.tokens[self.posicion].tipo == "NUEVA_LINEA"
        ):
            self.posicion += 1

        return self.tokens[self.posicion]

    def avanzar(self):
        token = self.actual()

        if token.tipo != "EOF":
            self.posicion += 1

        return token

    def esperar(self, tipo):
        token = self.actual()

        if token.tipo != tipo:
            encontrado = token.valor or token.tipo
            raise ErrorSintactico(
                f"Se esperaba {tipo}, pero se encontró {encontrado}",
                token.linea,
                token.columna
            )

        return self.avanzar()

    def analizar(self):
        inicio = self.esperar("INICIO")
        instrucciones = self.bloque()
        self.esperar("FIN")
        self.esperar("EOF")
        return Programa(instrucciones, inicio.linea, inicio.columna)

    def bloque(self):
        self.esperar("LLAVE_ABRE")
        instrucciones = []

        while self.actual().tipo not in ("LLAVE_CIERRA", "EOF"):
            instrucciones.append(self.instruccion())

        self.esperar("LLAVE_CIERRA")
        return instrucciones

    def instruccion(self):
        tipo = self.actual().tipo

        if tipo in self.TIPOS_DECLARACION:
            return self.declaracion()
        if tipo == "IDENTIFICADOR":
            return self.asignacion()
        if tipo == "MOSTRAR":
            return self.mostrar()
        if tipo == "LEER":
            return self.leer()
        if tipo == "SI":
            return self.condicion()
        if tipo == "REPETIR":
            return self.repeticion()
        if tipo == "PRODUCTO":
            return self.registrar_producto()
        if tipo == "ENTRADA":
            return self.registrar_entrada()
        if tipo == "SALIDA":
            return self.registrar_salida()
        if tipo == "CONSULTAR":
            return self.consultar_producto()
        if tipo == "ELIMINAR":
            return self.eliminar_producto()

        token = self.actual()
        raise ErrorSintactico(
            f"Instrucción no válida: {token.valor or token.tipo}",
            token.linea,
            token.columna
        )

    def declaracion(self):
        token_tipo = self.avanzar()
        nombre = self.esperar("IDENTIFICADOR").valor
        valor = None

        if self.actual().tipo == "ASIGNACION":
            self.avanzar()
            valor = self.expresion()

        return Declaracion(
            token_tipo.valor, nombre, valor,
            token_tipo.linea, token_tipo.columna
        )

    def asignacion(self):
        token_nombre = self.avanzar()
        nombre = token_nombre.valor
        token_operador = self.actual()
        operador = self.OPERADORES_ASIGNACION.get(token_operador.tipo)

        if operador is None:
            raise ErrorSintactico(
                f"Se esperaba un operador de asignación, "
                f"pero se encontró {token_operador.valor or token_operador.tipo}",
                token_operador.linea,
                token_operador.columna
            )

        self.avanzar()
        valor = self.expresion()
        return Asignacion(
            nombre, valor, operador,
            token_nombre.linea, token_nombre.columna
        )

    def mostrar(self):
        token = self.esperar("MOSTRAR")
        self.esperar("PARENTESIS_ABRE")
        expresion = self.expresion()
        self.esperar("PARENTESIS_CIERRA")
        return Mostrar(expresion, token.linea, token.columna)

    def leer(self):
        token = self.esperar("LEER")
        self.esperar("PARENTESIS_ABRE")
        nombre = self.esperar("IDENTIFICADOR").valor
        self.esperar("PARENTESIS_CIERRA")
        return Leer(nombre, token.linea, token.columna)

    def condicion(self):
        token = self.esperar("SI")
        condicion = self.expresion()
        instrucciones = self.bloque()
        sino = []

        if self.actual().tipo == "SINO":
            self.avanzar()
            sino = self.bloque()

        return Condicion(
            condicion, instrucciones, sino, token.linea, token.columna
        )

    def repeticion(self):
        token = self.esperar("REPETIR")
        veces = self.expresion()
        self.esperar("VECES")
        instrucciones = self.bloque()
        return Repeticion(
            veces, instrucciones, token.linea, token.columna
        )

    def registrar_producto(self):
        token = self.esperar("PRODUCTO")
        self.esperar("PARENTESIS_ABRE")
        codigo = self.expresion()
        self.esperar("COMA")
        nombre = self.expresion()
        self.esperar("COMA")
        cantidad = self.expresion()
        self.esperar("COMA")
        precio = self.expresion()
        self.esperar("PARENTESIS_CIERRA")
        return Producto(
            codigo, nombre, cantidad, precio, token.linea, token.columna
        )

    def registrar_entrada(self):
        token = self.esperar("ENTRADA")
        self.esperar("PARENTESIS_ABRE")
        producto = self.expresion()
        self.esperar("COMA")
        cantidad = self.expresion()
        self.esperar("PARENTESIS_CIERRA")
        return Entrada(producto, cantidad, token.linea, token.columna)

    def registrar_salida(self):
        token = self.esperar("SALIDA")
        self.esperar("PARENTESIS_ABRE")
        producto = self.expresion()
        self.esperar("COMA")
        cantidad = self.expresion()
        self.esperar("PARENTESIS_CIERRA")
        return Salida(producto, cantidad, token.linea, token.columna)

    def consultar_producto(self):
        token = self.esperar("CONSULTAR")

        if self.actual().tipo == "TODOS":
            self.avanzar()
            self.esperar("PARENTESIS_ABRE")
            self.esperar("PARENTESIS_CIERRA")
            return Consultar("todos", token.linea, token.columna)

        if self.actual().tipo == "VALOR":
            self.avanzar()
            self.esperar("PARENTESIS_ABRE")
            self.esperar("PARENTESIS_CIERRA")
            return Consultar("valor", token.linea, token.columna)

        self.esperar("PARENTESIS_ABRE")
        producto = self.expresion()
        self.esperar("PARENTESIS_CIERRA")
        return Consultar(producto, token.linea, token.columna)

    def eliminar_producto(self):
        token = self.esperar("ELIMINAR")
        self.esperar("PARENTESIS_ABRE")
        producto = self.expresion()
        self.esperar("PARENTESIS_CIERRA")
        return Eliminar(producto, token.linea, token.columna)

    def expresion(self):
        return self.expresion_o()

    def expresion_o(self):
        return self.operacion_en_cadena(self.expresion_y, ("OR",))

    def expresion_y(self):
        return self.operacion_en_cadena(self.igualdad, ("AND",))

    def igualdad(self):
        return self.operacion_en_cadena(
            self.comparacion, ("IGUAL_IGUAL", "DIFERENTE")
        )

    def comparacion(self):
        return self.operacion_en_cadena(
            self.suma, ("MAYOR", "MENOR", "MAYOR_IGUAL", "MENOR_IGUAL")
        )

    def suma(self):
        return self.operacion_en_cadena(self.producto, ("MAS", "MENOS"))

    def producto(self):
        return self.operacion_en_cadena(
            self.unario, ("MULTIPLICACION", "DIVISION")
        )

    def operacion_en_cadena(self, siguiente, operadores):
        izquierda = siguiente()

        while self.actual().tipo in operadores:
            token = self.avanzar()
            derecha = siguiente()
            izquierda = Operacion(
                izquierda, token.valor, derecha, token.linea, token.columna
            )

        return izquierda

    def unario(self):
        if self.actual().tipo == "NOT":
            token = self.avanzar()
            return OperacionUnaria(
                token.valor, self.unario(), token.linea, token.columna
            )

        return self.factor()

    def factor(self):
        token = self.actual()

        if token.tipo in ("ENTERO", "DECIMAL", "CADENA"):
            self.avanzar()

            if token.tipo == "ENTERO":
                valor = int(token.valor)
            elif token.tipo == "DECIMAL":
                valor = float(token.valor)
            else:
                valor = token.valor[1:-1]

            return Literal(valor, token.linea, token.columna)

        if token.tipo in ("VERDADERO", "FALSO"):
            self.avanzar()
            return Literal(
                token.tipo == "VERDADERO", token.linea, token.columna
            )

        if token.tipo == "NULL":
            self.avanzar()
            return Literal(None, token.linea, token.columna)

        if token.tipo == "IDENTIFICADOR":
            self.avanzar()
            return Variable(token.valor, token.linea, token.columna)

        if token.tipo == "PARENTESIS_ABRE":
            self.avanzar()
            expresion = self.expresion()
            self.esperar("PARENTESIS_CIERRA")
            return expresion

        raise ErrorSintactico(
            f"Expresión no válida: {token.valor or token.tipo}",
            token.linea,
            token.columna
        )


def analizar_sintaxis(tokens):
    parser = Parser(tokens)
    return parser.analizar()
