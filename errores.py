class ErrorCompilador(Exception):
    def __init__(self, mensaje, linea, columna):
        self.mensaje = mensaje
        self.linea = linea
        self.columna = columna
        super().__init__(f"{mensaje} (línea {linea}, columna {columna})")


class ErrorLexico(ErrorCompilador):
    pass


class ErrorSintactico(ErrorCompilador):
    pass


class ErrorSemantico(ErrorCompilador):
    pass


class ErrorEjecucion(ErrorCompilador):
    pass