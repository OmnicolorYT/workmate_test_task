"""Вспомогательные функции вывода для csvtool."""
from __future__ import annotations

from typing import Iterable, Dict, List, Any

from tabulate import tabulate

__all__ = ["render_rows", "render_aggregate"]


def _safe_print(table: str) -> None:
    """Печатает table, корректно обрабатывая терминалы без UTF‑8."""
    try:
        print(table)
    except UnicodeEncodeError:
        print(table.encode("ascii", errors="replace").decode())


def render_rows(rows: Iterable[Dict[str, Any]]) -> None:
    """Отображает список строк rows как таблицу."""
    rows_list: List[Dict[str, Any]] = list(rows)
    if not rows_list:
        print("[csvtool] Результат пуст.".center(60, "-"))
        return

    table = tabulate(
        rows_list,
        headers="keys",  # брать заголовки из ключей словаря
        tablefmt="github",
        stralign="left",
        numalign="right",
    )
    _safe_print(table)


def render_aggregate(result: Dict[str, str]) -> None:
    """Отображает результат агрегации."""
    table = tabulate(
        [[result["column"], result["function"], result["value"]]],
        headers=["column", "function", "value"],
        tablefmt="github",
        stralign="left",
        numalign="right",
    )
    _safe_print(table)
