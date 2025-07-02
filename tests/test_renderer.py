"""Тесты для модуля csvtool.renderer"""
from typing import List, Dict, Any

import csvtool.renderer as renderer


# ---------------------------------------------------------------------------
# render_rows — обычный вывод
# ---------------------------------------------------------------------------

def test_render_rows_normal(capsys):
    rows: List[Dict[str, Any]] = [
        {"price": "100", "brand": "alpha"},
        {"price": "200", "brand": "beta"},
    ]

    renderer.render_rows(rows)
    out = capsys.readouterr().out
    # Проверяем, что вывод содержит заголовки и значения
    assert "price" in out and "brand" in out and "200" in out


# ---------------------------------------------------------------------------
# render_rows — пустой набор данных
# ---------------------------------------------------------------------------

def test_render_rows_empty(capsys):
    renderer.render_rows([])
    out = capsys.readouterr().out
    assert "Результат пуст" in out


# ---------------------------------------------------------------------------
# render_aggregate
# ---------------------------------------------------------------------------

def test_render_aggregate(capsys):
    result = {"column": "price", "function": "max", "value": "200"}
    renderer.render_aggregate(result)
    out = capsys.readouterr().out
    assert "price" in out and "max" in out and "200" in out
