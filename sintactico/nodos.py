
from dataclasses import dataclass


@dataclass
class Programa:
    instrucciones: list


@dataclass
class Declaracion:
    tipo: str
    nombre: str
    valor: object


@dataclass
class Asignacion:
    nombre: str
    valor: object


@dataclass
class Mostrar:
    expresion: object


@dataclass
class Leer:
    nombre: str


@dataclass
class Producto:
    codigo: object
    nombre: object
    cantidad: object
    precio: object


@dataclass
class Entrada:
    producto: str
    cantidad: object


@dataclass
class Salida:
    producto: str
    cantidad: object


@dataclass
class Consultar:
    producto: str


@dataclass
class Eliminar:
    producto: str


@dataclass
class Condicion:
    condicion: object
    instrucciones: list
    sino: list


@dataclass
class Repeticion:
    veces: object
    instrucciones: list


@dataclass
class Operacion:
    izquierda: object
    operador: str
    derecha: object


@dataclass
class Literal:
    valor: object


@dataclass
class Variable:
    nombre: str
