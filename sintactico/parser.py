
from .nodos import (
    Programa, Declaracion, Asignacion, Mostrar, Leer,
    Operacion, Literal, Variable, Condicion, Repeticion,
    Producto, Entrada, Salida, Consultar, Eliminar
)
from errores import ErrorSintactico


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.posicion = 0

    def actual(self):
        while self.tokens[self.posicion].tipo == "NUEVA_LINEA":
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
            raise ErrorSintactico(
                f"Se esperaba {tipo}, pero se encontró {token.valor}",
                token.linea,
                token.columna
            )

        return self.avanzar()

    def analizar(self):
        self.esperar("INICIO")
        instrucciones = self.bloque()
        self.esperar("EOF")
        return Programa(instrucciones)

    def bloque(self):
        self.esperar("LLAVE_ABRE")
        instrucciones = []

        while self.actual().tipo not in ("LLAVE_CIERRA", "EOF"):
            instrucciones.append(self.instruccion())

        self.esperar("LLAVE_CIERRA")
        return instrucciones

    def instruccion(self):
        tipo = self.actual().tipo

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

        raise ErrorSintactico(
            f"Instrucción no válida: {self.actual().valor}",
            self.actual().linea,
            self.actual().columna
        )

    def declaracion(self):
        tipo = self.avanzar().valor
        nombre = self.esperar("IDENTIFICADOR").valor
        valor = None

        if self.actual().tipo == "ASIGNACION":
            self.avanzar()
            valor = self.expresion()

        return Declaracion(tipo, nombre, valor)

    def asignacion(self):
        nombre = self.avanzar().valor
        self.esperar("ASIGNACION")
        valor = self.expresion()
        return Asignacion(nombre, valor)

    def condicion(self):
        self.esperar("SI")
        condicion = self.expresion()
        instrucciones = self.bloque()
        sino = []

        if self.actual().tipo == "SINO":
            self.avanzar()
            sino = self.bloque()

        return Condicion(condicion, instrucciones, sino)

    def repeticion(self):
        self.esperar("REPETIR")
        veces = self.expresion()
        self.esperar("VECES")
        instrucciones = self.bloque()
        return Repeticion(veces, instrucciones)

    
    def registrar_producto(self):
        self.esperar("PRODUCTO")
        self.esperar("PARENTESIS_ABRE")

        codigo = self.expresion()
        self.esperar("COMA")

        nombre = self.expresion()
        self.esperar("COMA")

        cantidad = self.expresion()
        self.esperar("COMA")

        precio = self.expresion()
        self.esperar("PARENTESIS_CIERRA")

        return Producto(codigo, nombre, cantidad, precio)

    def registrar_entrada(self):
        self.esperar("ENTRADA")
        self.esperar("PARENTESIS_ABRE")

        producto = self.expresion()
        self.esperar("COMA")

        cantidad = self.expresion()
        self.esperar("PARENTESIS_CIERRA")

        return Entrada(producto, cantidad)

    def registrar_salida(self):
        self.esperar("SALIDA")
        self.esperar("PARENTESIS_ABRE")

        producto = self.expresion()
        self.esperar("COMA")

        cantidad = self.expresion()
        self.esperar("PARENTESIS_CIERRA")

        return Salida(producto, cantidad)

    
    def consultar_producto(self):
        self.esperar("CONSULTAR")

        if self.actual().tipo == "TODOS":
            self.avanzar()
            self.esperar("PARENTESIS_ABRE")
            self.esperar("PARENTESIS_CIERRA")
            return Consultar("todos")

        if self.actual().tipo == "VALOR":
            self.avanzar()
            self.esperar("PARENTESIS_ABRE")
            self.esperar("PARENTESIS_CIERRA")
            return Consultar("valor")

        self.esperar("PARENTESIS_ABRE")
        producto = self.expresion()
        self.esperar("PARENTESIS_CIERRA")

        return Consultar(producto)


    def eliminar_producto(self):
        self.esperar("ELIMINAR")
        self.esperar("PARENTESIS_ABRE")

        producto = self.expresion()

        self.esperar("PARENTESIS_CIERRA")
        return Eliminar(producto)


    def expresion(self):
        izquierda = self.termino()

        while self.actual().tipo in (
            "MAS", "MENOS", "IGUAL_IGUAL", "DIFERENTE",
            "MAYOR", "MENOR", "MAYOR_IGUAL", "MENOR_IGUAL"
        ):
            operador = self.avanzar().valor
            derecha = self.termino()
            izquierda = Operacion(izquierda, operador, derecha)

        return izquierda

    def termino(self):
        izquierda = self.factor()

        while self.actual().tipo in (
            "MULTIPLICACION", "DIVISION"
        ):
            operador = self.avanzar().valor
            derecha = self.factor()
            izquierda = Operacion(izquierda, operador, derecha)

        return izquierda

    def factor(self):
        token = self.actual()

        if token.tipo in ("ENTERO", "DECIMAL", "CADENA"):
            self.avanzar()
            valor = token.valor

            if token.tipo == "ENTERO":
                valor = int(valor)
            elif token.tipo == "DECIMAL":
                valor = float(valor)
            else:
                valor = valor[1:-1]

            return Literal(valor)

        if token.tipo in ("VERDADERO", "FALSO"):
            self.avanzar()
            return Literal(token.tipo == "VERDADERO")

        if token.tipo == "IDENTIFICADOR":
            self.avanzar()
            return Variable(token.valor)

        if token.tipo == "PARENTESIS_ABRE":
            self.avanzar()
            expresion = self.expresion()
            self.esperar("PARENTESIS_CIERRA")
            return expresion

        raise ErrorSintactico(
            f"Expresión no válida: {token.valor}",
            token.linea,
            token.columna
        )


def analizar_sintaxis(tokens):
    parser = Parser(tokens)
    return parser.analizar()
