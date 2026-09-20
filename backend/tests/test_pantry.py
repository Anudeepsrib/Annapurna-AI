from unittest.mock import patch

from fastapi.testclient import TestClient


def test_raw_pantry_text_is_parsed_normalized_and_persisted(client: TestClient):
    payload = {
        "householdSize": "2",
        "spiceLevel": "medium",
        "dietary": "vegetarian",
        "pantryText": (
            "kandi pappu - 2 kg\n"
            "spinach - 1 bunch - use within 2 days\n"
            "tamarind - small box\n"
            "mystery leaf - 3 packets"
        ),
    }

    with patch("app.services.plan_service.llm_service.generate_response", return_value="not json"):
        response = client.post("/api/v1/generate-plan", json=payload)

    assert response.status_code == 200
    pantry = client.get("/api/v1/pantry").json()
    assert len(pantry) == 4

    toor_dal = next(item for item in pantry if item["ingredientId"] == "pigeon_pea")
    assert toor_dal["displayName"] == "Toor Dal"
    assert toor_dal["quantity"] == "2"
    assert toor_dal["unit"] == "kg"
    assert toor_dal["category"] == "dals_legumes"

    spinach = next(item for item in pantry if item["ingredientId"] == "spinach")
    assert spinach["storageLocation"] == "refrigerator"
    assert spinach["expiresAt"] is not None

    tamarind = next(item for item in pantry if item["ingredientId"] == "tamarind")
    assert tamarind["quantity"] is None
    assert tamarind["quantityText"] == "small box"

    unknown = next(item for item in pantry if item["displayName"] == "mystery leaf")
    assert unknown["ingredientId"] is None
    assert unknown["quantity"] == "3"
    assert unknown["unit"] == "packet"

    pantry_category = next(
        category for category in response.json()["grocery_optimization"] if category["name"] == "Use From Pantry First"
    )
    assert any(item["id"] == "pigeon_pea" for item in pantry_category["items"])


def test_alias_imports_upsert_one_canonical_pantry_item(client: TestClient):
    response = client.post(
        "/api/v1/pantry/import",
        json={"pantryText": "toor dal - 1 kg\nkandi pappu - 2 kg"},
    )

    assert response.status_code == 200
    pantry = client.get("/api/v1/pantry").json()
    assert len(pantry) == 1
    assert pantry[0]["ingredientId"] == "pigeon_pea"
    assert pantry[0]["quantity"] == "2"


def test_transactions_convert_units_record_history_and_reject_stale_updates(client: TestClient):
    imported = client.post("/api/v1/pantry/import", json={"pantryText": "rice - 2 kg"}).json()
    rice = imported[0]

    consumed = client.post(
        f"/api/v1/pantry/{rice['id']}/transactions",
        json={
            "transactionType": "CONSUME",
            "quantity": "500",
            "unit": "g",
            "expectedVersion": rice["version"],
            "source": "meal",
        },
    )

    assert consumed.status_code == 200
    assert consumed.json()["item"]["quantity"] == "1.5"
    assert consumed.json()["item"]["unit"] == "kg"
    assert consumed.json()["item"]["version"] == 2
    assert consumed.json()["transaction"]["quantity"] == "500"
    assert consumed.json()["transaction"]["unit"] == "g"

    stale = client.post(
        f"/api/v1/pantry/{rice['id']}/transactions",
        json={
            "transactionType": "RESTOCK",
            "quantity": "1",
            "unit": "kg",
            "expectedVersion": rice["version"],
        },
    )
    assert stale.status_code == 409
    assert stale.json()["error"]["code"] == "PANTRY_CONFLICT"

    history = client.get(f"/api/v1/pantry/{rice['id']}/transactions")
    assert history.status_code == 200
    assert len(history.json()) == 1
    assert history.json()[0]["transactionType"] == "CONSUME"


def test_transaction_rejects_insufficient_stock_and_cross_dimension_conversion(client: TestClient):
    rice = client.post("/api/v1/pantry/import", json={"pantryText": "rice - 1 kg"}).json()[0]

    insufficient = client.post(
        f"/api/v1/pantry/{rice['id']}/transactions",
        json={
            "transactionType": "CONSUME",
            "quantity": "2",
            "unit": "kg",
            "expectedVersion": rice["version"],
        },
    )
    assert insufficient.status_code == 409

    incompatible = client.post(
        f"/api/v1/pantry/{rice['id']}/transactions",
        json={
            "transactionType": "ADJUST",
            "quantity": "2",
            "unit": "cup",
            "expectedVersion": rice["version"],
        },
    )
    assert incompatible.status_code == 409


def test_expired_and_zero_quantity_stock_are_not_used_for_grocery_reconciliation(client: TestClient):
    payload = {
        "householdSize": "2",
        "spiceLevel": "medium",
        "dietary": "vegetarian",
        "pantryInventory": [
            {
                "name": "rice",
                "quantity": "0 kg",
                "category": "grains",
                "expiresAt": "2020-01-01T00:00:00Z",
            }
        ],
    }

    with patch("app.services.plan_service.llm_service.generate_response", return_value="not json"):
        response = client.post("/api/v1/generate-plan", json=payload)

    assert response.status_code == 200
    buy_category = next(
        category for category in response.json()["grocery_optimization"] if category["name"] == "Buy / Replenish"
    )
    assert any(item["id"] == "rice" for item in buy_category["items"])
    stored_rice = client.get("/api/v1/pantry").json()[0]
    assert stored_rice["expired"] is True


def test_legacy_structured_fields_round_trip_through_pantry_v2(client: TestClient):
    payload = {
        "householdSize": "2",
        "spiceLevel": "medium",
        "dietary": "vegetarian",
        "pantryInventory": [
            {
                "name": "milk",
                "quantity": "1 l",
                "category": "dairy",
                "storageLocation": "refrigerator",
                "opened": True,
                "minimumStockQuantity": "500 ml",
                "preferredBrand": "Local dairy",
                "notes": "Use for curd",
            }
        ],
    }

    with patch("app.services.plan_service.llm_service.generate_response", return_value="not json"):
        assert client.post("/api/v1/generate-plan", json=payload).status_code == 200

    milk = client.get("/api/v1/pantry").json()[0]
    assert milk["ingredientId"] == "milk"
    assert milk["opened"] is True
    assert milk["minimumStockQuantity"] == "500"
    assert milk["minimumStockUnit"] == "ml"
    assert milk["preferredBrand"] == "Local dairy"
    assert milk["notes"] == "Use for curd"


def test_grocery_refresh_uses_current_pantry_quantity_after_transaction(client: TestClient):
    payload = {
        "householdSize": "2",
        "spiceLevel": "medium",
        "dietary": "vegetarian",
        "pantryText": "rice - 1 kg",
    }
    with patch("app.services.plan_service.llm_service.generate_response", return_value="not json"):
        generated = client.post("/api/v1/generate-plan", json=payload)
    assert generated.status_code == 200

    rice = next(item for item in client.get("/api/v1/pantry").json() if item["ingredientId"] == "rice")
    adjusted = client.post(
        f"/api/v1/pantry/{rice['id']}/transactions",
        json={
            "transactionType": "ADJUST",
            "quantity": "0",
            "unit": "kg",
            "expectedVersion": rice["version"],
        },
    )
    assert adjusted.status_code == 200

    grocery = client.get("/api/v1/grocery-list").json()
    buy_category = next(category for category in grocery if category["name"] == "Buy / Replenish")
    assert any(item["id"] == "rice" for item in buy_category["items"])
