"""Traduce el árbol del lenguaje Inventario de tienda a código Python."""

from sintactico.nodos import (
    Asignacion,
    Condicion,
    Consultar,
    Declaracion,
    Eliminar,
    Entrada,
    Literal,
    Leer,
    Mostrar,
    Operacion,
    OperacionUnaria,
    Producto,
    Repeticion,
    Salida,
    Variable,
)


CODIGO_BASE = '''import math

__variables = {}
__inventario = []


def __error(mensaje, linea, columna):
    raise ValueError(
        f"Error de ejecución: {mensaje} "
        f"(línea {linea}, columna {columna})"
    )


def __a_float(valor):
    if type(valor) is int:
        return float(valor)
    return valor


def __calcular(operador, izquierda, derecha, linea, columna):
    if operador == "+":
        resultado = izquierda + derecha
    elif operador == "-":
        resultado = izquierda - derecha
    elif operador == "*":
        resultado = izquierda * derecha
    elif operador == "/":
        if derecha == 0:
            __error("No se puede dividir entre cero", linea, columna)
        resultado = izquierda / derecha
    else:
        __error(f"Operador no válido: {operador}", linea, columna)

    if type(resultado) in (int, float) and resultado < 0:
        __error("No se admiten números negativos", linea, columna)
    return resultado


def __leer(tipo, linea, columna):
    entrada = input("Ingrese un valor: ")

    if tipo == "int":
        try:
            valor = int(entrada)
        except ValueError:
            __error("Se esperaba un número entero", linea, columna)
        if valor < 0:
            __error("No se admiten números negativos", linea, columna)
        return valor

    if tipo == "float":
        try:
            valor = float(entrada)
        except ValueError:
            __error("Se esperaba un número decimal", linea, columna)
        if not math.isfinite(valor):
            __error("Se esperaba un número decimal finito", linea, columna)
        if valor < 0:
            __error("No se admiten números negativos", linea, columna)
        return valor

    if tipo == "bool":
        valores = {"verdadero": True, "falso": False}
        valor = valores.get(entrada.strip().lower())
        if valor is None:
            __error("Se esperaba 'verdadero' o 'falso'", linea, columna)
        return valor

    return entrada


def __buscar_productos(identificador):
    if type(identificador) is int:
        return [
            producto for producto in __inventario
            if producto["codigo"] == identificador
        ]
    if type(identificador) is str:
        return [
            producto for producto in __inventario
            if producto["nombre"].lower() == identificador.lower()
        ]
    return []


def __imprimir_producto(producto):
    valor = producto["cantidad"] * producto["precio"]
    print(
        f"Código: {producto['codigo']} | "
        f"Nombre: {producto['nombre']} | "
        f"Cantidad: {producto['cantidad']} | "
        f"Precio: {producto['precio']:.2f} | "
        f"Valor: {valor:.2f}"
    )


def __registrar_producto(codigo, nombre, cantidad, precio, linea, columna):
    if type(codigo) is not int:
        __error("El código debe ser entero", linea, columna)
    if any(producto["codigo"] == codigo for producto in __inventario):
        __error(f"El código {codigo} ya está registrado", linea, columna)
    if type(nombre) is not str:
        __error("El nombre debe ser texto", linea, columna)
    if type(cantidad) is not int or cantidad <= 0:
        __error(
            "La cantidad inicial debe ser un entero positivo", linea, columna
        )
    if type(precio) not in (int, float) or precio <= 0:
        __error("El precio debe ser un número positivo", linea, columna)

    __inventario.append({
        "codigo": codigo,
        "nombre": nombre,
        "cantidad": cantidad,
        "precio": float(precio),
    })
    print(f"Producto registrado: {nombre}")


def __mover_existencias(identificador, cantidad, operacion, linea, columna):
    if type(cantidad) is not int or cantidad <= 0:
        __error("La cantidad debe ser un entero positivo", linea, columna)

    productos = __buscar_productos(identificador)
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
        return

    if cantidad > producto["cantidad"]:
        __error(
            "No puedes retirar más unidades de las existentes",
            linea,
            columna,
        )
    producto["cantidad"] -= cantidad
    print(f"Salida registrada: {producto['nombre']}")


def __consultar_producto(identificador):
    productos = __buscar_productos(identificador)
    if not productos:
        print("No se encontró el producto.")
        return
    for producto in productos:
        __imprimir_producto(producto)


def __consultar_todos():
    if not __inventario:
        print("El inventario está vacío.")
        return
    for producto in __inventario:
        __imprimir_producto(producto)


def __consultar_valor():
    total = sum(
        producto["cantidad"] * producto["precio"]
        for producto in __inventario
    )
    print(f"Registros: {len(__inventario)}")
    print(f"Valor total: {total:.2f}")


def __eliminar_producto(codigo, linea, columna):
    if type(codigo) is not int:
        __error("Para eliminar debes indicar el código entero", linea, columna)

    for producto in __inventario:
        if producto["codigo"] == codigo:
            __inventario.remove(producto)
            print(f"Producto {codigo} eliminado.")
            return
    print(f"No se encontró el producto con código {codigo}.")
'''


class GeneradorPython:
    def __init__(self, programa):
        self.programa = programa
        self.tipos = self._recolectar_tipos(programa.instrucciones)

    def generar(self):
        lineas = [
            "# Código Python generado por Inventario de tienda.",
            CODIGO_BASE.rstrip(),
            "",
        ]
        self._emitir_bloque(self.programa.instrucciones, lineas, 0)
        return "\n".join(lineas) + "\n"

    def _recolectar_tipos(self, instrucciones):
        tipos = {}
        for instruccion in instrucciones:
            if isinstance(instruccion, Declaracion):
                tipos[instruccion.nombre] = instruccion.tipo
            elif isinstance(instruccion, Condicion):
                tipos.update(self._recolectar_tipos(instruccion.instrucciones))
                tipos.update(self._recolectar_tipos(instruccion.sino))
            elif isinstance(instruccion, Repeticion):
                tipos.update(self._recolectar_tipos(instruccion.instrucciones))
        return tipos

    def _emitir_bloque(self, instrucciones, lineas, nivel):
        if not instrucciones:
            lineas.append("    " * nivel + "pass")
            return
        for instruccion in instrucciones:
            self._emitir_instruccion(instruccion, lineas, nivel)

    def _emitir_instruccion(self, instruccion, lineas, nivel):
        sangria = "    " * nivel
        if isinstance(instruccion, Declaracion):
            valor = (
                "None"
                if instruccion.valor is None
                else self._expresion(instruccion.valor)
            )
            if instruccion.tipo == "float":
                valor = f"__a_float({valor})"
            linea = f"__variables[{instruccion.nombre!r}] = {valor}"
        elif isinstance(instruccion, Asignacion):
            nombre = f"__variables[{instruccion.nombre!r}]"
            valor = self._expresion(instruccion.valor)
            if instruccion.operador == "=":
                if self.tipos.get(instruccion.nombre) == "float":
                    valor = f"__a_float({valor})"
            else:
                operador = instruccion.operador[0]
                valor = (
                    f"__calcular({operador!r}, {nombre}, {valor}, "
                    f"{instruccion.linea}, {instruccion.columna})"
                )
                if self.tipos.get(instruccion.nombre) == "float":
                    valor = f"__a_float({valor})"
            linea = f"{nombre} = {valor}"
        elif isinstance(instruccion, Mostrar):
            linea = f"print({self._expresion(instruccion.expresion)})"
        elif isinstance(instruccion, Leer):
            nombre = f"__variables[{instruccion.nombre!r}]"
            tipo = self.tipos[instruccion.nombre]
            valor = (
                f"__leer({tipo!r}, {instruccion.linea}, "
                f"{instruccion.columna})"
            )
            if tipo == "float":
                valor = f"__a_float({valor})"
            linea = f"{nombre} = {valor}"
        elif isinstance(instruccion, Condicion):
            lineas.append(
                f"{sangria}if {self._expresion(instruccion.condicion)}:"
            )
            self._emitir_bloque(instruccion.instrucciones, lineas, nivel + 1)
            if instruccion.sino:
                lineas.append(f"{sangria}else:")
                self._emitir_bloque(instruccion.sino, lineas, nivel + 1)
            return
        elif isinstance(instruccion, Repeticion):
            lineas.append(
                f"{sangria}for _ in range({self._expresion(instruccion.veces)}):"
            )
            self._emitir_bloque(instruccion.instrucciones, lineas, nivel + 1)
            return
        elif isinstance(instruccion, Producto):
            argumentos = ", ".join(
                self._expresion(valor)
                for valor in (
                    instruccion.codigo,
                    instruccion.nombre,
                    instruccion.cantidad,
                    instruccion.precio,
                )
            )
            linea = (
                f"__registrar_producto({argumentos}, "
                f"{instruccion.linea}, {instruccion.columna})"
            )
        elif isinstance(instruccion, (Entrada, Salida)):
            operacion = "entrada" if isinstance(instruccion, Entrada) else "salida"
            linea = (
                f"__mover_existencias("
                f"{self._expresion(instruccion.producto)}, "
                f"{self._expresion(instruccion.cantidad)}, {operacion!r}, "
                f"{instruccion.linea}, {instruccion.columna})"
            )
        elif isinstance(instruccion, Consultar):
            if instruccion.producto == "todos":
                linea = "__consultar_todos()"
            elif instruccion.producto == "valor":
                linea = "__consultar_valor()"
            else:
                linea = (
                    f"__consultar_producto("
                    f"{self._expresion(instruccion.producto)})"
                )
        elif isinstance(instruccion, Eliminar):
            linea = (
                f"__eliminar_producto("
                f"{self._expresion(instruccion.producto)}, "
                f"{instruccion.linea}, {instruccion.columna})"
            )
        else:
            raise TypeError(
                f"No se puede traducir la instrucción "
                f"{type(instruccion).__name__}"
            )
        lineas.append(sangria + linea)

    def _expresion(self, expresion):
        if isinstance(expresion, Literal):
            return repr(expresion.valor)
        if isinstance(expresion, Variable):
            return f"__variables[{expresion.nombre!r}]"
        if isinstance(expresion, OperacionUnaria):
            return f"(not {self._expresion(expresion.operando)})"
        if isinstance(expresion, Operacion):
            izquierda = self._expresion(expresion.izquierda)
            derecha = self._expresion(expresion.derecha)
            operador = expresion.operador
            if operador in ("+", "-", "*", "/"):
                return (
                    f"__calcular({operador!r}, {izquierda}, {derecha}, "
                    f"{expresion.linea}, {expresion.columna})"
                )
            operadores = {"&&": "and", "||": "or"}
            operador_python = operadores.get(operador, operador)
            return f"({izquierda} {operador_python} {derecha})"
        raise TypeError(
            f"No se puede traducir la expresión {type(expresion).__name__}"
        )


def generar_python(programa):
    return GeneradorPython(programa).generar()
