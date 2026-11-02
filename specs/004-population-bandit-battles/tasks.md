---

description: "Task list for population, two-slot construction queue, and safe bandit battles"
---

# Tasks: Poblacion, cola y batallas contra bandidos

**Input**: Design documents from `specs/004-population-bandit-battles/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/observed-http.md`, `quickstart.md`

**Tests**: Required. Write deterministic tests before implementation. Preserve coverage >= 0.80.

**Safety**: No live battle mutation until simulator, dispatch, result, and reward contracts are captured and reviewed.

## Phase 1: Setup

- [ ] T001 Create battle fixtures and test directories for population, queue, units, simulator, movements, and rewards in `tests/fixtures/` and `tests/`.
- [ ] T002 [P] Add battle feature configuration for safety threshold, queue capacity fallback, battle interval, and reward interval in `.env.example` and `src/config.py`.
- [ ] T003 [P] Add observed battle research notes and contract placeholders for simulator, dispatch, result, and reward in `specs/004-population-bandit-battles/contracts/observed-http.md`.

## Phase 2: Foundational

- [ ] T004 [P] Extend shared entities for population state, queue plans, unit state, bandit targets, simulations, movements, and rewards in `src/models.py`.
- [ ] T005 [P] Add fixture clock and server timestamps for cooldown, arrival, and reward transitions in `tests/conftest.py`.
- [ ] T006 Implement server-driven `cooldown_at` and `cooldown_duration` scheduling without hardcoded cooldown values in `src/scheduler.py`.
- [ ] T007 Implement persisted movement, reward, and queue reservation state with atomic recovery in `src/state_store.py`.
- [ ] T008 Add foundational tests for cooldown variability, queue capacity, persistence recovery, and duplicate-action prevention in `tests/unit/test_battle_foundation.py`.

**Checkpoint**: Dynamic timing and persisted battle state are ready. No battle mutation is enabled.

## Phase 3: User Story 1 - Poblacion bloqueada (Priority: P1)

**Goal**: Prioritize a valid farm expansion when available population is zero.

**Independent Test**: Provide zero population, valid farm, and competing buildings; verify farm priority and invalid-farm fallback.

### Tests

- [ ] T009 [P] [US1] Add population parsing contract tests for zero, positive, maximum, and blocked values in `tests/contract/test_population_contract.py`.
- [ ] T010 [P] [US1] Add farm-priority decision tests for population zero, unavailable farm, missing dependencies, and insufficient resources in `tests/unit/test_population_priority.py`.

### Implementation

- [ ] T011 [US1] Parse population and farm building state from the live Backbone in `src/game_data.py`.
- [ ] T012 [US1] Add population-zero farm priority before normal level ordering in `src/construction.py`.
- [ ] T013 [US1] Integrate the population priority into the construction cycle without bypassing queue, resource, storage, or dependency checks in `src/main.py`.
- [ ] T014 [US1] Add independent population-zero integration coverage in `tests/integration/test_population_construction.py`.

**Checkpoint**: Population zero selects farm only when server state permits it.

## Phase 4: User Story 2 - Cola de dos construcciones (Priority: P1)

**Goal**: Fill up to two construction slots using reserved resources and stable priority.

**Independent Test**: Run plans with zero, one, and two active orders plus competing costs; verify no overfill and no overspending.

### Tests

- [ ] T015 [P] [US2] Add queue-capacity contract tests for zero, one, and two active orders in `tests/contract/test_queue_contract.py`.
- [ ] T016 [P] [US2] Add accumulated-cost decision tests for two plans, ties, dependencies, storage, and population in `tests/unit/test_queue_planner.py`.
- [ ] T017 [P] [US2] Add queue refresh tests proving server state wins after a concurrent queue change in `tests/integration/test_queue_reconciliation.py`.

### Implementation

- [ ] T018 [US2] Normalize active order count, queue capacity, and server queue-full state in `src/game_data.py`.
- [ ] T019 [US2] Implement multi-order planning with reserved resources and population, capped at server capacity two, in `src/construction.py`.
- [ ] T020 [US2] Send only the next valid queue action and refresh state before planning the following action in `src/game_api.py` and `src/main.py`.
- [ ] T021 [US2] Persist planned reservations and release them when the server rejects or confirms an order in `src/state_store.py`.
- [ ] T022 [US2] Add end-to-end queue integration coverage for filling one and two slots in `tests/integration/test_two_slot_queue.py`.

**Checkpoint**: Queue never exceeds two active orders and never reserves the same resources twice.

## Phase 5: User Story 3 - Simular batalla contra bandidos (Priority: P1)

**Goal**: Read troops and bandit state, run a verified simulator, and select only safe strategies.

**Independent Test**: Use fixtures for available troops, bandit forces, simulator wins/draws/losses, and incomplete responses; verify only safe wins are selected.

### Tests

- [ ] T023 [P] [US3] Add unit and bandit target read-contract fixtures for `Units`, `PlayerAttackSpot`, cooldown, and reward metadata in `tests/contract/test_battle_read_contract.py`.
- [ ] T024 [P] [US3] Add simulator contract tests only after DevTools captures method, URL, payload, response, and server fields in `tests/contract/test_battle_simulator_contract.py`.
- [ ] T025 [P] [US3] Add pure strategy tests for no troops, missing enemy data, loss, draw, unsafe win, and safe win in `tests/unit/test_battle_engine.py`.

### Implementation

- [ ] T026 [P] [US3] Parse unit counts, `PlayerAttackSpot`, enemy data, reward metadata, and dynamic cooldowns in `src/battle_data.py`.
- [ ] T027 [US3] Implement pure battle strategy selection with configurable safety threshold and no-send fallback in `src/battle_engine.py`.
- [ ] T028 [US3] Implement read-only battle and simulator methods only from verified contracts in `src/game_api.py`.
- [ ] T029 [US3] Add battle decision logging without troops, cookies, CSRF, or raw payloads in `src/logging_config.py` and `src/main.py`.
- [ ] T030 [US3] Add safe battle-cycle integration tests proving no mutation occurs when simulation is missing or unsafe in `tests/integration/test_battle_decision.py`.

**Checkpoint**: Bot can choose a safe strategy but still sends no battle until dispatch contract is verified.

## Phase 6: User Story 4 - Envio, llegada y recompensa (Priority: P2)

**Goal**: Dispatch validated troops, wait for server arrival/result, and collect each confirmed reward once.

**Independent Test**: Use movement and reward fixtures across restart, timeout, arrival, result, and duplicate collection scenarios.

### Tests

- [ ] T031 [P] [US4] Add dispatch contract tests from an authenticated DevTools capture in `tests/contract/test_battle_dispatch_contract.py`.
- [ ] T032 [P] [US4] Add movement and arrival scheduling tests using server timestamps in `tests/unit/test_battle_movement.py`.
- [ ] T033 [P] [US4] Add result and reward collection contract tests from authenticated DevTools captures in `tests/contract/test_battle_reward_contract.py`.
- [ ] T034 [P] [US4] Add restart and duplicate-reward tests in `tests/integration/test_battle_recovery.py`.

### Implementation

- [ ] T035 [US4] Implement guarded troop dispatch with `DRY_RUN`, duplicate-movement checks, and reconciliation after ambiguous responses in `src/game_api.py`.
- [ ] T036 [US4] Persist movement, arrival, result, and reward state with server timestamps in `src/state_store.py` and `src/battle_data.py`.
- [ ] T037 [US4] Implement one-shot battle and reward scheduling driven by server arrival and cooldown values in `src/scheduler.py` and `src/main.py`.
- [ ] T038 [US4] Implement idempotent reward collection only after confirmed battle result in `src/game_api.py` and `src/battle_engine.py`.
- [ ] T039 [US4] Add end-to-end dry-run coverage for dispatch, arrival, result, reward, restart, and duplicate prevention in `tests/integration/test_battle_lifecycle.py`.

**Checkpoint**: Battle lifecycle remains safe, recoverable, and idempotent.

## Phase 7: Polish and Safety

- [ ] T040 [P] Update `README.md` and `specs/004-population-bandit-battles/quickstart.md` with population, queue, simulator, and battle safety workflows.
- [ ] T041 [P] Add secret-redaction and no-live-mutation assertions for battle payloads in `tests/unit/test_battle_safety.py`.
- [ ] T042 Run `python -m pytest --cov=src --cov-fail-under=80 -q` and record coverage.
- [ ] T043 Review battle contracts and keep dispatch/reward tasks blocked until every contract has been verified.

## Dependencies and Execution Order

- Setup T001-T003 comes first.
- Foundation T004-T008 blocks all stories.
- US1 and US2 can proceed in parallel after Foundation.
- US3 depends on read models but remains read-only until simulator contract capture.
- US4 depends on US3 safe strategy and all mutation contracts.
- Polish depends on completed desired stories and safety gates.

## Parallel Opportunities

- T009-T010 can run in parallel.
- T015-T017 can run in parallel.
- T023-T025 can run in parallel once read fixtures exist.
- T031-T034 can run in parallel after DevTools captures are available.
- US1 and US2 can be assigned independently after Foundation.

## MVP Strategy

1. Implement US1 population-zero priority.
2. Implement US2 two-slot queue.
3. Validate with `DRY_RUN=true`.
4. Add US3 read-only units, targets, cooldown, and pure simulator adapter.
5. Do not enable US4 live dispatch until DevTools contracts are complete.
