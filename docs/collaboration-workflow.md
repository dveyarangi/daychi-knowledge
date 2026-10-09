# Работа с знаниями · протокол 1

Это точка входа для человека, Claude и Codex. Читать также AGENTS.md,
[протокол участника](wiki-contributor-pipeline.md),
[редакционный процесс](wiki-production-pipeline.md) и
[правила реестра](wiki-team-pipeline.md). Для тем/словаря —
[семантический протокол](wiki-semantic-pipeline.md).

## Первые действия агента

1. Обновить checkout, прочитать инструкции и проверить git status. Старые PR и
   таблицы прогресса описывают прошлые снимки, а не свободные задания сегодня.
2. Получить у координатора актуальную очередь и зарезервированный пакет с
   `assignment_id`, `batch_id`, стабильными ID, revisions и hashes источников.
   Без подтверждённого резервирования не начинать редактуру или новую статью.
3. Проверить свою роль, объём и доступность полного источника. Если назначения,
   версия или источник расходятся — вернуть blocked с причиной, не выбирать замену.
4. Выполнить только назначенную работу, вернуть результат и evidence; указать
   выполненные/невыполненные проверки, фактическое время и доступный usage.
5. Другой проверяющий проверяет полный источник и именно hash итогового результата.
   Финальная приёмка остаётся у одного ответственного: сейчас `sleontenko`.
6. После приёмки публикацию выполняет координатор по отдельному разрешению на
   конкретный пакет. Участник не получает owner credentials.

PR с кодом/документацией и приёмка содержимого — разные события. Конспекты,
расшифровки, назначения и результаты передаются приватными пакетами вне Git.

## Где находится актуальное состояние

| Данные | Авторитет и доступ |
|---|---|
| Идентичность источника, исходный период, ручные примечания, прежние назначения | Приватный XLSX `data/wiki-workspace/outputs/2026-10-02/wiki-materials.xlsx` |
| Новые резервирования, review, приёмка, разрешение публикации, журнал событий | Одна приватная SQLite `data/wiki-workspace/coordinator/workflow.sqlite3` на хосте координатора |
| Что действительно опубликовано | Действующий Daychi API; receipts плюс проверка DTO |
| Протокол, инструменты, тесты, исторические QA, сводный снимок | Этот Git-репозиторий |

SQLite — журнал выполнения и блокировок, не второй каталог. Команды читают XLSX,
не сохраняют и не пересобирают его. Новые резервирования ведутся в журнале;
ручное назначение в XLSX блокирует автоматическую выдачу до согласования.
После завершения координатор объединяет факты в прежний XLSX по стабильным ID,
сохраняя ручные поля, периоды, формулы, validation и историю. Самостоятельные
копии SQLite на компьютерах участников не дают права брать задания.

Read-only snapshot сверяет каждую карточку действующего каталога с реестром.
Он действует максимум 24 часа. Изменение XLSX, неполный API ответ, расхождение
импорта или недоступный сервер требуют новой сверки. Snapshot не является
долгосрочной гарантией неизменности сервера: перед приёмкой и публикацией
координатор повторяет сверку. При offline новое задание не выдаётся.

Public DTO подтверждает наличие конспекта, source ID и revision. Он очищает
содержимое; точное совпадение приватного payload и UI-проверку он не доказывает.
Для публикационной QA нужен авторизованный reader DTO и сохранённые доказательства.

## Роли и приёмка

Редактор и проверяющий имеют разные идентификаторы. Проверяющий читает полный
источник, проверяет каждое утверждение, точность цитат, таймкоды, quarantine,
язык, ограничения и покрытие. Одних тестов, brief summary или просмотра отрывков
недостаточно. pass ссылается на `result_sha256`; изменение результата отменяет review.

Ответственный за финальную приёмку проверяет покрытие, независимость review,
source/provenance hashes, валидность пакета и явно фиксирует решение для его hash.
Сейчас это человек-владелец. Приёмка не даёт разрешения на production-импорт.
Будущий агент-приёмщик получит полномочия только после отдельного решения,
версионированных критериев и изменения назначения; текущие агенты их не наследуют.

CLI `--actor` — метка аудита, не авторизация. SQLite и команды мутации доступны
только координатору через существующие права на хосте; участники возвращают
файлы, а координатор проверяет происхождение решений. Не выдавать им writable
доступ к журналу или owner-сессии. Это локальный протокол, не новый web-сервис.

## Статусы

| Статус | Значение и следующий шаг |
|---|---|
| available | Допущена к выдаче; резервирование ещё обязательно |
| blocked | Источник/доступ/назначение/привязка расходятся; причина обязательна |
| claimed | Зарезервирована одной парой editor/reviewer |
| submitted | Итоговый результат и его hash зафиксированы |
| needs_changes | Вернуть назначенному редактору, затем новый независимый review |
| review_pass | Независимый review пройден; ожидается финальный ответственный |
| accepted | Ответственный принял конкретный hash; публикация ещё не разрешена |
| publishing | Запись на сервер начата; повтор/освобождение запрещены до сверки |
| imported | Есть receipt; полная публикационная QA ещё не завершена |
| verified | QA завершена, реестр обновлён; результат пригоден для следующего этапа |
| published_existing | Уже на сервере до введения журнала; не импортировать повторно |
| released | Ответственный снял назначение с причиной; новый snapshot нужен до выдачи |

Отдельные виды работ: `prepare` — доступ/скачивание/текст/ASR/привязка;
`summary` — конспект; `review` — независимая проверка уже опубликованного;
`semantic` — страницы тем/словаря. При отсутствии проверенного текста адаптер
создаёт prepare, даже если название кажется пригодным для статьи.

Нет автоматического освобождения по таймауту: агент мог продолжать работать.
Задача определяется canonical target, видом работы и revision. Все источники
одной карточки согласуются до выдачи summary; активная revision блокирует другие.
Для терминов координатор сверяет существующие canonical concept_id и aliases
до назначения. Название не служит идентификатором.

## Команды координатора

Все рабочие переменные задаются локально. `$WIKI_WORKFLOW_DB`, `$WIKI_REGISTRY`,
`$WIKI_SNAPSHOT`, `$WIKI_PACKET`, `$WIKI_RESULT`, `$WIKI_REVIEW` и `$WIKI_RECEIPT`
должны указывать в приватную область `data/`. Секреты передаются только файлом.

```sh
python -m scripts.wiki_workflow --db "$WIKI_WORKFLOW_DB" init --acceptor sleontenko
python -m scripts.wiki_workflow_snapshot --registry "$WIKI_REGISTRY" --output "$WIKI_SNAPSHOT"
python -m scripts.wiki_workflow --db "$WIKI_WORKFLOW_DB" sync --snapshot "$WIKI_SNAPSHOT" --actor coordinator
python -m scripts.wiki_workflow --db "$WIKI_WORKFLOW_DB" status
python -m scripts.wiki_workflow --db "$WIKI_WORKFLOW_DB" queue --state available
python -m scripts.wiki_workflow --db "$WIKI_WORKFLOW_DB" claim \
  --task '<task ID from current queue>' --editor '<editor>' --reviewer '<different reviewer>' \
  --batch-id '<unique batch>' --actor coordinator --output "$WIKI_PACKET"
```

`init` выполняется однажды. Одновременные claim сериализуются `BEGIN IMMEDIATE`;
при занятой задаче вся заявка отклоняется. Packet дополняет прежний source packet,
не заменяет полные тексты, segments, ASR diagnostics и quarantine.

После принятой prepare координатор дополняет XLSX без перезаписи ручных правок.
Готовность summary вводится приватным intake JSON: `summaries` с `source_task_id`,
`source_fingerprint` из свежей очереди, `target`, `revision: 1`,
`full_text_available: true` и `ready_evidence` (пути и hashes полных текстов,
привязки и проверки доступа). Новый snapshot запускается с `--intake <file>`.
Адаптер требует единственной текущей каталожной привязки; совпадение названий
не принимается. Исправления требуют отдельного согласования следующей revision;
автоматический initial intake их не создаёт. Для semantic координатор готовит
нормализованное задание по семантическому протоколу после сверки текущих страниц,
aliases и всех source revisions; при выключенном/недоступном API выдача заблокирована.

```sh
python -m scripts.wiki_workflow --db "$WIKI_WORKFLOW_DB" submit \
  --assignment "$WIKI_ASSIGNMENT" --actor "$WIKI_EDITOR" --file "$WIKI_RESULT"
python -m scripts.wiki_workflow --db "$WIKI_WORKFLOW_DB" review \
  --assignment "$WIKI_ASSIGNMENT" --actor "$WIKI_REVIEWER" --file "$WIKI_REVIEW"
python -m scripts.wiki_workflow --db "$WIKI_WORKFLOW_DB" accept \
  --assignment "$WIKI_ASSIGNMENT" --actor sleontenko --reference '<explicit acceptance evidence>'
```

Review JSON содержит `assignment_id`, `result_sha256`, `decision`, `scope`,
`full_source_read` и `evidence` с путями/hashes доказательств. Decision:
pass / needs_changes / blocked. Полное покрытие требуется для pass.
`summary`/`semantic` result — финальный валидированный batch.json;
prepare/review result — приватный отчёт, hash которого фиксируется целиком.

## Публикация и восстановление

```sh
python -m scripts.wiki_workflow --db "$WIKI_WORKFLOW_DB" authorize-publication \
  --assignment "$WIKI_ASSIGNMENT" --actor sleontenko --reference '<permission for this batch>'
python -m scripts.wiki_enrichment_import --batch "$WIKI_RESULT" \
  --apply --password-file "$WIKI_OWNER_PASSWORD_FILE" \
  --workflow-db "$WIKI_WORKFLOW_DB" --assignment "$WIKI_ASSIGNMENT" --receipt "$WIKI_RECEIPT"
```

Для semantic применяется `scripts.wiki_semantic_import` с теми же gate-аргументами.
Без `--apply` прежняя локальная валидация работает без журнала и credentials.
С `--apply` необходимы accepted hash, отдельное разрешение и тот же origin, что
в свежем snapshot. Receipt записывается сразу после первой записи до replay.
Wire payload и серверные API не меняются. Исторические партии не переимпортируются.

После записи координатор сверяет все payload, исходные поля, идемпотентный replay,
anonymous access и авторизованный UI, затем обновляет XLSX. Новый snapshot
обновляет факт publication. `verify --file <QA JSON>` завершает журнал только
при `assignment_id`, `batch_id`, `result_sha256`, `evidence` и true-полях:
`all_payloads_exact`, `source_fields_unchanged`, `idempotent_replay`,
`anonymous_access_checked`, `authorized_ui_checked`, `registry_updated`.
Невыполненная проверка остаётся видимой; не отмечать true по косвенным данным.

При timeout/ошибке publishing остаётся зарезервированным. Ответственный делает
read-only сверку сервера; `reconcile-import --file <report>` требует accepted
hash, evidence и `server_write: present_exact` с receipt либо `absent`.
Неизвестное/конфликтующее состояние остаётся заблокированным. Если записи нет,
разрешение сбрасывается и перед повтором выдаётся новое. `release` не освобождает
publishing/imported/verified; в остальных случаях нужен ответственный и причина.

prepare/review не импортируют новый конспект. После приёмки, обновления XLSX и
сверки `complete --file <report>` фиксирует verified; отчёт содержит
`result_sha256`, `registry_updated: true` и evidence. Проверка старого конспекта
не меняет его текст автоматически; исправление — отдельная revision/приёмка.

## Передача следующему участнику

Сохранять packet, source/provenance hashes, результат, независимый review,
acceptance, permission, receipt и QA вне Git. Обновлять [план](wiki-work-plan.md)
и [статус](wiki-status.md) сводными фактами с датой; не коммитить полный список
задач/источников. Следующий участник получает новую очередь и резервирование,
а не выбирает работу из старой записи в README. PR с кодом проходит CI и
repository guard; финальное решение по содержимому принимает ответственный.
