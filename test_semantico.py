import unittest

from errores import ErrorSemantico
from lexico.tokenizer import tokenizar
from semantico.analizador import analizar_semantica
from sintactico.parser import analizar_sintaxis


class PruebasSemanticas(unittest.TestCase):
    def analizar_codigo(self, codigo):
        programa = analizar_sintaxis(tokenizar(codigo))
        return analizar_semantica(programa)

    def test_tipos_operaciones_logicas_y_asignaciones_compuestas(self):
        codigo = """inicio {
int cantidad = 2
cantidad += 3
float promedio = cantidad / 2
bool disponible = promedio >= 2 && !falso
str nombre = "tienda" + " uno"
} fin"""

        tabla = self.analizar_codigo(codigo)

        self.assertEqual(tabla.obtener("cantidad"), 5)
        self.assertEqual(tabla.obtener("promedio"), 2.5)
        self.assertIs(tabla.obtener("disponible"), True)
        self.assertEqual(tabla.obtener("nombre"), "tienda uno")

    def test_errores_semanticos_indican_linea_y_columna(self):
        casos = (
            ("inicio {\nmostrar(noExiste)\n} fin", 2, 9),
            ("inicio {\nint cantidad = 1.5\n} fin", 2, 16),
            ("inicio {\nbool activo = 1\n} fin", 2, 15),
            ("inicio {\nmostrar(\"a\" - \"b\")\n} fin", 2, 13),
            ("inicio {\nsi 1 { mostrar(1) }\n} fin", 2, 4),
            ("inicio {\nrepetir 1.5 veces {}\n} fin", 2, 9),
            ("inicio {\nrepetir 0 - 1 veces {}\n} fin", 2, 11),
            ("inicio {\nint total = 0 - 1\n} fin", 2, 15),
            ("inicio {\nproducto(\"1\", \"A\", 1, 2)\n} fin", 2, 10),
            ("inicio {\nentrada(1, 1.5)\n} fin", 2, 12),
            ("inicio {\neliminar(\"1\")\n} fin", 2, 10),
        )

        for codigo, linea, columna in casos:
            with self.subTest(codigo=codigo):
                with self.assertRaises(ErrorSemantico) as contexto:
                    self.analizar_codigo(codigo)
                self.assertEqual(contexto.exception.linea, linea)
                self.assertEqual(contexto.exception.columna, columna)

    def test_rechaza_declaracion_duplicada(self):
        codigo = """inicio {
int total = 1
int total = 2
} fin"""

        with self.assertRaises(ErrorSemantico) as contexto:
            self.analizar_codigo(codigo)

        self.assertEqual(contexto.exception.linea, 3)
        self.assertEqual(contexto.exception.columna, 1)
        self.assertIn("línea 2, columna 1", str(contexto.exception))
        self.assertIn("Error semántico:", str(contexto.exception))

    def test_entero_asignado_a_float_se_convierte_a_decimal(self):
        codigo = """inicio {
float precio = 1
precio = 2
} fin"""

        tabla = self.analizar_codigo(codigo)

        self.assertIs(type(tabla.obtener("precio")), float)
        self.assertEqual(tabla.obtener("precio"), 2.0)

    def test_tabla_guarda_la_ubicacion_declarada(self):
        codigo = """inicio {
int cantidad = 2
cantidad += 1
} fin"""

        tabla = self.analizar_codigo(codigo)

        self.assertEqual(tabla.simbolos["cantidad"]["linea"], 2)
        self.assertEqual(tabla.simbolos["cantidad"]["columna"], 1)

    def test_rechaza_condiciones_y_cantidades_invalidas(self):
        codigo = """inicio {
producto(1, "Arroz", 0, 2)
} fin"""

        with self.assertRaises(ErrorSemantico) as contexto:
            self.analizar_codigo(codigo)

        self.assertIn("cantidad inicial", str(contexto.exception))
        self.assertEqual(contexto.exception.linea, 2)

    def test_rechaza_codigos_duplicados_y_salidas_sin_existencias(self):
        casos = (
            """inicio {
producto(1, "Arroz", 2, 3)
producto(1, "Otro", 1, 4)
} fin""",
            """inicio {
producto(1, "Arroz", 2, 3)
salida(1, 3)
} fin""",
        )

        for codigo in casos:
            with self.subTest(codigo=codigo):
                with self.assertRaises(ErrorSemantico):
                    self.analizar_codigo(codigo)

    def test_null_se_puede_guardar_pero_no_usar_en_cuentas(self):
        programa = """inicio {
int cantidad
cantidad = null
} fin"""
        tabla = self.analizar_codigo(programa)
        self.assertIs(tabla.simbolos["cantidad"]["inicializado"], False)

        codigo = """inicio {
int cantidad
int total = cantidad + 1
} fin"""
        with self.assertRaises(ErrorSemantico) as contexto:
            self.analizar_codigo(codigo)

        self.assertIn("numéricos", str(contexto.exception))
        self.assertEqual(contexto.exception.linea, 3)
        self.assertEqual(contexto.exception.columna, 22)


if __name__ == "__main__":
    unittest.main()
