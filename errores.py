class ErrorCompilador(Exception):
    tipo_error = "Error del compilador"

    def __init__(self, mensaje, linea, columna):
        self.mensaje = mensaje
        self.linea = linea
        self.columna = columna
        super().__init__(
            f"{self.tipo_error}: {mensaje} "
            f"(línea {linea}, columna {columna})"
        )


class ErrorLexico(ErrorCompilador):
    tipo_error = "Error léxico"


class ErrorSintactico(ErrorCompilador):
    tipo_error = "Error sintáctico"


class ErrorSemantico(ErrorCompilador):
    tipo_error = "Error semántico"


class ErrorEjecucion(ErrorCompilador):
    tipo_error = "Error de ejecución"