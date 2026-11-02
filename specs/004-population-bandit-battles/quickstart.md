# Quickstart

## Prerequisites

- Python 3.11+.
- Existing `venv` and dependencies installed.
- `DRY_RUN=true` during research.
- Authenticated DevTools session only when capturing contracts.

## Offline validation

```powershell
.\venv\Scripts\python.exe -m pytest -q
```

Validate:

1. Population zero selects farm only when valid.
2. Queue never exceeds server capacity two.
3. Resource reservations account for earlier planned orders.
4. Cooldown values come from target state.
5. Missing enemy data blocks battle.
6. Loss, draw, incomplete simulation and duplicate movement block sending.
7. Reward collection is idempotent after restart.

## DevTools research gate

1. Keep session authenticated in POROS.
2. Open the bandit target and simulator.
3. Capture read-only simulator and target requests.
4. Record method, URL, field names, response keys and server timestamps.
5. Perform no live troop dispatch until contracts are reviewed.

## Controlled live validation

1. Keep `DRY_RUN=true`.
2. Validate unit counts, target, cooldown and reward metadata.
3. Enable writes only after simulator and dispatch contracts are documented.
4. Send one controlled battle.
5. Verify arrival, result and reward state.
6. Restore `DRY_RUN=true`.
