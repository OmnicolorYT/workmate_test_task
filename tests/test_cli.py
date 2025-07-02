"""Интеграционные тесты CLI-интерфейса csvtool."""
from typing import List, Dict

import pytest

import csvtool.cli as cli

# ---------------------------------------------------------------------------
# Вспомогательные объекты
# ---------------------------------------------------------------------------


SAMPLE_ROWS: List[Dict[str, str]] = [
    {"price": "100", "brand": "alpha"},
    {"price": "200", "brand": "beta"},
]


# ---------------------------------------------------------------------------
# Позитивные сценарии
# ---------------------------------------------------------------------------


def test_success_render_rows(monkeypatch):
    """Без --aggregate выводятся строки (ветка render_rows)."""

    # Заглушаем load_csv
    monkeypatch.setattr(cli, "load_csv", lambda path: SAMPLE_ROWS)

    # Отлавливаем вызов render_rows
    called = {}

    def fake_render_rows(rows):
        called["rows"] = rows

    monkeypatch.setattr(cli, "render_rows", fake_render_rows)

    # Запускаем main
    cli.main(["file.csv"])

    assert called["rows"] == SAMPLE_ROWS  # render_rows вызван с теми же данными


def test_success_aggregate(monkeypatch):
    """С --aggregate должен вызываться render_aggregate без ошибок."""

    monkeypatch.setattr(cli, "load_csv", lambda path: SAMPLE_ROWS)

    # Используем реальную apply_aggregate, поэтому укажем существующую функцию

    captured = {}

    def fake_render_aggregate(result):
        captured["result"] = result

    monkeypatch.setattr(cli, "render_aggregate", fake_render_aggregate)

    cli.main(["file.csv", "--aggregate", "price=max"])

    assert captured["result"]["value"] == "200"


# ---------------------------------------------------------------------------
# Ошибки при загрузке CSV
# ---------------------------------------------------------------------------


def test_file_not_found(monkeypatch, capsys):
    """FileNotFoundError -> exit code 1."""

    def raise_fn(path):
        raise FileNotFoundError

    monkeypatch.setattr(cli, "load_csv", raise_fn)

    with pytest.raises(SystemExit) as exc:
        cli.main(["missing.csv"])

    assert exc.value.code == 1
    err = capsys.readouterr().err
    assert "Файл не найден" in err


def test_generic_loader_error(monkeypatch, capsys):
    """Любая другая ошибка чтения CSV -> exit code 1."""

    def raise_fn(path):
        raise RuntimeError("boom")

    monkeypatch.setattr(cli, "load_csv", raise_fn)

    with pytest.raises(SystemExit) as exc:
        cli.main(["broken.csv"])

    assert exc.value.code == 1
    err = capsys.readouterr().err
    assert "Ошибка чтения CSV" in err and "boom" in err


# ---------------------------------------------------------------------------
# Ошибки фильтрации и агрегации
# ---------------------------------------------------------------------------


def test_filter_error(monkeypatch, capsys):
    """apply_where выдаёт ValueError -> exit code 2."""

    monkeypatch.setattr(cli, "load_csv", lambda path: SAMPLE_ROWS)

    def raise_filter(rows, expr):  # noqa: D401, ANN001
        raise ValueError("bad where")

    monkeypatch.setattr(cli, "apply_where", raise_filter)

    with pytest.raises(SystemExit) as exc:
        cli.main(["file.csv", "--where", "bad"])

    assert exc.value.code == 2
    err = capsys.readouterr().err
    assert "Ошибка фильтрации" in err


def test_aggregate_error(monkeypatch, capsys):
    """apply_aggregate выдаёт ValueError -> exit code 2."""

    monkeypatch.setattr(cli, "load_csv", lambda path: SAMPLE_ROWS)

    def raise_agg(rows, expr):  # noqa: D401, ANN001
        raise ValueError("bad agg")

    monkeypatch.setattr(cli, "apply_aggregate", raise_agg)

    with pytest.raises(SystemExit) as exc:
        cli.main(["file.csv", "--aggregate", "something=bad"])

    assert exc.value.code == 2
    err = capsys.readouterr().err
    assert "Ошибка агрегации" in err
