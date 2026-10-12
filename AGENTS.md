# Daychi Knowledge

Работать с оцифровкой и редакционным пайплайном здесь, а не в Daychi.
Перед работой прочитать README.md, docs/wiki-production-pipeline.md,
docs/wiki-contributor-pipeline.md, docs/wiki-team-pipeline.md и docs/wiki-work-plan.md.
Сначала выполнить docs/collaboration-workflow.md: свежая очередь, координаторское
резервирование, независимый review и одна финальная приёмка.
Смысловые страницы также требуют docs/wiki-semantic-pipeline.md.

- Git хранит инструменты, документацию и синтетические fixtures. Не коммитить
  корпус, расшифровки, реестр, рабочие базы, receipts, сессии и credentials.
- Основной реестр — приватный `data/wiki-workspace/outputs/2026-10-02/wiki-materials.xlsx`.
  Объединять по стабильным ID, сохранять исходные периоды, назначения и правки.
- После партии обновлять docs/wiki-work-plan.md: выполнено/осталось, фактическое
  время, доступный usage, оценки и следующий объём. Не переписывать прошлые факты.
- Редактор и проверяющий независимы. Данные и импорт остаются у координатора.
  Не приписывать слушание, измеренную точность или одобрение преподавателя.
- Не начинать работу из старого прогресса/PR. Нужен coordinator-issued assignment_id;
  не создавать свой авторитетный журнал. Финальный ответственный сейчас sleontenko.
  SQLite хранит новые резервирования и решения, XLSX остаётся каталогом/ручным реестром.
- Не освобождать занятые задачи по таймауту. accepted не означает published;
  --apply требует отдельного разрешения, accepted hash и publication QA после receipt.
- Приложение, сайт, reader/граф и серверный API принадлежат `sleontenko/daychi`.
  Форматы импорта определены в docs/daychi-content-contract.md.
- Любые production imports, deploy и releases требуют отдельного явного разрешения.
  Разделение репозиториев не является таким разрешением.
- Перед commit/push проверить git status, staged diff и scripts/check_repository.py.
  PR title/body — на английском. Тесты: `python -m pytest -q`.
- Не копировать server/storage в этот репозиторий. Изменения wire contract
  согласовывать с Daychi, сохраняя совместимость действующей версии.

## Workshop collaboration

Use [.agents/skills/collaborate/SKILL.md](.agents/skills/collaborate/SKILL.md)
at session startup, before boundary changes, and when coordinating with Workshop.
Daychi Knowledge is a separate Workshop participant addressed as `project:knowledge`.
Existing inspected boundary: Knowledge prepares and imports source-bound content
packages into Daychi's provider-owned content, semantic-content and article operations.
Knowledge owns source preparation, editorial review and its gated import tools;
Daychi owns the API, persisted content, access control and readers.
Local context: `scripts/wiki_enrichment_import.py`, `scripts/wiki_semantic_import.py`,
`scripts/wiki_article_import.py`, `daychi_contracts/` and `contracts/`;
provider definitions are referenced by `docs/daychi-content-contract.md` and
`docs/daychi-article-contract.md`.
Content/semantics v1 remain active. Structured-article acceptance remains in
[Workshop issue 9](https://github.com/dveyarangi/xuanxue-workshop/issues/9).
See [accepted roles](https://github.com/dveyarangi/xuanxue-workshop/blob/8d4def164131c3f8fe737548b888643551b3a004/docs/boundaries.md#accepted-knowledge-responsibility-boundary)
and [scoped evidence](https://github.com/dveyarangi/xuanxue-workshop/blob/8d4def164131c3f8fe737548b888643551b3a004/docs/current-system.md#knowledge-reception-evidence--inspected-2026-10-12).
Cabinet/native application work remains separately addressed to its responsible projects.
