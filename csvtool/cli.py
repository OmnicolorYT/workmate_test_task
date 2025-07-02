"""Command‑line интерфейс для csvtool.

Пример использования:
    $ python -m csvtool data.csv --where "price>300" --aggregate "rating=avg"
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

from csvtool.loader import load_csv
from csvtool.filters import apply_where
from csvtool.aggregators import apply_aggregate
from csvtool.renderer import render_rows, render_aggregate


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="csvtool",
        description="Filter and aggregate CSV files from the command line.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument("csv_file", type=Path, help="Путь к CSV‑файлу для обработки.")

    parser.add_argument(
        "--where",
        metavar="EXPR",
        action="append",
        help=(
            "Условие фильтрации вида 'column<value', 'column>value' или 'column=value'. "
            "Можно передавать несколько --where для объединения AND‑логикой."
        ),
    )

    parser.add_argument(
        "--aggregate",
        metavar="EXPR",
        help=(
            "Агрегация вида 'column=function', где function = avg | min | max."
            "Если флаг не указан — выводятся отфильтрованные строки."
        ),
    )

    # TODO здесь можно добавить новую команду по аналогии с двумя предыдущими

    return parser


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    """Парсинг аргументов с возможностью передачи списка из тестов."""
    parser = _build_parser()
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> None:
    """Точка входа"""
    args = parse_args(argv)

    # Загрузка данных
    try:
        rows = load_csv(args.csv_file)
    except FileNotFoundError:
        print(f"[csvtool] Файл не найден: {args.csv_file}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"[csvtool] Ошибка чтения CSV: {exc}", file=sys.stderr)
        sys.exit(1)

    # Фильтрация
    if args.where:
        for expr in args.where:
            try:
                rows = apply_where(rows, expr)
            except ValueError as exc:
                print(f"[csvtool] Ошибка фильтрации: {exc}", file=sys.stderr)
                sys.exit(2)

    # TODO здесь можно добавить обработку новых команд (до агрегации)

    # Агрегация или вывод строк
    if args.aggregate:
        try:
            result = apply_aggregate(rows, args.aggregate)
            render_aggregate(result)
        except ValueError as exc:
            print(f"[csvtool] Ошибка агрегации: {exc}", file=sys.stderr)
            sys.exit(2)
    else:
        render_rows(rows)

if __name__ == "__main__":
    main()
