"""Полный набор тестов для модуля csvtool.aggregators.
"""
from decimal import Decimal

import pytest

from csvtool.aggregators import (
    apply_aggregate,
    AggregationError,
    _Min,
    _Max,
    _Avg,
)

# ---------- Позитивные сценарии -------------------------------------------------


@pytest.mark.parametrize(
    "func, expected",
    [("min", "50"), ("max", "200")],
)
def test_min_max(func, expected):
    """Проверяем корректность min/max при обычном наборе данных."""
    rows = [{"price": "100"}, {"price": "200"}, {"price": "50"}]
    result = apply_aggregate(rows, f"price={func}")
    assert result["value"] == expected


def test_avg():
    """Проверяем вычисление среднего значения (avg)."""
    rows = [{"price": "100"}, {"price": "200"}, {"price": "50"}]
    result = apply_aggregate(rows, "price=avg")

    value = Decimal(result["value"])
    expected = Decimal("116.6666666666666666666667")  # 350 / 3
    assert abs(value - expected) < Decimal("1e-6")


# ---------- Исключения в apply_aggregate ---------------------------------------


@pytest.mark.parametrize(
    "expr, exc_pattern",
    [
        ("price=sum", r"Неизвестная функция"),
        ("price>max", r"Некорректное выражение"),
    ],
)
def test_invalid_expression(expr, exc_pattern):
    rows = [{"price": "1"}]
    with pytest.raises(AggregationError, match=exc_pattern):
        apply_aggregate(rows, expr)


def test_non_numeric_value():
    rows = [{"price": "foo"}]
    with pytest.raises(AggregationError, match=r"числовые колонки"):
        apply_aggregate(rows, "price=min")


def test_column_not_found():
    rows = [{"value": "10"}]
    with pytest.raises(AggregationError, match=r"Колонка 'price'"):
        apply_aggregate(rows, "price=max")


def test_no_rows():
    with pytest.raises(AggregationError, match="Нет строк для агрегации"):
        apply_aggregate([], "price=min")


# ---------- Исключения внутри классов‑агрегаторов ------------------------------


@pytest.mark.parametrize(
    "agg_cls, msg_part",
    [(_Min, "min"), (_Max, "max"), (_Avg, "avg")],
)
def test_aggregator_no_data(agg_cls, msg_part):
    """Метод .result() без предварительного combine() должен бросать ошибку."""
    aggregator = agg_cls()
    with pytest.raises(AggregationError, match=f"Нет данных для вычисления {msg_part}"):
        aggregator.result()
