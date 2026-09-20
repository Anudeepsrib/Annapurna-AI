# Pantry V2

Pantry V2 stores household inventory as structured local records while keeping
the existing text-entry workflow and `pantryInventory` request shape compatible.
The browser sends raw `pantryText`; FastAPI is the authoritative parser.

## Inventory record

Each item stores canonical ingredient identity when resolved, display name,
structured quantity and unit, original quantity text, category, pantry/fridge/
freezer location, opened state, expiry, minimum stock, preferred brand, notes,
and an optimistic `version`.

Unknown ingredients are retained with a null `ingredientId`. Quantities such as
`small box` are retained in `quantityText` without inventing a numeric value.

## Text import

One item is accepted per line:

```text
rice - 5 kg
kandi pappu - 1 kg
spinach - 1 bunch - use within 2 days
tamarind - small box
```

Imports upsert by canonical ingredient identity, so aliases do not create
duplicate stock records. At most 80 non-empty lines are accepted per import.

## Transactions

Supported event types are `PURCHASE`, `CONSUME`, `ADJUST`, `EXPIRE`, `DISCARD`,
and `RESTOCK`. Each event records its submitted quantity/unit and the resulting
inventory quantity. The request must include the item's current `expectedVersion`;
a stale version returns HTTP 409 without writing an event.

Weight and volume conversions follow the deterministic Milestone 2 rules.
Over-consumption, cross-dimension conversion, and subtraction from unresolved
stock are rejected.

## Grocery reconciliation

Grocery refreshes use current pantry records, including transaction results.
Expired and zero-quantity items are not treated as available. Recipe ingredients
still lack structured quantities, so Pantry V2 reports available stock but does
not fabricate exact subtraction; quantity-aware recipe requirements arrive in a
later grocery compiler milestone.
