
class TablaSimbolos:
    def __init__(self):
        self.simbolos = {}

    def declarar(
        self, nombre, tipo, valor=None, inicializado=None, linea=1, columna=1
    ):
        if nombre in self.simbolos:
            declaracion = self.simbolos[nombre]
            raise ValueError(
                f"La variable '{nombre}' ya fue declarada en "
                f"línea {declaracion['linea']}, columna {declaracion['columna']}"
            )

        if inicializado is None:
            inicializado = valor is not None

        self.simbolos[nombre] = {
            "tipo": tipo,
            "valor": valor,
            "inicializado": inicializado,
            "linea": linea,
            "columna": columna,
        }

    def asignar(self, nombre, valor, inicializado=None):
        if nombre not in self.simbolos:
            raise ValueError(
                f"La variable '{nombre}' no está declarada"
            )

        if inicializado is None:
            inicializado = valor is not None

        self.simbolos[nombre]["valor"] = valor
        self.simbolos[nombre]["inicializado"] = inicializado

    def reiniciar_valores(self):
        for simbolo in self.simbolos.values():
            simbolo["valor"] = None
            simbolo["inicializado"] = False

    def obtener(self, nombre):
        if nombre not in self.simbolos:
            raise ValueError(
                f"La variable '{nombre}' no está declarada"
            )

        return self.simbolos[nombre]["valor"]

    def obtener_tipo(self, nombre):
        if nombre not in self.simbolos:
            raise ValueError(
                f"La variable '{nombre}' no está declarada"
            )

        return self.simbolos[nombre]["tipo"]

    def existe(self, nombre):
        return nombre in self.simbolos
