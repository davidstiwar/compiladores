
from semantico.tabla_simbolos import TablaSimbolos
from errores import ErrorEjecucion


class Ejecutor:
    def __init__(self):
        self.tabla = TablaSimbolos()
        self.inventario = []

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

            self.tabla.declarar(
                instruccion.nombre,
                instruccion.tipo,
                valor
            )

        elif tipo == "Asignacion":
            valor = self.evaluar(instruccion.valor)
            self.tabla.asignar(instruccion.nombre, valor)

        elif tipo == "Mostrar":
            print(self.evaluar(instruccion.expresion))

        elif tipo == "Leer":
            valor = input("Ingrese un valor: ")
            self.tabla.asignar(instruccion.nombre, valor)

        elif tipo == "Condicion":
            resultado = self.evaluar(instruccion.condicion)

            if not isinstance(resultado, bool):
                raise ErrorEjecucion(
                    "La condición debe ser verdadera o falsa", 1, 1
                )

            bloque = (
                instruccion.instrucciones
                if resultado else instruccion.sino
            )

            for elemento in bloque:
                self.ejecutar_instruccion(elemento)

        elif tipo == "Repeticion":
            veces = self.evaluar(instruccion.veces)

            if type(veces) != int or veces < 0:
                raise ErrorEjecucion(
                    "La repetición necesita un entero no negativo", 1, 1
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

        if tipo == "Operacion":
            izquierda = self.evaluar(expresion.izquierda)
            derecha = self.evaluar(expresion.derecha)
            operador = expresion.operador

            if operador == "+":
                if type(izquierda) == str and type(derecha) == str:
                    return izquierda + derecha
                return izquierda + derecha

            elif operador == "-":
                return izquierda - derecha

            elif operador == "*":
                return izquierda * derecha

            elif operador == "/":
                if derecha == 0:
                    raise ErrorEjecucion(
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

    def registrar_producto(self, instruccion):
        codigo = self.evaluar(instruccion.codigo)
        nombre = self.evaluar(instruccion.nombre)
        cantidad = self.evaluar(instruccion.cantidad)
        precio = self.evaluar(instruccion.precio)

        if type(codigo) != int:
            raise ErrorEjecucion("El código debe ser entero", 1, 1)

        if any(p["codigo"] == codigo for p in self.inventario):
            raise ErrorEjecucion(
                f"El código {codigo} ya está registrado", 1, 1
            )

        if type(nombre) != str:
            raise ErrorEjecucion("El nombre debe ser texto", 1, 1)

        if type(cantidad) != int or cantidad <= 0:
            raise ErrorEjecucion(
                "La cantidad inicial debe ser un entero positivo", 1, 1
            )

        if type(precio) not in (int, float) or precio <= 0:
            raise ErrorEjecucion(
                "El precio debe ser un número positivo", 1, 1
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

    def mover_existencias(self, instruccion, operacion):
        identificador = self.evaluar(instruccion.producto)
        cantidad = self.evaluar(instruccion.cantidad)

        if type(cantidad) != int or cantidad <= 0:
            raise ErrorEjecucion(
                "La cantidad debe ser un entero positivo", 1, 1
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
                raise ErrorEjecucion(
                    "No puedes retirar más unidades de las existentes", 1, 1
                )

            producto["cantidad"] -= cantidad
            print(f"Salida registrada: {producto['nombre']}")

    def consultar(self, identificador):
        if identificador == "todos":
            if not self.inventario:
                print("El inventario está vacío.")
                return

            for producto in self.inventario:
                valor = producto["cantidad"] * producto["precio"]
                print(
                    f"Código: {producto['codigo']} | "
                    f"Nombre: {producto['nombre']} | "
                    f"Cantidad: {producto['cantidad']} | "
                    f"Precio: {producto['precio']:.2f} | "
                    f"Valor: {valor:.2f}"
                )

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
            valor_total = producto["cantidad"] * producto["precio"]
            print(
                f"Código: {producto['codigo']} | "
                f"Nombre: {producto['nombre']} | "
                f"Cantidad: {producto['cantidad']} | "
                f"Precio: {producto['precio']:.2f} | "
                f"Valor: {valor_total:.2f}"
            )

    def eliminar(self, expresion):
        codigo = self.evaluar(expresion)

        if type(codigo) != int:
            raise ErrorEjecucion(
                "Para eliminar debes indicar el código entero", 1, 1
            )

        for producto in self.inventario:
            if producto["codigo"] == codigo:
                self.inventario.remove(producto)
                print(f"Producto {codigo} eliminado.")
                return

        print(f"No se encontró el producto con código {codigo}.")


def ejecutar_programa(programa):
    ejecutor = Ejecutor()
    return ejecutor.ejecutar(programa)
