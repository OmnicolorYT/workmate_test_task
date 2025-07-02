"""Тесты для модуля csvtool.filters."""
from decimal import Decimal

import pytest

from csvtool import filters
from csvtool.filters import apply_where

# ---------------------------------------------------------------------------
# Данные примеров
# ---------------------------------------------------------------------------

ROWS = [
    {"price": "100", "name": "Alpha"},
    {"price": "200", "name": "Beta"},
    {"price": "50", "name": "Alpha"},
]


# ---------------------------------------------------------------------------
# Позитивные сценарии (должны возвращать список строк)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "expr, expected_ids",
    [
        ("price>100", ["200"]),  # числовое сравнение >
        ("price<100", ["50"]),   # числовое сравнение <
        ("price=100", ["100"]),  # числовое сравнение =
        ("name=Alpha", ["100", "50"]),  # строковое равенство
    ],
)
def test_positive_filters(expr, expected_ids):
    result = apply_where(ROWS, expr)
    assert [r["price"] for r in result] == expected_ids


# ---------------------------------------------------------------------------
# Отрицательные сценарии (ожидаем ошибки)
# ---------------------------------------------------------------------------


def test_invalid_operator_on_string():
    """Попытка использовать > для строк вызывает ValueError."""
    with pytest.raises(ValueError, match="строковых колонок"):
        apply_where(ROWS, "name>Gamma")


def test_type_mismatch_numeric_vs_string():
    """Сравнение числа и строки в числовой колонке должно бросить ValueError."""
    with pytest.raises(ValueError, match="Несовместимые типы"):
        apply_where(ROWS, "price>foo")


def test_column_not_found():
    with pytest.raises(ValueError, match="Колонка 'age'"):
        apply_where(ROWS, "age>30")


def test_empty_dataset():
    assert apply_where([], "price>100") == []


def test_malformed_expression():
    with pytest.raises(ValueError, match="Некорректное выражение"):
        apply_where(ROWS, "badexpr")

# ---------------------------------------------------------------------------
# Дополнительная ветка: неизвестный оператор внутри compare_numeric
# ---------------------------------------------------------------------------


def test_unknown_operator_branch():
    """Обходим регэксп и вызываем _make_comparator напрямую."""
    comp = filters._make_comparator("^", "123")  # op '^' недопустим
    with pytest.raises(ValueError, match="Неизвестный оператор"):
        comp("1", "2")