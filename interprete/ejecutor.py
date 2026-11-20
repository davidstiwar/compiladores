
import math

from semantico.tabla_simbolos import TablaSimbolos
from errores import ErrorEjecucion


class Ejecutor:
    def __init__(self, tabla=None):
        self.tabla = tabla if tabla is not None else TablaSimbolos()
        self.inventario = []

    def error(self, mensaje, nodo):
        raise ErrorEjecucion(
            mensaje,
            getattr(nodo, "linea", 1),
            getattr(nodo, "columna", 1)
        )

    def ejecutar(self, programa):
        for instruccion in programa.instrucciones:
            self.ejecutar_instruccion(instruccion)

        return self.tabla

    def ejecutar_instruccion(self, instruccion):
        tipo = instruccion.__class__.__name__

        if tipo == "Declaracion":
            valor = None

            if instruccion.valor is not None:
                valor = self.evaluar(instruccion.valor)

            if instruccion.tipo == "float" and type(valor) is int:
                valor = float(valor)

            if self.tabla.existe(instruccion.nombre):
                self.tabla.asignar(
                    instruccion.nombre, valor, valor is not None
                )
            else:
                self.tabla.declarar(
                    instruccion.nombre,
                    instruccion.tipo,
                    valor,
                    linea=instruccion.linea,
                    columna=instruccion.columna
                )

        elif tipo == "Asignacion":
            tipo_variable = self.tabla.obtener_tipo(instruccion.nombre)
            valor = self.evaluar(instruccion.valor)
            if instruccion.operador != "=":
                valor_actual = self.tabla.obtener(instruccion.nombre)
                operador = instruccion.operador[0]
                valor = self.aplicar_operador(
                    operador, valor_actual, valor, instruccion
                )
            if tipo_variable == "float" and type(valor) is int:
                valor = float(valor)
            self.tabla.asignar(instruccion.nombre, valor)

        elif tipo == "Mostrar":
            print(self.evaluar(instruccion.expresion))

        elif tipo == "Leer":
            entrada = input("Ingrese un valor: ")
            tipo_variable = self.tabla.obtener_tipo(instruccion.nombre)

            if tipo_variable == "int":
                try:
                    valor = int(entrada)
                except ValueError:
                    self.error("Se esperaba un número entero", instruccion)
                if valor < 0:
                    self.error("No se admiten números negativos", instruccion)
            elif tipo_variable == "float":
                try:
                    valor = float(entrada)
                except ValueError:
                    self.error("Se esperaba un número decimal", instruccion)
                if not math.isfinite(valor):
                    self.error(
                        "Se esperaba un número decimal finito", instruccion
                    )
                if valor < 0:
                    self.error("No se admiten números negativos", instruccion)
            elif tipo_variable == "bool":
                valores_booleanos = {
                    "verdadero": True,
                    "falso": False,
                }
                valor = valores_booleanos.get(entrada.strip().lower())
                if valor is None:
                    self.error(
                        "Se esperaba 'verdadero' o 'falso'", instruccion
                    )
            else:
                valor = entrada

            self.tabla.asignar(instruccion.nombre, valor)

        elif tipo == "Condicion":
            resultado = self.evaluar(instruccion.condicion)

            if not isinstance(resultado, bool):
                self.error(
                    "La condición debe ser verdadera o falsa", instruccion
                )

            if resultado:
                for elemento in instruccion.instrucciones:
                    self.ejecutar_instruccion(elemento)
            else:
                for elemento in instruccion.sino:
                    self.ejecutar_instruccion(elemento)

        elif tipo == "Repeticion":
            veces = self.evaluar(instruccion.veces)

            if type(veces) != int or veces < 0:
                self.error(
                    "La repetición necesita un entero no negativo",
                    instruccion.veces
                )

            for _ in range(veces):
                for elemento in instruccion.instrucciones:
                    self.ejecutar_instruccion(elemento)

        elif tipo == "Producto":
            self.registrar_producto(instruccion)

        elif tipo == "Entrada":
            self.mover_existencias(instruccion, "entrada")

        elif tipo == "Salida":
            self.mover_existencias(instruccion, "salida")

        elif tipo == "Consultar":
            self.consultar(instruccion.producto)

        elif tipo == "Eliminar":
            self.eliminar(instruccion.producto)

    def evaluar(self, expresion):
        tipo = expresion.__class__.__name__

        if tipo == "Literal":
            return expresion.valor

        if tipo == "Variable":
            return self.tabla.obtener(expresion.nombre)

        if tipo == "OperacionUnaria":
            valor = self.evaluar(expresion.operando)
            if type(valor) is not bool:
                self.error(
                    "El operador ! necesita un valor verdadero o falso",
                    expresion
                )
            return not valor

        if tipo == "Operacion":
            operador = expresion.operador

            izquierda = self.evaluar(expresion.izquierda)
            if operador == "&&":
                if type(izquierda) is not bool:
                    self.error(
                        "El operador && necesita valores verdaderos o falsos",
                        expresion
                    )
                if not izquierda:
                    return False
            elif operador == "||":
                if type(izquierda) is not bool:
                    self.error(
                        "El operador || necesita valores verdaderos o falsos",
                        expresion
                    )
                if izquierda:
                    return True

            derecha = self.evaluar(expresion.derecha)
            return self.aplicar_operador(
                operador, izquierda, derecha, expresion
            )

        return None

    def aplicar_operador(self, operador, izquierda, derecha, nodo=None):
        if operador == "+":
            return self.validar_numero(izquierda + derecha, nodo)
        if operador == "-":
            return self.validar_numero(izquierda - derecha, nodo)
        if operador == "*":
            return self.validar_numero(izquierda * derecha, nodo)
        if operador == "/":
            if derecha == 0:
                self.error("No se puede dividir entre cero", nodo)
            return self.validar_numero(izquierda / derecha, nodo)
        if operador == "==":
            return izquierda == derecha
        if operador == "!=":
            return izquierda != derecha
        if operador == ">":
            return izquierda > derecha
        if operador == "<":
            return izquierda < derecha
        if operador == ">=":
            return izquierda >= derecha
        if operador == "<=":
            return izquierda <= derecha
        if operador in ("&&", "||"):
            if type(izquierda) is not bool or type(derecha) is not bool:
                self.error(
                    f"El operador {operador} necesita valores verdaderos o falsos",
                    nodo
                )
            if operador == "&&":
                return izquierda and derecha
            return izquierda or derecha

        self.error(f"Operador no válido: {operador}", nodo)

    def validar_numero(self, valor, nodo):
        if type(valor) in (int, float) and valor < 0:
            self.error("No se admiten números negativos", nodo)
        return valor

    def registrar_producto(self, instruccion):
        codigo = self.evaluar(instruccion.codigo)
        nombre = self.evaluar(instruccion.nombre)
        cantidad = self.evaluar(instruccion.cantidad)
        precio = self.evaluar(instruccion.precio)

        if type(codigo) != int:
            self.error("El código debe ser entero", instruccion.codigo)

        if any(p["codigo"] == codigo for p in self.inventario):
            self.error(
                f"El código {codigo} ya está registrado", instruccion
            )

        if type(nombre) != str:
            self.error("El nombre debe ser texto", instruccion.nombre)

        if type(cantidad) != int or cantidad <= 0:
            self.error(
                "La cantidad inicial debe ser un entero positivo",
                instruccion.cantidad
            )

        if type(precio) not in (int, float) or precio <= 0:
            self.error(
                "El precio debe ser un número positivo", instruccion.precio
            )

        self.inventario.append({
            "codigo": codigo,
            "nombre": nombre,
            "cantidad": cantidad,
            "precio": float(precio)
        })

        print(f"Producto registrado: {nombre}")

    def buscar_productos(self, identificador):
        if type(identificador) == int:
            return [
                p for p in self.inventario
                if p["codigo"] == identificador
            ]

        if type(identificador) == str:
            return [
                p for p in self.inventario
                if p["nombre"].lower() == identificador.lower()
            ]

        return []

    def imprimir_producto(self, producto):
        valor = producto["cantidad"] * producto["precio"]
        print(
            f"Código: {producto['codigo']} | "
            f"Nombre: {producto['nombre']} | "
            f"Cantidad: {producto['cantidad']} | "
            f"Precio: {producto['precio']:.2f} | "
            f"Valor: {valor:.2f}"
        )

    def mover_existencias(self, instruccion, operacion):
        identificador = self.evaluar(instruccion.producto)
        cantidad = self.evaluar(instruccion.cantidad)

        if type(cantidad) != int or cantidad <= 0:
            self.error(
                "La cantidad debe ser un entero positivo", instruccion.cantidad
            )

        productos = self.buscar_productos(identificador)

        if not productos:
            print("No se encontró el producto. El inventario sigue igual.")
            return

        if len(productos) > 1:
            print("Hay varios productos con ese nombre. No se modificó ninguno.")
            return

        producto = productos[0]

        if operacion == "entrada":
            producto["cantidad"] += cantidad
            print(f"Entrada registrada: {producto['nombre']}")

        else:
            if cantidad > producto["cantidad"]:
                self.error(
                    "No puedes retirar más unidades de las existentes",
                    instruccion
                )

            producto["cantidad"] -= cantidad
            print(f"Salida registrada: {producto['nombre']}")

    def consultar(self, identificador):
        if identificador == "todos":
            if not self.inventario:
                print("El inventario está vacío.")
                return

            for producto in self.inventario:
                self.imprimir_producto(producto)

            return

        if identificador == "valor":
            registros = len(self.inventario)
            total = sum(
                p["cantidad"] * p["precio"]
                for p in self.inventario
            )

            print(f"Registros: {registros}")
            print(f"Valor total: {total:.2f}")
            return

        valor = self.evaluar(identificador)
        productos = self.buscar_productos(valor)

        if not productos:
            print("No se encontró el producto.")
            return

        for producto in productos:
            self.imprimir_producto(producto)

    def eliminar(self, expresion):
        codigo = self.evaluar(expresion)

        if type(codigo) != int:
            self.error(
                "Para eliminar debes indicar el código entero", expresion
            )

        for producto in self.inventario:
            if producto["codigo"] == codigo:
                self.inventario.remove(producto)
                print(f"Producto {codigo} eliminado.")
                return

        print(f"No se encontró el producto con código {codigo}.")


def ejecutar_programa(programa, tabla=None):
    if tabla is not None:
        tabla.reiniciar_valores()
    ejecutor = Ejecutor(tabla)
    return ejecutor.ejecutar(programa)
