import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import tempfile
from unittest.mock import patch

from generador_python import generar_python
from lexico.tokenizer import tokenizar
from semantico.analizador import analizar_semantica
from sintactico.parser import analizar_sintaxis


class PruebasGeneradorPython(unittest.TestCase):
    def traducir_y_ejecutar(self, codigo, entrada=None):
        programa = analizar_sintaxis(tokenizar(codigo))
        analizar_semantica(programa)
        traduccion = generar_python(programa)
        salida = StringIO()

        with patch("builtins.input", return_value=entrada):
            with redirect_stdout(salida):
                exec(compile(traduccion, "<traduccion>", "exec"), {})

        return salida.getvalue()

    def test_traduce_variables_condiciones_y_repeticiones(self):
        codigo = """inicio {
int if = 0
float precio = 2
precio = 3
repetir 2 veces {
    if += 1
}
si if == 2 {
    mostrar(precio)
} sino {
    mostrar(0)
}
} fin"""

        self.assertEqual(self.traducir_y_ejecutar(codigo), "3.0\n")

    def test_traduce_comandos_del_inventario(self):
        codigo = """inicio {
producto(101, "Arroz", 2, 3.5)
entrada(101, 2)
salida(101, 1)
consultar("Arroz")
consultar todos()
consultar valor()
eliminar(101)
consultar todos()
} fin"""
        esperado = (
            "Producto registrado: Arroz\n"
            "Entrada registrada: Arroz\n"
            "Salida registrada: Arroz\n"
            "Código: 101 | Nombre: Arroz | Cantidad: 3 | "
            "Precio: 3.50 | Valor: 10.50\n"
            "Código: 101 | Nombre: Arroz | Cantidad: 3 | "
            "Precio: 3.50 | Valor: 10.50\n"
            "Registros: 1\n"
            "Valor total: 10.50\n"
            "Producto 101 eliminado.\n"
            "El inventario está vacío.\n"
        )

        self.assertEqual(self.traducir_y_ejecutar(codigo), esperado)

    def test_traduce_lectura_de_datos(self):
        codigo = """inicio {
int cantidad
leer(cantidad)
mostrar(cantidad)
} fin"""

        self.assertEqual(self.traducir_y_ejecutar(codigo, "6"), "6\n")

    def test_traduce_division_entre_cero_con_ubicacion(self):
        codigo = """inicio {
mostrar(10 / 0)
} fin"""
        programa = analizar_sintaxis(tokenizar(codigo))
        analizar_semantica(programa)
        traduccion = generar_python(programa)

        with self.assertRaisesRegex(ValueError, "línea 2, columna 12"):
            exec(compile(traduccion, "<traduccion>", "exec"), {})

    def test_main_guarda_la_traduccion_en_utf8(self):
        import main

        with tempfile.TemporaryDirectory() as directorio:
            salida_python = Path(directorio) / "generado.py"
            salida_consola = StringIO()
            argumentos = [
                "main.py",
                "--python",
                r"programas_prueba\01_correcto_inventario.txt",
                str(salida_python),
            ]

            with patch("sys.argv", argumentos):
                with redirect_stdout(salida_consola):
                    main.main()

            traduccion = salida_python.read_text(encoding="utf-8")
            compile(traduccion, str(salida_python), "exec")
            self.assertIn("Traducción guardada en:", salida_consola.getvalue())


if __name__ == "__main__":
    unittest.main()
