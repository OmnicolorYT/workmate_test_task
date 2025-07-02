"""Логика фильтрации для csvtool.

Модуль разбирает и применяет выражения `--where`, например:
    `price>300`
    `name=John`
    `rating=4.5`
"""
from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Iterable, List, Dict, Callable, Optional

__all__ = ["apply_where"]

# Регулярное выражение для парсинга строк вида "price>300" или "name=John"
# TODO Если нужно добавить доп.операторы - их нужно прописать в регулярке
_EXPR_RE = re.compile(r"(?P<column>[\w\s]+)(?P<op>[><=])(?P<value>.+)")

Comparator = Callable[[str, str], bool]


def _to_decimal_maybe(value: str) -> Optional[Decimal]:
    """Преобразует строку value в :class:`~decimal.Decimal`, если возможно.

    Возвращает ``None``, если значение не является числом.
    Поддерживаются разделители дробной части «.» и «,».
    """
    try:
        cleaned = value.replace(",", ".")
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def _make_comparator(op: str, sample_value: str) -> Comparator:
    """Создаёт функцию‑компаратор для оператора op.

    Сначала по sample_value определяется тип колонки (число/строка),
    после чего подбирается нужный тип сравнения.
    """
    # Проверяем, является ли значение числом
    sample_num = _to_decimal_maybe(sample_value)

    if sample_num is not None:
        value_parser = _to_decimal_maybe

        def compare_numeric(a: str, b: str) -> bool:
            aval = value_parser(a)
            bval = value_parser(b)
            if aval is None or bval is None:
                raise ValueError(
                    "Несовместимые типы: попытка сравнить строку и число в условии where"
                )
            # TODO Если нужен доп.оператор - его необходимо вписать в условие
            if op == ">":
                return aval > bval
            elif op == "<":
                return aval < bval
            elif op == "=":
                return aval == bval
            raise ValueError(f"Неизвестный оператор: {op}")

        return compare_numeric

    # Строковая колонка: допустим только '='
    if op != "=":
        raise ValueError("Для строковых колонок поддерживается только оператор '='.")

    def compare_str(a: str, b: str) -> bool:
        return a == b

    return compare_str


def apply_where(rows: Iterable[Dict[str, str]], expr: str) -> List[Dict[str, str]]:
    """Фильтрует rows по условию expr.

    Параметры
    ---------
    rows
        Итератор словарей «колонка → значение».
    expr
        Выражение вида ``column>value``, ``column<value`` или ``column=value``.

    Возвращает
    ---------
    List[Dict[str, str]]
        Список строк, удовлетворяющих условию.
    """
    match = _EXPR_RE.fullmatch(expr.strip())
    if not match:
        raise ValueError("Некорректное выражение --where. Ожидается 'column[><=]value'.")

    column = match.group("column").strip()
    op = match.group("op")
    rhs_raw = match.group("value").strip()

    # Берём первую строку, чтобы проверить наличие колонки и определить тип
    try:
        first_row = next(iter(rows))
    except StopIteration:
        return []

    if column not in first_row:
        raise ValueError(f"Колонка '{column}' не найдена в CSV.")

    comparator = _make_comparator(op, first_row[column])

    # Применяем фильтр
    filtered: List[Dict[str, str]] = [row for row in rows if comparator(row[column], rhs_raw)]
    return filtered
