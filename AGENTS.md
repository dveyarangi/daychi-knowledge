# Daychi Knowledge

Работать с оцифровкой и редакционным пайплайном здесь, а не в Daychi.
Перед работой прочитать README.md, docs/wiki-production-pipeline.md,
docs/wiki-contributor-pipeline.md, docs/wiki-team-pipeline.md и docs/wiki-work-plan.md.
Смысловые страницы также требуют docs/wiki-semantic-pipeline.md.

- Git хранит инструменты, документацию и синтетические fixtures. Не коммитить
  корпус, расшифровки, реестр, рабочие базы, receipts, сессии и credentials.
- Основной реестр — приватный `data/wiki-workspace/outputs/2026-10-02/wiki-materials.xlsx`.
  Объединять по стабильным ID, сохранять исходные периоды, назначения и правки.
- После партии обновлять docs/wiki-work-plan.md: выполнено/осталось, фактическое
  время, доступный usage, оценки и следующий объём. Не переписывать прошлые факты.
- Редактор и проверяющий независимы. Данные и импорт остаются у координатора.
  Не приписывать слушание, измеренную точность или одобрение преподавателя.
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
This is Daychi's knowledge track; retain `project:daychi`, not a new recipient label.
Existing: knowledge pipeline prepares v1 JSON batches for Daychi's existing owner
content import endpoints. Daychi owns content delivery, public/private access,
its clients and Cabinet integration. The retained content API remains in Daychi.
No Cabinet migration, deployment or publication is authorized by this split.
