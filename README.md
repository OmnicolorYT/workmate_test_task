# csvtool

CLI-утилита:  
* **Фильтрация** — `--where "column<value|>value|=value"`  
* **Агрегация** — `--aggregate "column=min|max|avg"`

## Установка
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Использование
```bash
# отфильтровать строки
python -m csvtool data.csv --where "price>300"

# среднее значение колонки после фильтра
python -m csvtool data.csv --where "brand=apple" --aggregate "rating=avg"
```

## Примеры
```bash
python -m csvtool products.csv --where "brand=apple"
python -m csvtool products.csv --where "brand=samsung" --aggregate "price=avg"
python -m csvtool products.csv --where "price<400" --aggregate "rating=max"
python -m csvtool products.csv --where "price>300" --where "price<800"
python -m csvtool products.csv --where "brand=xiaomi" --aggregate "price=min"
python -m csvtool products.csv --aggregate "rating=avg"
python -m csvtool products.csv --where "brand=apple" --aggregate "price=max"
python -m csvtool products.csv --where "rating>4.5"
```

## Тесты
```bash
pytest -q                          # все тесты
pytest --cov=csvtool --cov=tests   # покрытие
```