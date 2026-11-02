---

description: "Task list for portable Grepolis autonomous bot"
---

# Tasks: Bot autonomo de construcciones y aldeas

**Input**: Design documents from `specs/003-grepolis-autonomous-bot/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/observed-http.md`, `quickstart.md`

**Tests**: Required by the feature specification. Write tests before implementation and keep coverage at least 0.80.

**Target**: Windows and Linux. Application code belongs in `src/`; tests belong in `tests/`.

## Phase 1: Setup

**Purpose**: Establish portable project structure and test entry points.

- [X] T001 Create the `src/` package and `tests/unit/`, `tests/contract/`, and `tests/integration/` directories.
- [X] T002 [P] Add portable project configuration and dependency declarations in `requirements.txt` and `src/__init__.py`.
- [X] T003 [P] Add cross-platform test configuration and coverage settings in `pytest.ini`.
- [X] T004 [P] Add environment template with `DRY_RUN=true`, world, town, farm, interval, margin, retry, and state path settings in `.env.example`.

## Phase 2: Foundational

**Purpose**: Blocking infrastructure required by all user stories.

- [X] T005 [P] Implement validated cross-platform settings and `pathlib`-based paths in `src/config.py`.
- [X] T006 [P] Implement secret-safe structured logging and redaction in `src/logging_config.py`.
- [X] T007 [P] Implement atomic versioned JSON persistence with temporary-file replacement in `src/state_store.py`.
- [X] T008 [P] Define shared dataclasses for cities, buildings, orders, farm relations, scheduled tasks, and execution results in `src/models.py`.
- [X] T009 [P] Add deterministic fake-clock and HTTP-response fixtures in `tests/conftest.py`.
- [X] T010 Implement shared retry classification, bounded exponential backoff, and no-retry rules for ambiguous mutations in `src/retry.py`.
- [X] T011 Implement the scheduler core with independent task queues, injected clock, persisted task state, and per-task error isolation in `src/scheduler.py`.
- [X] T012 Add foundational tests for settings validation, redaction, atomic recovery, retry policy, scheduler isolation, and restart restoration in `tests/unit/test_foundation.py`.

**Checkpoint**: Foundation is ready. User stories can proceed independently.

## Phase 3: User Story 1 - Gestionar construcciones (Priority: P1) MVP

**Goal**: Select and schedule at most one valid building expansion using server state, queue completion, resource production, population, dependencies, and storage capacity.

**Independent Test**: Run construction cycles with fixtures for active queues, ties, unaffordable candidates, storage limits, and successful mutation responses.

### Tests for User Story 1

- [X] T013 [P] [US1] Add contract fixtures and tests for Backbone building data and `BuildingOrders` parsing in `tests/contract/test_building_read_contract.py`.
- [X] T014 [P] [US1] Add contract tests for `build_building` payload, response validation, and CSRF/header redaction in `tests/contract/test_building_write_contract.py`.
- [X] T015 [P] [US1] Add decision tests for queue blocking, lowest-level priority, stable tie order, dependency filtering, population filtering, and fallback candidates in `tests/unit/test_construction.py`.
- [X] T016 [P] [US1] Add resource-wait tests for hourly production, zero production, storage capacity, and server completion timestamps in `tests/unit/test_construction_timing.py`.

### Implementation for User Story 1

- [X] T017 [P] [US1] Implement Backbone normalization for town resources, production, storage, buildings, and `BuildingOrders` in `src/game_data.py`.
- [X] T018 [P] [US1] Implement read methods for town state, building data, and construction queue in `src/game_api.py`.
- [X] T019 [US1] Implement candidate filtering, stable lowest-level selection, fallback selection, and resource-wait calculation in `src/construction.py`.
- [X] T020 [US1] Implement guarded `build_building` mutation with `DRY_RUN`, fresh state validation, and response parsing in `src/game_api.py`.
- [X] T021 [US1] Implement construction cycle scheduling from active order completion, server action completion, resource wait, and configured margin in `src/construction.py`.
- [X] T022 [US1] Integrate the construction cycle with persisted tasks and safe execution logging in `src/scheduler.py` and `src/main.py`.
- [X] T023 [US1] Add independent construction-cycle integration coverage for dry-run, successful build, active queue, and failed response in `tests/integration/test_construction_cycle.py`.

**Checkpoint**: Construction works independently and never starts a second expansion while the queue is active.

## Phase 4: User Story 2 - Recoger recursos de aldeas (Priority: P1)

**Goal**: Process every configured farm town independently and collect resources with the five-minute option when eligible.

**Independent Test**: Run a farm cycle with eligible, future, inactive, missing, and failing relations and verify continuation.

### Tests for User Story 2

- [X] T024 [P] [US2] Add contract fixtures and tests for `FarmTowns` and `FarmTownPlayerRelations` parsing in `tests/contract/test_farm_read_contract.py`.
- [X] T025 [P] [US2] Add contract tests for `frontend_bridge?action=execute` claim payload, `option=1`, and response validation in `tests/contract/test_farm_write_contract.py`.
- [X] T026 [P] [US2] Add eligibility tests for active relations, future `lootable_at`, missing timestamps, unavailable options, and configured-ID filtering in `tests/unit/test_farm_towns.py`.

### Implementation for User Story 2

- [X] T027 [P] [US2] Implement farm town and relation normalization with server timestamps in `src/game_data.py`.
- [X] T028 [P] [US2] Implement read methods for configured farm towns and player relations in `src/game_api.py`.
- [X] T029 [US2] Implement per-farm eligibility decisions and five-minute collection planning in `src/farm_towns.py`.
- [X] T030 [US2] Implement guarded farm collection with `action_name=claim`, `type=resources`, `option=1`, `DRY_RUN`, and response parsing in `src/game_api.py`.
- [X] T031 [US2] Integrate the 300-second farm cycle, per-farm failure isolation, persisted next run, and safe logs in `src/scheduler.py` and `src/main.py`.
- [X] T032 [US2] Add independent farm-cycle integration coverage for eligible, unavailable, failed, dry-run, and repeated-cycle behavior in `tests/integration/test_farm_cycle.py`.

**Checkpoint**: Farm collection works independently and one failed village does not stop the rest.

## Phase 5: User Story 3 - Ejecucion segura y recuperable (Priority: P1)

**Goal**: Run both cycles independently, recover state after restart, and protect all mutations with dry-run and bounded retries.

**Independent Test**: Run both cycles with injected failures and restart the process between persisted task executions.

### Tests for User Story 3

- [X] T033 [P] [US3] Add restart and corrupted-state tests for task restoration, completed-action deduplication, and safe recovery in `tests/integration/test_restart_recovery.py`.
- [X] T034 [P] [US3] Add isolation tests proving construction failures do not stop farms and farm failures do not stop construction in `tests/integration/test_cycle_isolation.py`.
- [X] T035 [P] [US3] Add dry-run, secret-redaction, retry-limit, and ambiguous-timeout tests in `tests/unit/test_safety.py`.
- [X] T036 [P] [US3] Add CLI smoke tests for Windows and Linux command paths in `tests/integration/test_cli.py`.

### Implementation for User Story 3

- [X] T037 Implement shared HTTP session login, CSRF refresh, reauthentication, and safe request headers in `src/session.py`.
- [X] T038 Implement CLI commands, startup restoration, independent cycle runners, shutdown handling, and `DRY_RUN` enforcement in `src/main.py`.
- [X] T039 Implement state reconciliation after ambiguous mutation responses by refreshing queue or farm relation before retrying in `src/scheduler.py` and `src/game_api.py`.
- [X] T040 Implement portable signal handling, error boundaries, and graceful shutdown for Windows and Linux in `src/main.py`.
- [X] T041 Add end-to-end dry-run coverage proving both cycles run independently and persist their next executions in `tests/integration/test_bot_run.py`.

**Checkpoint**: The bot survives restart and isolated failures without duplicating confirmed actions.

## Phase 6: Polish and Cross-Cutting Validation

- [X] T042 [P] Add user-facing setup and operation documentation for Windows, Linux, Raspberry Pi, `.env`, `DRY_RUN`, and state backup in `README.md`.
- [X] T043 [P] Add secure-log assertions and a repository check preventing `.env`, cookies, CSRF, and Network artifacts from being committed in `tests/unit/test_secret_safety.py`.
- [ ] T044 [P] Add resource and memory smoke measurements for a 24-hour scheduler simulation in `tests/integration/test_long_run.py`.
- [X] T045 Run the full venv test suite with coverage and enforce at least 0.80 coverage in `pyproject.toml` or `pytest.ini`.
- [ ] T046 Run the Windows and Linux quickstart commands from `specs/003-grepolis-autonomous-bot/quickstart.md` and record results in `README.md`.
- [X] T047 Review all contracts and confirm that no mutation runs with `DRY_RUN=true` before enabling any live test.

## Dependencies and Execution Order

### Phase Dependencies

- Phase 1 has no dependencies.
- Phase 2 depends on Phase 1 and blocks all user stories.
- Phase 3, Phase 4, and Phase 5 depend on Phase 2.
- Phase 6 depends on the selected user stories being complete.

### User Story Dependencies

- US1 can start after Phase 2 and is the MVP.
- US2 can start after Phase 2 and shares only foundational models, API session, and scheduler contracts.
- US3 depends on the cycle interfaces from US1 and US2, so implement it after both cycles exist.

### Parallel Opportunities

- T002-T009 can run in parallel when they touch separate files.
- T013-T016 can run in parallel because they create separate construction test files.
- T024-T026 can run in parallel because they create separate farm test files.
- T033-T036 can run in parallel because they create separate safety and integration test files.
- US1 and US2 implementation can run in parallel after Phase 2 if shared contracts are agreed first.

## Parallel Execution Examples

### User Story 1

```text
T013 tests/contract/test_building_read_contract.py
T014 tests/contract/test_building_write_contract.py
T015 tests/unit/test_construction.py
T016 tests/unit/test_construction_timing.py
```

### User Story 2

```text
T024 tests/contract/test_farm_read_contract.py
T025 tests/contract/test_farm_write_contract.py
T026 tests/unit/test_farm_towns.py
```

### User Story 3

```text
T033 tests/integration/test_restart_recovery.py
T034 tests/integration/test_cycle_isolation.py
T035 tests/unit/test_safety.py
T036 tests/integration/test_cli.py
```

## Implementation Strategy

### MVP

1. Complete Phase 1 and Phase 2.
2. Complete US1 construction with `DRY_RUN=true`.
3. Run construction tests and one read-only live validation.
4. Stop before enabling mutations.

### Incremental Delivery

1. Add US2 farm collection and validate `option=1` in dry-run.
2. Add US3 persistence, isolation, retries, and CLI recovery.
3. Run cross-platform quickstart and coverage gates.
4. Enable one controlled live mutation only after safety checks pass.
