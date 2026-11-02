# Observed HTTP Contracts

These are observed contracts, not guarantees of future server compatibility. CSRF values, cookies and credentials are runtime-only.

## Construction

- Method: `POST`
- Path: `/game/town_overviews`
- Query: `town_id`, `action=build_building`, `h=<csrf>`
- Form field: `json`
- JSON fields: `building_id`, `town_id`, `tear_down`, `no_bar`, `build_for_gold`, `nl_init`
- Observed safe action: `building_id=lumber`, `build_for_gold=false`
- Response: JSON wrapper containing `success`, `building_data`, `available_population`, `is_building_order_queue_full`, `notifications`, `next_fetch_in`.

## Farm collection

- Method: `POST`
- Path: `/game/frontend_bridge`
- Query: `town_id`, `action=execute`, `h=<csrf>`
- Form field: `json`
- JSON fields: `model_url`, `action_name=claim`, `captcha`, `arguments`, `town_id`, `nl_init`
- `arguments`: `farm_town_id`, `type=resources`, `option=1`.
- Response: JSON wrapper containing `success`, `next_fetch_in`, `notifications`.

## Read operations

- Backbone: `POST /game/data?town_id=<id>&action=get&h=<csrf>` with form field `json`.
- Building overview: `GET /game/town_overviews?town_id=<id>&action=building_overview&h=<csrf>`.
- Farm window: `GET /game/frontend_bridge?town_id=<id>&action=fetch&h=<csrf>` with a JSON query describing `farm_town` and target id.

## Safety contract

- Refresh CSRF from current game page when needed.
- Do not log query `h`, cookies, credentials or raw response containing tokens.
- Refresh state before mutation.
- On ambiguous timeout after mutation, read state before retrying.
- Send no mutation while `dry_run` is true.
