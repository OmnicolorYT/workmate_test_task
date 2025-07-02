"""Загрузчик CSV‑файлов для **csvtool**.

Модуль читает весь файл в память и возвращает список словарей. Ключи —
названия колонок из первой строки (заголовка). Преобразование типов не
выполняется.
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import List, Dict, Optional

__all__ = ["load_csv"]


class CSVLoaderError(Exception):
    """Базовая ошибка при чтении CSV."""


def load_csv(path: Optional[Path], encoding: str = "utf-8") -> List[Dict[str, str]]:
    """Считывает *весь* CSV‑файл и возвращает данные.

    Параметры
    ---------
    path : Path | str
        Путь к файлу CSV.
    encoding : str, default «utf‑8»
        Кодировка файла.

    Возвращает
    ----------
    List[Dict[str, str]]
        Список строк, где каждая строка представлена словарём
        «имя_колонки → значение».

    Исключения
    ----------
    FileNotFoundError
        Файл не найден.
    CSVLoaderError
        Формат CSV нарушен либо отсутствует строка‑заголовок.
    """
    csv_path = Path(path)
    if not csv_path.is_file():
        raise FileNotFoundError(path)

    try:
        with csv_path.open(newline="", encoding=encoding) as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames is None:
                raise CSVLoaderError("CSV-файл без заголовка не поддерживается.")
            rows: List[Dict[str, str]] = list(reader)
    except csv.Error as exc:
        raise CSVLoaderError(f"Ошибка CSV: {exc}") from exc

    return rows
