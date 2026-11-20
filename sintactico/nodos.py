
from dataclasses import dataclass


@dataclass
class Programa:
    instrucciones: list
    linea: int = 1
    columna: int = 1


@dataclass
class Declaracion:
    tipo: str
    nombre: str
    valor: object
    linea: int = 1
    columna: int = 1


@dataclass
class Asignacion:
    nombre: str
    valor: object
    operador: str = "="
    linea: int = 1
    columna: int = 1


@dataclass
class Mostrar:
    expresion: object
    linea: int = 1
    columna: int = 1


@dataclass
class Leer:
    nombre: str
    linea: int = 1
    columna: int = 1


@dataclass
class Producto:
    codigo: object
    nombre: object
    cantidad: object
    precio: object
    linea: int = 1
    columna: int = 1


@dataclass
class Entrada:
    producto: object
    cantidad: object
    linea: int = 1
    columna: int = 1


@dataclass
class Salida:
    producto: object
    cantidad: object
    linea: int = 1
    columna: int = 1


@dataclass
class Consultar:
    producto: object
    linea: int = 1
    columna: int = 1


@dataclass
class Eliminar:
    producto: object
    linea: int = 1
    columna: int = 1


@dataclass
class Condicion:
    condicion: object
    instrucciones: list
    sino: list
    linea: int = 1
    columna: int = 1


@dataclass
class Repeticion:
    veces: object
    instrucciones: list
    linea: int = 1
    columna: int = 1


@dataclass
class Operacion:
    izquierda: object
    operador: str
    derecha: object
    linea: int = 1
    columna: int = 1


@dataclass
class OperacionUnaria:
    operador: str
    operando: object
    linea: int = 1
    columna: int = 1


@dataclass
class Literal:
    valor: object
    linea: int = 1
    columna: int = 1


@dataclass
class Variable:
    nombre: str
    linea: int = 1
    columna: int = 1
