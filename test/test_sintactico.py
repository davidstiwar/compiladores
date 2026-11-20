import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from errores import ErrorEjecucion, ErrorSintactico
from interprete.ejecutor import ejecutar_programa
from lexico.tokenizer import tokenizar
from semantico.analizador import analizar_semantica
from sintactico.parser import analizar_sintaxis


class PruebasSintactico(unittest.TestCase):
    def ejecutar_codigo(self, codigo):
        programa = analizar_sintaxis(tokenizar(codigo))
        tabla = analizar_semantica(programa)
        salida = StringIO()
        with redirect_stdout(salida):
            ejecutar_programa(programa, tabla)
        return salida.getvalue()

    def test_asignaciones_simples_compuestas_y_precedencia(self):
        codigo = """inicio {
            float total = 20
            total = total + 4 * 2
            total += 4
            total -= 2
            total *= 3
            total /= 2
            mostrar(total)
        } fin"""

        self.assertEqual(self.ejecutar_codigo(codigo), "45.0\n")

    def test_operadores_del_mismo_nivel_se_evaluan_de_izquierda_a_derecha(self):
        codigo = """inicio {
            mostrar(8 - 3 - 1)
            mostrar(20 / 2 / 2)
        } fin"""

        self.assertEqual(self.ejecutar_codigo(codigo), "4\n5.0\n")

    def test_entero_asignado_a_float_se_muestra_como_decimal(self):
        codigo = """inicio {
float numero = 1
numero = 2
mostrar(numero + 1)
} fin"""

        self.assertEqual(self.ejecutar_codigo(codigo), "3.0\n")

    def test_acepta_varias_instrucciones_en_una_linea(self):
        codigo = "inicio { int cantidad = 1 mostrar(cantidad) } fin"

        self.assertEqual(self.ejecutar_codigo(codigo), "1\n")

    def test_mostrar_exige_parentesis(self):
        codigo = "inicio {\nmostrar 1\n} fin"

        with self.assertRaises(ErrorSintactico) as contexto:
            analizar_sintaxis(tokenizar(codigo))

        self.assertIn("PARENTESIS_ABRE", str(contexto.exception))

    def test_condiciones_logicas_y_sino(self):
        codigo = """inicio {
            bool activo = verdadero || falso && falso
            si !activo {
                mostrar("incorrecto")
            } sino {
                mostrar("correcto")
            }
        } fin"""

        self.assertEqual(self.ejecutar_codigo(codigo), "correcto\n")

    def test_repeticiones_anidadas(self):
        codigo = """inicio {
            int contador = 0
            repetir 2 veces {
                repetir 3 veces {
                    contador += 1
                }
            }
            mostrar(contador)
        } fin"""

        self.assertEqual(self.ejecutar_codigo(codigo), "6\n")

    def test_leer_y_mostrar_con_parentesis(self):
        codigo = """inicio {
            str nombre
            leer(nombre)
            mostrar(nombre)
        } fin"""
        programa = analizar_sintaxis(tokenizar(codigo))
        tabla = analizar_semantica(programa)
        salida = StringIO()

        with patch("builtins.input", return_value="David"):
            with redirect_stdout(salida):
                ejecutar_programa(programa, tabla)

        self.assertEqual(salida.getvalue(), "David\n")

    def test_tabla_semantica_es_la_que_usa_el_ejecutor(self):
        codigo = """inicio {
int cantidad = 4
cantidad += 1
} fin"""
        programa = analizar_sintaxis(tokenizar(codigo))
        tabla = analizar_semantica(programa)

        tabla_ejecutada = ejecutar_programa(programa, tabla)

        self.assertIs(tabla_ejecutada, tabla)
        self.assertEqual(tabla.obtener("cantidad"), 5)

    def test_consultar_producto_muestra_el_mismo_formato(self):
        codigo = """inicio {
producto(101, "Arroz", 2, 3.5)
consultar todos()
consultar(101)
} fin"""
        linea_producto = (
            "Código: 101 | Nombre: Arroz | Cantidad: 2 | "
            "Precio: 3.50 | Valor: 7.00\n"
        )

        self.assertEqual(
            self.ejecutar_codigo(codigo),
            "Producto registrado: Arroz\n" + linea_producto * 2
        )

    def test_error_sintactico_con_linea_y_columna(self):
        codigo = """inicio {
  mostrar(1 + )
} fin"""

        with self.assertRaises(ErrorSintactico) as contexto:
            analizar_sintaxis(tokenizar(codigo))

        self.assertEqual(contexto.exception.linea, 2)
        self.assertEqual(contexto.exception.columna, 15)
        self.assertIn("Error sintáctico:", str(contexto.exception))

    def test_fin_es_obligatorio(self):
        codigo = "inicio {\nmostrar(1)\n}"

        with self.assertRaises(ErrorSintactico) as contexto:
            analizar_sintaxis(tokenizar(codigo))

        self.assertIn("FIN", str(contexto.exception))
        self.assertEqual(contexto.exception.linea, 3)
        self.assertEqual(contexto.exception.columna, 2)

    def test_leer_rechaza_un_valor_negativo_con_su_ubicacion(self):
        codigo = """inicio {
int cantidad = 0
leer(cantidad)
} fin"""
        programa = analizar_sintaxis(tokenizar(codigo))
        tabla = analizar_semantica(programa)

        with patch("builtins.input", return_value="-2"):
            with self.assertRaises(ErrorEjecucion) as contexto:
                ejecutar_programa(programa, tabla)

        self.assertEqual(contexto.exception.linea, 3)
        self.assertEqual(contexto.exception.columna, 1)

    def test_division_entre_cero_se_informa_durante_ejecucion(self):
        codigo = """inicio {
mostrar(10 / 0)
} fin"""
        programa = analizar_sintaxis(tokenizar(codigo))
        tabla = analizar_semantica(programa)

        with self.assertRaises(ErrorEjecucion) as contexto:
            ejecutar_programa(programa, tabla)

        self.assertIn("dividir entre cero", str(contexto.exception))
        self.assertIn("Error de ejecución:", str(contexto.exception))
        self.assertEqual(contexto.exception.linea, 2)

    def test_leer_float_rechaza_valores_no_finitos(self):
        codigo = """inicio {
float numero
leer(numero)
} fin"""
        programa = analizar_sintaxis(tokenizar(codigo))
        tabla = analizar_semantica(programa)

        for entrada in ("nan", "inf", "-inf", "1e309"):
            with self.subTest(entrada=entrada):
                with patch("builtins.input", return_value=entrada):
                    with redirect_stdout(StringIO()):
                        with self.assertRaises(ErrorEjecucion) as contexto:
                            ejecutar_programa(programa, tabla)

                self.assertIn("finito", str(contexto.exception))


if __name__ == "__main__":
    unittest.main()
