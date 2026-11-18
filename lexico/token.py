from dataclasses import dataclass


@dataclass
class Token:
    """Una pieza del programa: tipo, valor, línea y columna"""
    tipo: str
    valor: str
    linea: int
    columna: int

    def __repr__(self):
        return f"Token({self.tipo}, {self.valor!r}, línea {self.linea}, col {self.columna})"