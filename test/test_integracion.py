
import unittest
import subprocess
import sys
from pathlib import Path

PROYECTO = Path(__file__).resolve().parent.parent
MAIN = PROYECTO / "main.py"
PROGRAMAS = PROYECTO / "programas_prueba"


class TestIntegracion(unittest.TestCase):

    def ejecutar_programa(self, nombre):
        archivo = PROGRAMAS / nombre

        resultado = subprocess.run(
            [sys.executable, str(MAIN), str(archivo)],
            capture_output=True,
            text=True
        )

        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        return resultado.stdout

    def test_inventario_completo(self):
        salida = self.ejecutar_programa("07_inventario_completo.txt")
        self.assertIn("Cafe", salida)
        self.assertIn("Azucar", salida)
        self.assertIn("Valor total: 39000.00", salida)

    def test_variables_y_repeticion(self):
        salida = self.ejecutar_programa("08_variables_y_repeticion.txt")
        self.assertIn("6000.0", salida)
        self.assertIn("Compra necesaria", salida)
        self.assertIn("6", salida)

    def test_eliminar_producto(self):
        salida = self.ejecutar_programa("09_eliminar_producto.txt")
        self.assertIn("Producto 301 eliminado.", salida)
        self.assertIn("No se encontró el producto.", salida)
        self.assertIn("Registros: 0", salida)
        self.assertIn("Valor total: 0.00", salida)


if __name__ == "__main__":
    unittest.main()
