
from .tabla_simbolos import TablaSimbolos
from errores import ErrorSemantico


class AnalizadorSemantico:
    def __init__(self):
        self.tabla = TablaSimbolos()

    def analizar(self, programa):
        for instruccion in programa.instrucciones:
            self.analizar_instruccion(instruccion)

        return self.tabla

    def analizar_instruccion(self, instruccion):

        if instruccion.__class__.__name__ == "Declaracion":
            nombre = instruccion.nombre
            tipo = instruccion.tipo

            if self.tabla.existe(nombre):
                raise ErrorSemantico(
                    f"La variable '{nombre}' ya fue declarada",
                    1, 1
                )

            valor = None

            if instruccion.valor is not None:
                valor = self.evaluar_expresion(instruccion.valor)
                self.validar_tipo(tipo, valor)

            self.tabla.declarar(nombre, tipo, valor)

        elif instruccion.__class__.__name__ == "Asignacion":
            nombre = instruccion.nombre

            if not self.tabla.existe(nombre):
                raise ErrorSemantico(
                    f"La variable '{nombre}' no está declarada",
                    1, 1
                )

            valor = self.evaluar_expresion(instruccion.valor)
            tipo = self.tabla.obtener_tipo(nombre)

            self.validar_tipo(tipo, valor)
            self.tabla.asignar(nombre, valor)

        elif instruccion.__class__.__name__ == "Mostrar":
            self.evaluar_expresion(instruccion.expresion)

        elif instruccion.__class__.__name__ == "Leer":
            if not self.tabla.existe(instruccion.nombre):
                raise ErrorSemantico(
                    f"La variable '{instruccion.nombre}' no está declarada",
                    1, 1
                )

        elif instruccion.__class__.__name__ == "Condicion":
            self.evaluar_expresion(instruccion.condicion)

            for elemento in instruccion.instrucciones:
                self.analizar_instruccion(elemento)

            for elemento in instruccion.sino:
                self.analizar_instruccion(elemento)

        elif instruccion.__class__.__name__ == "Repeticion":
            self.evaluar_expresion(instruccion.veces)

            for elemento in instruccion.instrucciones:
                self.analizar_instruccion(elemento)

    def evaluar_expresion(self, expresion):

        if expresion.__class__.__name__ == "Literal":
            return expresion.valor

        if expresion.__class__.__name__ == "Variable":
            nombre = expresion.nombre

            if not self.tabla.existe(nombre):
                raise ErrorSemantico(
                    f"La variable '{nombre}' no está declarada",
                    1, 1
                )

            return self.tabla.obtener(nombre)

        if expresion.__class__.__name__ == "Operacion":
            izquierda = self.evaluar_expresion(expresion.izquierda)
            derecha = self.evaluar_expresion(expresion.derecha)
            operador = expresion.operador

            if operador == "+":
                return izquierda + derecha
            elif operador == "-":
                return izquierda - derecha
            elif operador == "*":
                return izquierda * derecha
            elif operador == "/":
                if derecha == 0:
                    raise ErrorSemantico(
                        "No se puede dividir entre cero", 1, 1
                    )
                return izquierda / derecha
            elif operador == "==":
                return izquierda == derecha
            elif operador == "!=":
                return izquierda != derecha
            elif operador == ">":
                return izquierda > derecha
            elif operador == "<":
                return izquierda < derecha
            elif operador == ">=":
                return izquierda >= derecha
            elif operador == "<=":
                return izquierda <= derecha

        return None

    def validar_tipo(self, tipo, valor):
        tipos = {
            "int": int,
            "float": (int, float),
            "str": str,
            "bool": bool
        }

        if valor is None:
            return

        tipo_python = tipos.get(tipo)

        if tipo_python is None:
            raise ErrorSemantico(
                f"Tipo de dato no reconocido: {tipo}", 1, 1
            )

        if isinstance(valor, bool) and tipo != "bool":
            raise ErrorSemantico(
                f"El valor no corresponde al tipo {tipo}", 1, 1
            )

        if not isinstance(valor, tipo_python):
            raise ErrorSemantico(
                f"El valor no corresponde al tipo {tipo}", 1, 1
            )


def analizar_semantica(programa):
    analizador = AnalizadorSemantico()
    return analizador.analizar(programa)
