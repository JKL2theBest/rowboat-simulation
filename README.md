# Rowboat Simulation API

Проект представляет собой API для симуляции управления вёсельной лодкой, написанный на Python, с полным набором автотестов на `pytest`.

```
├── rowboat/
│ ├── init.py
│ ├── models.py
│ └── exceptions.py
├── tests/
│ ├── init.py
│ └── test_rowboat.py
├── pyproject.toml
├── README.md
└── testcases.md
```

## Установка и запуск

**Требования:**
*   Python 3.10+

---

**Шаг 1**
```bash
git clone https://github.com/JKL2theBest/rowboat-simulation/
cd rowboat-simulation
```

**Шаг 2: Создать и активировать виртуальное окружение (рекомендуется)**
```bash
# Для Linux / macOS
python3 -m venv venv
source venv/bin/activate
```
```bash
# Для Windows
python -m venv venv
venv\Scripts\activate
```

**Шаг 3: Установить проект и зависимости для разработки**

Команда установит `pytest`.
```bash
pip install -e .[dev]
```

**Шаг 4: Запустить тесты**

Чтобы убедиться, что всё работает корректно, запустите полный набор тестов:
```bash
pytest -v
```
Вы должны увидеть, что все тесты успешно пройдены.

Подробные тест-кейсы, разработанные для этого проекта (функциональные, интеграционные, системные), находятся в файле `testcases.md`.
