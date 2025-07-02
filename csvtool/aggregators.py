"""Утилиты агрегации для csvtool."""
from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from statistics import mean
from typing import Iterable, List, Optional

__all__ = ["apply_aggregate"]

_AGG_RE = re.compile(r"(?P<column>[\w\s]+)=(?P<func>\w+)")


class AggregationError(ValueError):
    """Ошибки вычисления агрегаций."""


class _Aggregator:
    """Базовый агрегатор.

    В дочерних классах должны быть реализованы .combine(value) и .result() методы.
    """

    name: str

    def combine(self, value: Decimal) -> None:
        raise NotImplementedError

    def result(self) -> Decimal:
        """Возвращает результат агрегации."""
        raise NotImplementedError


class _Min(_Aggregator):
    name = "min"

    def __init__(self) -> None:
        self._min: Optional[Decimal] = None

    def combine(self, value: Decimal) -> None:
        self._min = value if self._min is None or value < self._min else self._min

    def result(self) -> Decimal:
        if self._min is None:
            raise AggregationError("Нет данных для вычисления min.")
        return self._min


class _Max(_Aggregator):
    name = "max"

    def __init__(self) -> None:
        self._max: Optional[Decimal] = None

    def combine(self, value: Decimal) -> None:
        self._max = value if self._max is None or value > self._max else self._max

    def result(self) -> Decimal:
        if self._max is None:
            raise AggregationError("Нет данных для вычисления max.")
        return self._max


class _Avg(_Aggregator):
    name = "avg"

    def __init__(self) -> None:
        self._values: List[Decimal] = []

    def combine(self, value: Decimal) -> None:
        self._values.append(value)

    def result(self) -> Decimal:
        if not self._values:
            raise AggregationError("Нет данных для вычисления avg.")
        return Decimal(str(mean(self._values)))


# TODO если нужно добавить новый агрегатор - его необходимо вписать в кортеж
#  (предварительно создав дочерний класс от агрегатора с реализацией необходимого функционала)
_AGGREGATORS = {cls.name: cls for cls in (_Min, _Max, _Avg)}


def _to_decimal(value: str) -> Decimal:
    try:
        cleaned = value.replace(",", ".")
        return Decimal(cleaned)
    except InvalidOperation:
        raise AggregationError(
            "Агрегировать можно только числовые колонки. Обнаружено строковое значение."
        ) from None


def apply_aggregate(rows: Iterable[dict[str, str]], expr: str) -> dict[str, str]:
    """Производит агрегацию над rows в соответствии с expr.

    Параметры
    ----------
    rows: iterable
        Входные строки (могут быть уже отфильтрованы).
    expr: str
        Выражение "column=function" где функция является avg | min | max.

    Возвращает
    -------
    dict[str, str]
        Словарь с ключами: column, function, value.
    """
    m = _AGG_RE.fullmatch(expr.strip())
    if not m:
        raise AggregationError("Некорректное выражение --aggregate. Ожидается 'column=function'.")

    column = m.group("column").strip()
    func_name = m.group("func").lower()

    try:
        agg_cls = _AGGREGATORS[func_name]
    except KeyError:
        raise AggregationError(f"Неизвестная функция агрегации '{func_name}'.") from None

    aggregator: _Aggregator = agg_cls()

    processed_any = False
    for row in rows:
        try:
            value = _to_decimal(row[column])
        except KeyError:
            raise AggregationError(f"Колонка '{column}' не найдена в CSV.") from None
        aggregator.combine(value)
        processed_any = True

    if not processed_any:
        raise AggregationError("Нет строк для агрегации.")

    result_value = aggregator.result()
    return {"column": column, "function": func_name, "value": str(result_value)}
