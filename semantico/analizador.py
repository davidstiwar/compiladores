from .tabla_simbolos import TablaSimbolos
from errores import ErrorSemantico
from sintactico.nodos import Literal, Operacion, Variable


class AnalizadorSemantico:
    TIPOS = {"int", "float", "str", "bool"}
    TIPOS_NUMERICOS = {"int", "float"}

    def __init__(self):
        self.tabla = TablaSimbolos()
        self.productos = {}

    def analizar(self, programa):
        for instruccion in programa.instrucciones:
            self.analizar_instruccion(instruccion)

        return self.tabla

    def _error(self, mensaje, nodo):
        raise ErrorSemantico(
            mensaje,
            getattr(nodo, "linea", 1),
            getattr(nodo, "columna", 1)
        )

    def analizar_instruccion(self, instruccion):
        tipo_instruccion = instruccion.__class__.__name__

        if tipo_instruccion == "Declaracion":
            nombre = instruccion.nombre
            tipo = instruccion.tipo

            if tipo not in self.TIPOS:
                self._error(f"Tipo de dato no reconocido: {tipo}", instruccion)
            if self.tabla.existe(nombre):
                declaracion = self.tabla.simbolos[nombre]
                self._error(
                    f"La variable '{nombre}' ya fue declarada en "
                    f"línea {declaracion['linea']}, "
                    f"columna {declaracion['columna']}",
                    instruccion
                )

            valor = None
            inicializado = False
            if instruccion.valor is not None:
                tipo_valor, valor, conocido = self._inferir(instruccion.valor)
                self._validar_tipo_inferido(
                    tipo, tipo_valor, instruccion.valor
                )
                if tipo == "float" and tipo_valor == "int" and conocido:
                    valor = float(valor)
                inicializado = tipo_valor != "null"
                if not conocido or not inicializado:
                    valor = None

            self.tabla.declarar(
                nombre,
                tipo,
                valor,
                inicializado,
                instruccion.linea,
                instruccion.columna
            )
            return

        if tipo_instruccion == "Asignacion":
            nombre = instruccion.nombre
            if not self.tabla.existe(nombre):
                self._error(
                    f"La variable '{nombre}' no está declarada", instruccion
                )

            expresion = instruccion.valor
            if instruccion.operador != "=":
                expresion = Operacion(
                    Variable(
                        nombre, instruccion.linea, instruccion.columna
                    ),
                    instruccion.operador[0],
                    expresion,
                    instruccion.linea,
                    instruccion.columna
                )

            tipo_valor, valor, conocido = self._inferir(expresion)
            tipo_variable = self.tabla.obtener_tipo(nombre)
            self._validar_tipo_inferido(
                tipo_variable, tipo_valor, instruccion.valor
            )
            if (
                tipo_variable == "float"
                and tipo_valor == "int"
                and conocido
            ):
                valor = float(valor)
            inicializado = tipo_valor != "null"
            self.tabla.asignar(
                nombre,
                valor if conocido and inicializado else None,
                inicializado
            )
            return

        if tipo_instruccion == "Mostrar":
            self._inferir(instruccion.expresion)
            return

        if tipo_instruccion == "Leer":
            if not self.tabla.existe(instruccion.nombre):
                self._error(
                    f"La variable '{instruccion.nombre}' no está declarada",
                    instruccion
                )
            self.tabla.asignar(instruccion.nombre, None, True)
            return

        if tipo_instruccion == "Condicion":
            tipo_condicion, _, _ = self._inferir(instruccion.condicion)
            if tipo_condicion != "bool":
                self._error(
                    "La condición debe ser verdadera o falsa",
                    instruccion.condicion
                )

            # Cada rama parte del mismo estado para no mezclar sus asignaciones.
            estado_anterior = {
                nombre: simbolo.copy()
                for nombre, simbolo in self.tabla.simbolos.items()
            }
            inventario_anterior = self._copiar_inventario()
            for elemento in instruccion.instrucciones:
                self.analizar_instruccion(elemento)

            estado_si = {
                nombre: simbolo.copy()
                for nombre, simbolo in self.tabla.simbolos.items()
            }
            inventario_si = self._copiar_inventario()
            self.tabla.simbolos = {
                nombre: simbolo.copy()
                for nombre, simbolo in estado_anterior.items()
            }
            self.productos = inventario_anterior
            for elemento in instruccion.sino:
                self.analizar_instruccion(elemento)

            estado_sino = {
                nombre: simbolo.copy()
                for nombre, simbolo in self.tabla.simbolos.items()
            }
            inventario_sino = self._copiar_inventario()
            nombres_comunes = estado_si.keys() & estado_sino.keys()
            self.tabla.simbolos = {}
            for nombre in nombres_comunes:
                simbolo_si = estado_si[nombre]
                simbolo_sino = estado_sino[nombre]
                if simbolo_si["tipo"] != simbolo_sino["tipo"]:
                    self._error(
                        f"La variable '{nombre}' tiene tipos diferentes "
                        "en las ramas de la condición",
                        instruccion
                    )
                valor_si = simbolo_si["valor"]
                valor_sino = simbolo_sino["valor"]
                inicializado_si = simbolo_si["inicializado"]
                inicializado_sino = simbolo_sino["inicializado"]
                inicializado = (
                    inicializado_si
                    if inicializado_si == inicializado_sino else None
                )
                valor = (
                    valor_si
                    if inicializado is True and valor_si == valor_sino
                    else None
                )
                self.tabla.simbolos[nombre] = {
                    "tipo": simbolo_si["tipo"],
                    "valor": valor,
                    "inicializado": inicializado,
                    "linea": simbolo_si["linea"],
                    "columna": simbolo_si["columna"],
                }
            productos_comunes = inventario_si.keys() & inventario_sino.keys()
            self.productos = {}
            for codigo in productos_comunes:
                producto_si = inventario_si[codigo]
                producto_sino = inventario_sino[codigo]
                cantidad_si = producto_si["cantidad"]
                cantidad_sino = producto_sino["cantidad"]
                self.productos[codigo] = {
                    "nombre": (
                        producto_si["nombre"]
                        if producto_si["nombre"] == producto_sino["nombre"]
                        else None
                    ),
                    "cantidad": (
                        cantidad_si if cantidad_si == cantidad_sino else None
                    ),
                }
            return

        if tipo_instruccion == "Repeticion":
            tipo_veces, veces, conocido = self._inferir(instruccion.veces)
            if tipo_veces != "int":
                self._error(
                    "La repetición necesita un entero no negativo",
                    instruccion.veces
                )
            if conocido and veces < 0:
                self._error(
                    "La repetición necesita un entero no negativo",
                    instruccion.veces
                )

            # El ciclo puede ejecutarse cero veces, por eso no se conservan valores.
            estado_anterior = {
                nombre: simbolo.copy()
                for nombre, simbolo in self.tabla.simbolos.items()
            }
            inventario_anterior = self._copiar_inventario()
            for elemento in instruccion.instrucciones:
                self.analizar_instruccion(elemento)
            estado_ciclo = self.tabla.simbolos
            self.tabla.simbolos = {}
            for nombre, simbolo_anterior in estado_anterior.items():
                simbolo_ciclo = estado_ciclo[nombre]
                iniciado_antes = simbolo_anterior["inicializado"]
                iniciado_despues = simbolo_ciclo["inicializado"]
                if iniciado_antes == iniciado_despues:
                    inicializado = iniciado_antes
                else:
                    inicializado = None
                valor = None
                if (
                    inicializado is True
                    and simbolo_anterior["valor"] == simbolo_ciclo["valor"]
                ):
                    valor = simbolo_anterior["valor"]
                self.tabla.simbolos[nombre] = {
                    "tipo": simbolo_anterior["tipo"],
                    "valor": valor,
                    "inicializado": inicializado,
                    "linea": simbolo_anterior["linea"],
                    "columna": simbolo_anterior["columna"],
                }
            self.productos = {
                codigo: {"nombre": producto["nombre"], "cantidad": None}
                for codigo, producto in inventario_anterior.items()
            }
            return

        if tipo_instruccion == "Producto":
            codigo = self._validar_expresion(
                instruccion.codigo, "int", "El código debe ser entero"
            )
            nombre = self._validar_expresion(
                instruccion.nombre, "str", "El nombre debe ser texto"
            )
            cantidad = self._validar_expresion(
                instruccion.cantidad, "int",
                "La cantidad inicial debe ser un entero positivo"
            )
            precio_tipo, precio, precio_conocido = self._inferir(
                instruccion.precio
            )
            if precio_tipo not in self.TIPOS_NUMERICOS:
                self._error("El precio debe ser numérico", instruccion.precio)
            if precio_conocido and precio <= 0:
                self._error(
                    "El precio debe ser un número positivo", instruccion.precio
                )
            if cantidad is not None and cantidad <= 0:
                self._error(
                    "La cantidad inicial debe ser un entero positivo",
                    instruccion.cantidad
                )
            if codigo is not None and codigo in self.productos:
                self._error(
                    f"El código {codigo} ya está registrado", instruccion
                )
            if codigo is not None:
                self.productos[codigo] = {
                    "nombre": nombre,
                    "cantidad": cantidad,
                }
            return

        if tipo_instruccion in ("Entrada", "Salida"):
            tipo_producto, identificador, id_conocido = self._inferir(
                instruccion.producto
            )
            if tipo_producto not in ("int", "str"):
                self._error(
                    "El producto debe identificarse con código o nombre",
                    instruccion.producto
                )

            cantidad = self._validar_expresion(
                instruccion.cantidad, "int",
                "La cantidad debe ser un entero positivo"
            )
            if cantidad is not None and cantidad <= 0:
                self._error(
                    "La cantidad debe ser un entero positivo",
                    instruccion.cantidad
                )
            if id_conocido:
                producto = self._buscar_producto(identificador)
                if producto is not None and cantidad is not None:
                    if tipo_instruccion == "Entrada":
                        if producto["cantidad"] is not None:
                            producto["cantidad"] += cantidad
                    elif producto["cantidad"] is not None:
                        if cantidad > producto["cantidad"]:
                            self._error(
                                "No puedes retirar más unidades de las existentes",
                                instruccion
                            )
                        producto["cantidad"] -= cantidad
                elif producto is not None:
                    producto["cantidad"] = None
            return

        if tipo_instruccion == "Consultar":
            if instruccion.producto in ("todos", "valor"):
                return
            tipo_producto, _, _ = self._inferir(instruccion.producto)
            if tipo_producto not in ("int", "str"):
                self._error(
                    "La consulta necesita un código o nombre de producto",
                    instruccion.producto
                )
            return

        if tipo_instruccion == "Eliminar":
            codigo = self._validar_expresion(
                instruccion.producto, "int",
                "Para eliminar debes indicar el código entero"
            )
            if codigo is not None:
                self.productos.pop(codigo, None)
            return

        self._error(
            f"Instrucción sin validación semántica: {tipo_instruccion}",
            instruccion
        )

    def _validar_expresion(self, expresion, tipo_esperado, mensaje):
        tipo_valor, valor, conocido = self._inferir(expresion)
        coincide = tipo_valor == tipo_esperado
        if tipo_esperado == "float" and tipo_valor in self.TIPOS_NUMERICOS:
            coincide = True
        if not coincide:
            self._error(mensaje, expresion)
        return valor if conocido else None

    def _copiar_inventario(self):
        return {
            codigo: producto.copy()
            for codigo, producto in self.productos.items()
        }

    def _buscar_producto(self, identificador):
        if type(identificador) is int:
            return self.productos.get(identificador)
        if type(identificador) is str:
            coincidencias = [
                producto for producto in self.productos.values()
                if producto["nombre"] is not None
                and producto["nombre"].lower() == identificador.lower()
            ]
            if len(coincidencias) == 1:
                return coincidencias[0]
        return None

    def _tipo_de_valor(self, valor):
        if valor is None:
            return "null"
        if type(valor) is bool:
            return "bool"
        if type(valor) is int:
            return "int"
        if type(valor) is float:
            return "float"
        if type(valor) is str:
            return "str"
        return "desconocido"

    def _validar_tipo_inferido(self, esperado, recibido, nodo):
        if recibido == "null":
            return

        coincide = recibido == esperado
        if esperado == "float" and recibido in self.TIPOS_NUMERICOS:
            coincide = True

        if not coincide:
            self._error(
                f"El valor de tipo {recibido} no corresponde al tipo {esperado}",
                nodo
            )

    def _inferir(self, expresion):
        clase = expresion.__class__.__name__

        if clase == "Literal":
            return self._tipo_de_valor(expresion.valor), expresion.valor, True

        if clase == "Variable":
            if not self.tabla.existe(expresion.nombre):
                self._error(
                    f"La variable '{expresion.nombre}' no está declarada",
                    expresion
                )
            simbolo = self.tabla.simbolos[expresion.nombre]
            inicializado = simbolo["inicializado"]
            if inicializado is False:
                return "null", None, True
            if inicializado is None:
                return "null", None, False
            valor = simbolo["valor"]
            return (
                simbolo["tipo"],
                valor,
                valor is not None
            )

        if clase == "OperacionUnaria":
            tipo, valor, conocido = self._inferir(expresion.operando)
            if tipo != "bool":
                self._error(
                    "El operador ! necesita un valor verdadero o falso",
                    expresion
                )
            return "bool", not valor if conocido else None, conocido

        if clase == "Operacion":
            tipo_izquierda, izquierda, izquierda_conocida = self._inferir(
                expresion.izquierda
            )
            tipo_derecha, derecha, derecha_conocida = self._inferir(
                expresion.derecha
            )
            tipo_resultado = self._validar_operacion(
                expresion.operador,
                tipo_izquierda,
                tipo_derecha,
                expresion
            )

            if expresion.operador == "&&" and izquierda_conocida and not izquierda:
                return "bool", False, True
            if expresion.operador == "||" and izquierda_conocida and izquierda:
                return "bool", True, True

            if (
                expresion.operador == "/"
                and derecha_conocida
                and derecha == 0
            ):
                return tipo_resultado, None, False

            conocido = izquierda_conocida and derecha_conocida
            if not conocido:
                return tipo_resultado, None, False

            try:
                valor = self._calcular(
                    expresion.operador, izquierda, derecha
                )
            except (TypeError, ValueError, OverflowError) as error:
                self._error(f"Operación no válida: {error}", expresion)
            if self._tipo_de_valor(valor) in self.TIPOS_NUMERICOS and valor < 0:
                self._error("No se admiten números negativos", expresion)
            return tipo_resultado, valor, True

        self._error("Expresión no válida", expresion)

    def _validar_operacion(self, operador, izquierda, derecha, nodo):
        if operador in ("&&", "||"):
            if izquierda == derecha == "bool":
                return "bool"
            self._error(
                f"El operador {operador} solo admite valores booleanos", nodo
            )

        if operador == "+" and izquierda == derecha == "str":
            return "str"

        if operador in ("+", "-", "*", "/"):
            if (
                izquierda in self.TIPOS_NUMERICOS
                and derecha in self.TIPOS_NUMERICOS
            ):
                if operador == "/" or "float" in (izquierda, derecha):
                    return "float"
                return "int"
            self._error(
                f"El operador {operador} necesita valores numéricos "
                "o dos textos para concatenar con +",
                nodo
            )

        if operador in ("==", "!="):
            compatibles = (
                izquierda == derecha
                or izquierda in self.TIPOS_NUMERICOS
                and derecha in self.TIPOS_NUMERICOS
                or izquierda == "null"
                or derecha == "null"
            )
            if compatibles:
                return "bool"
            self._error(
                "No se pueden comparar valores de tipos diferentes", nodo
            )

        if operador in (">", "<", ">=", "<="):
            if (
                izquierda in self.TIPOS_NUMERICOS
                and derecha in self.TIPOS_NUMERICOS
                or izquierda == derecha == "str"
            ):
                return "bool"
            self._error(
                f"El operador {operador} necesita valores del mismo tipo "
                "numérico o texto",
                nodo
            )

        self._error(f"Operador no válido: {operador}", nodo)

    def _calcular(self, operador, izquierda, derecha):
        if operador == "+":
            return izquierda + derecha
        if operador == "-":
            return izquierda - derecha
        if operador == "*":
            return izquierda * derecha
        if operador == "/":
            return izquierda / derecha
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
        if operador == "&&":
            return izquierda and derecha
        if operador == "||":
            return izquierda or derecha
        self._error(f"Operador no válido: {operador}", Literal(None))

def analizar_semantica(programa):
    analizador = AnalizadorSemantico()
    return analizador.analizar(programa)
