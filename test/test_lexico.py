import unittest

from errores import ErrorLexico
from lexico.tokenizer import tokenizar


class PruebasLexicas(unittest.TestCase):
    def test_error_lexico_indica_su_fase(self):
        with self.assertRaises(ErrorLexico) as contexto:
            tokenizar("@")

        self.assertIn("Error léxico:", str(contexto.exception))


if __name__ == "__main__":
    unittest.main()
