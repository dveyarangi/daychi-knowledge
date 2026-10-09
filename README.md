# Daychi Knowledge

Приватный проект подготовки знаний школы: источники, оцифровка, расшифровки,
конспекты, темы, словарь, редактура и независимая проверка.

Приложение, сайт, интерфейс вики и серверный API находятся в
[Daychi](https://github.com/sleontenko/daychi). Этот репозиторий готовит пакеты
для существующего API; отдельный сервер и новый API не вводятся.

## Начало работы

```sh
git clone https://github.com/sleontenko/daychi-knowledge.git
cd daychi-knowledge
python3.12 -m venv .venv
.venv/bin/python -m pip install -e '.[test]'
.venv/bin/python -m pytest -q
.venv/bin/python scripts/check_repository.py
```

Для существующих команд сохранён namespace `scripts.*`: запускать их из корня
этого репозитория. Команды и протоколы — в [процессе](docs/wiki-production-pipeline.md),
[инструкции участника](docs/wiki-contributor-pipeline.md),
[реестре](docs/wiki-team-pipeline.md), [плане](docs/wiki-work-plan.md)
и [семантическом протоколе](docs/wiki-semantic-pipeline.md).
Модели ASR устанавливаются отдельно по `scripts/wiki-pipeline-requirements.txt`
в существующее совместимое окружение Apple Silicon. Обычные тесты их не требуют.

## Данные и публикация

`data/` — локальная приватная рабочая область, исключённая из Git вместе с
аудио, видео, PDF, Excel, SQLite, receipts и credentials. Git хранит код,
протоколы и синтетические тесты; приватность репозитория не отменяет это правило.
Основной реестр — `data/wiki-workspace/outputs/2026-10-02/wiki-materials.xlsx`.
Не создавать второй авторитетный реестр и не пересобирать поверх ручных правок.

Координатор выдаёт задания, принимает независимый review, валидирует и импортирует
пакет. `--apply` означает запись на сервер и требует разрешения на конкретную
партию. Сам перенос репозитория не разрешает новый production-импорт.
Конспекты сохраняют статус `source_checked_draft`; он не означает одобрения
преподавателем. Редакторам не нужны административные credentials.

## Граница с Daychi

[Контракт v1](docs/daychi-content-contract.md) сохраняет ID, revisions, hashes,
статусы, payload и owner endpoints. Локальные модели в `daychi_contracts/`
не зависят от `practice_api`; сервер остаётся авторитетным валидатором.
[Запись переноса](docs/repository-migration-2026-10-09.md) и
`migration/source-manifest.json` фиксируют происхождение файлов, в том числе
сохранённые незакоммиченные изменения. История исходного репозитория не переписана.
