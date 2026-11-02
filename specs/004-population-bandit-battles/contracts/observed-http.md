# Observed Contracts

## Read data confirmed

- Backbone returns `Units` with unit counts.
- Backbone returns `PlayerAttackSpot` with `level`, `town_id`, `units`, `reward`, `reward_available`, `cooldown_at` and `cooldown_duration`.
- `cooldown_duration` is server-provided per target and must never be hardcoded.
- `Attacks` and movement collections expose active battle state when present.

## Mutation contracts pending

The following contracts require DevTools capture before implementation:

- Battle simulator request and response.
- Bandit troop composition request if not included in the attack spot window.
- Troop dispatch request, including origin, target, unit counts and arrival time.
- Battle result or movement completion request.
- Reward collection request and response.

## Safety gate

No battle mutation is part of the current implementation until each pending contract has method, URL, payload, response, CSRF behavior and post-action state verified.
