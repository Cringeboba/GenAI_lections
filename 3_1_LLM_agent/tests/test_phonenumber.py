# tests/test_phonenumber.py

"""
Юнит-тесты для PhoneNumberTool.

Запуск:
    python -m pytest tests/ -v
"""

import unittest

from llm_agent.tool_phonenumber import PhoneNumberTool


class TestPhoneNumberTool(unittest.TestCase):

    def setUp(self):
        self.tool = PhoneNumberTool(default_region="RU")

    # ------------------------------------------------------------------ #
    #  Тест 1. Валидный российский мобильный номер                        #
    # ------------------------------------------------------------------ #
    def test_valid_russian_mobile(self):
        result = self.tool.use("+7 (912) 345-67-89")

        self.assertTrue(result["valid"], msg=f"Результат: {result}")
        self.assertTrue(result["possible"])
        self.assertEqual(result["e164"], "+79123456789")
        self.assertEqual(result["country_code"], 7)
        self.assertEqual(result["region"], "RU")
        self.assertEqual(result["type"], "mobile")
        # Международный формат должен содержать код страны
        self.assertIn("+7", result["international"])

    # ------------------------------------------------------------------ #
    #  Тест 2. Номер без '+' с указанием региона                           #
    # ------------------------------------------------------------------ #
    def test_local_number_with_region(self):
        result = self.tool.use("8 912 345 67 89; region=RU")

        self.assertTrue(result["valid"], msg=f"Результат: {result}")
        self.assertEqual(result["e164"], "+79123456789")
        self.assertEqual(result["region"], "RU")

    # ------------------------------------------------------------------ #
    #  Тест 3. Американский номер в национальном формате                   #
    # ------------------------------------------------------------------ #
    def test_us_number(self):
        result = self.tool.use("(202) 555-0147; region=US")

        self.assertEqual(result["country_code"], 1)
        self.assertEqual(result["region"], "US")
        # E.164 должен начинаться с +1
        self.assertTrue(result["e164"].startswith("+1"))
        self.assertTrue(result["possible"])

    # ------------------------------------------------------------------ #
    #  Тест 4. Невалидный / мусорный ввод                                  #
    # ------------------------------------------------------------------ #
    def test_invalid_input(self):
        result = self.tool.use("это не телефон")

        self.assertFalse(result["valid"])
        self.assertIn("error", result)

    # ------------------------------------------------------------------ #
    #  Тест 5. Пустой ввод                                                 #
    # ------------------------------------------------------------------ #
    def test_empty_input(self):
        result = self.tool.use("")

        self.assertIn("error", result)
        self.assertNotIn("valid", result)


# ---------------------------------------------------------------------- #
#  Обёртка, которую требует задание: "вызвать их внутри отдельной         #
#  тестовой функции". Кроме pytest-совместимости, можно запустить         #
#  напрямую: python tests/test_phonenumber.py                             #
# ---------------------------------------------------------------------- #
def run_all_tests():
    """Запуск всех тестов через unittest (без pytest)."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPhoneNumberTool)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    ok = run_all_tests()
    raise SystemExit(0 if ok else 1)