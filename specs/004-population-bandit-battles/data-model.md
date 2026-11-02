# Data Model

## PopulationState

- `town_id`
- `available`
- `maximum`
- `blocked`
- `farm_candidate`
- `server_observed_at`

## ConstructionQueuePlan

- `town_id`
- `active_orders`
- `capacity`: server-provided, expected maximum two
- `planned_orders`
- `reserved_resources`
- `reserved_population`
- `next_run_at`

Invariant: `active_orders + planned_orders <= capacity`.

## UnitState

- `town_id`
- `available_units`
- `committed_units`
- `observed_at`

## BanditTarget

- `target_id`
- `town_id`
- `level`
- `enemy_units`
- `cooldown_at`
- `cooldown_duration`
- `reward`
- `reward_available`
- `observed_at`

Cooldown values are dynamic server data. Never default them to 300 seconds.

## BattleSimulation

- `target_id`
- `attacker_units`
- `defender_units`
- `result`: win, draw, loss, unknown
- `losses`
- `security_score`
- `simulated_at`

Only win with configured security score may proceed.

## TroopMovement

- `movement_id`
- `origin_town_id`
- `target_id`
- `units`
- `sent_at`
- `arrives_at`
- `status`: planned, sent, arrived, resolved, unknown

## BattleReward

- `target_id`
- `available`
- `type`
- `amount`
- `collected_at`
- `status`: pending, collected, unavailable, unknown

## Persistence rules

Persist queue reservations, movements and reward status. Never persist credentials, cookies, CSRF, raw Network captures or sensitive request headers.
