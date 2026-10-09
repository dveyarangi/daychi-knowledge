# Contributing

Start with [AGENTS.md](AGENTS.md) and the
[collaboration workflow](docs/collaboration-workflow.md), for humans and agents.

For content, request a coordinator-issued private assignment. Do not choose a
source from historical totals, publish a corpus in a PR, or create another
authoritative register. Independent review and final operator acceptance are
required; a merged code PR does not accept or publish a content batch.

For tools and protocol changes, use a branch and an English PR title/body.
Describe the trigger, resulting behavior and checks actually run. Keep fixtures
synthetic. Run `python -m pytest -q`, `python scripts/check_repository.py --staged`
and `git diff --cached --check`. Retain existing Daychi v1 payloads and IDs.

Do not claim audio listening, measured ASR accuracy, teacher approval, UI checks
or production publication without their evidence. Coordinate incompatible
contract changes with Daychi before implementation.
