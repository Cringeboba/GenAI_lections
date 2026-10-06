# llm_agent/tool_phonenumber.py

import phonenumbers

from phonenumbers import (
    geocoder,
    carrier,
    NumberParseException,
    PhoneNumberType,
    PhoneNumberFormat,
)


# Человекочитаемые названия типов номеров phonenumbers
_PHONE_TYPE_MAP = {
    PhoneNumberType.MOBILE: "mobile",
    PhoneNumberType.FIXED_LINE: "fixed_line",
    PhoneNumberType.FIXED_LINE_OR_MOBILE: "fixed_line_or_mobile",
    PhoneNumberType.TOLL_FREE: "toll_free",
    PhoneNumberType.PREMIUM_RATE: "premium_rate",
    PhoneNumberType.SHARED_COST: "shared_cost",
    PhoneNumberType.VOIP: "voip",
    PhoneNumberType.PERSONAL_NUMBER: "personal_number",
    PhoneNumberType.PAGER: "pager",
    PhoneNumberType.UAN: "uan",
    PhoneNumberType.VOICEMAIL: "voicemail",
    PhoneNumberType.UNKNOWN: "unknown",
}


class PhoneNumberTool:

    DEFAULT_REGION = "RU"  # регион по умолчанию, если номер задан без '+'

    def __init__(self, default_region: str = DEFAULT_REGION):
        self.default_region = default_region.upper()


    def use(self, tool_input: str) -> dict:
        """
        Точка входа для агента.

        Args:
            tool_input: строка вида "<номер>" или "<номер>; region=<XX>"

        Returns:
            dict с результатом разбора номера.
        """
        try:
            raw_phone, region = self._parse_input(tool_input)
        except ValueError as e:
            return {"error": str(e), "raw_input": tool_input}

        try:
            number = phonenumbers.parse(raw_phone, region)
        except NumberParseException as e:
            return {
                "raw_input": raw_phone,
                "region": region,
                "valid": False,
                "error": f"Не удалось распарсить номер: {e}",
            }

        return self._analyze(number, region)


    def _parse_input(self, tool_input: str) -> tuple:
        if not isinstance(tool_input, str) or not tool_input.strip():
            raise ValueError("Пустой ввод: ожидается телефонный номер.")

        text = tool_input.strip()
        region = self.default_region

        # Ищем указание региона: "; region=RU" или ", region=RU"
        for sep in (";", ","):
            if sep in text:
                parts = text.split(sep)
                # Первая часть — номер, остальные могут содержать region=
                text = parts[0].strip()
                for part in parts[1:]:
                    part = part.strip()
                    if part.lower().startswith("region="):
                        region = part.split("=", 1)[1].strip().upper()
                    elif len(part) == 2 and part.isalpha():
                        # допускаем просто "RU"
                        region = part.upper()
                break

        if not text:
            raise ValueError("Не удалось извлечь телефонный номер из ввода.")

        return text, region


    def _analyze(self, number: phonenumbers.PhoneNumber, region: str) -> dict:
        is_valid = phonenumbers.is_valid_number(number)
        is_possible = phonenumbers.is_possible_number(number)

        # Нормализованные представления
        try:
            e164 = phonenumbers.format_number(number, PhoneNumberFormat.E164)
        except Exception:
            e164 = None

        try:
            international = phonenumbers.format_number(
                number, PhoneNumberFormat.INTERNATIONAL
            )
        except Exception:
            international = None

        try:
            national = phonenumbers.format_number(
                number, PhoneNumberFormat.NATIONAL
            )
        except Exception:
            national = None

        try:
            rfc3966 = phonenumbers.format_number(
                number, PhoneNumberFormat.RFC3966
            )
        except Exception:
            rfc3966 = None

        # Код страны и национальный номер
        country_code = number.country_code
        national_number = number.national_number

        # Регион (ISO-код) из самого номера (может отличаться от переданного)
        detected_region = phonenumbers.region_code_for_number(number)

        # Гео-описание (город/регион)
        try:
            geo = geocoder.description_for_number(number, "ru") or None
        except Exception:
            geo = None

        # Оператор
        try:
            operator = carrier.name_for_number(number, "ru") or None
        except Exception:
            operator = None

        # Тип номера
        try:
            num_type = phonenumbers.number_type(number)
            type_name = _PHONE_TYPE_MAP.get(num_type, "unknown")
        except Exception:
            type_name = "unknown"

        return {
            "raw_input": str(number),
            "valid": is_valid,
            "possible": is_possible,
            "country_code": country_code,
            "national_number": national_number,
            "region": detected_region or region,
            "e164": e164,
            "international": international,
            "national": national,
            "rfc3966": rfc3966,
            "type": type_name,
            "operator": operator,
            "geo": geo,
        }