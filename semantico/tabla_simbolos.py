
class TablaSimbolos:
    def __init__(self):
        self.simbolos = {}

    def declarar(self, nombre, tipo, valor=None):
        if nombre in self.simbolos:
            raise ValueError(
                f"La variable '{nombre}' ya fue declarada"
            )

        self.simbolos[nombre] = {
            "tipo": tipo,
            "valor": valor
        }

    def asignar(self, nombre, valor):
        if nombre not in self.simbolos:
            raise ValueError(
                f"La variable '{nombre}' no está declarada"
            )

        self.simbolos[nombre]["valor"] = valor

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
