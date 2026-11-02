# Quickstart

## Prerequisites

- Python 3.11+.
- Windows PowerShell or Linux shell.
- Virtual environment in repository root.
- Credentials in `noselenium/.env`; never print or commit it.
- Keep `DRY_RUN=true`.

## Windows

```powershell
.\venv\Scripts\Activate.ps1
python -m pytest -q
python -m src.main --once --dry-run
```

## Linux

```bash
source venv/bin/activate
python -m pytest -q
python -m src.main --once --dry-run
```

## Offline validation

Use fixture responses and fake clock to test:

1. Active construction blocks a second construction.
2. Lowest-level payable building wins, preserving server order on ties.
3. Resource wait respects production and storage capacity.
4. Farm cycle sends only eligible five-minute collections.
5. One farm failure does not stop other farms.
6. State survives restart and does not repeat confirmed actions.
7. `DRY_RUN=true` emits planned actions but sends no mutation request.

## Controlled live validation

1. Set `DRY_RUN=true`.
2. Start the bot and confirm read-only login, Backbone and scheduling logs.
3. Inspect planned building and farm actions without enabling writes.
4. Enable writes only after reviewing persisted state and logs.
5. Run one controlled construction and one controlled five-minute collection.
6. Verify server queue, `lootable_at`, logs and state JSON.
7. Restore `DRY_RUN=true`.

Expected result: each invocation checks due tasks, schedules the exact next run, exits, and never exposes secrets in logs. Install the first trigger with `python -m src.main --install-scheduler`.

For detailed diagnostics, add `--logs`:

```powershell
python -m src.main --logs --dry-run
```
