import pytest
from pytest_bdd import given, parsers, scenarios, then, when


scenarios("../features/petstore.feature")


def create_pet(api_session, base_url, context, unique_id, status="available"):
    pet = {
        "id": unique_id,
        "name": f"bdd-pet-{unique_id}",
        "photoUrls": [],
        "status": status,
    }

    response = api_session.post(
        f"{base_url}/pet",
        json=pet,
        timeout=10,
    )
    assert response.status_code == 200, response.text

    context["pet"] = pet
    return pet


def create_order(api_session, base_url, context, unique_id):
    pet = context["pet"]

    order = {
        "id": unique_id,
        "petId": pet["id"],
        "quantity": 1,
        "status": "placed",
        "complete": False,
    }

    response = api_session.post(
        f"{base_url}/store/order",
        json=order,
        timeout=10,
    )
    assert response.status_code == 200, response.text

    context["order"] = order
    return order


def create_user(api_session, base_url, context, unique_id):
    user = {
        "id": unique_id,
        "username": f"bdd_user_{unique_id}",
        "firstName": "BDD",
        "lastName": "Tester",
        "email": f"bdd_{unique_id}@example.com",
        "password": "test-password",
        "phone": "1234567890",
        "userStatus": 1,
    }

    response = api_session.post(
        f"{base_url}/user",
        json=user,
        timeout=10,
    )
    assert response.status_code == 200, response.text

    context["user"] = user
    return user


# ---------- Предусловия: Given ----------

@given("подготовлен новый питомец")
def given_new_pet(context, unique_id):
    context["pet"] = {
        "id": unique_id,
        "name": f"bdd-pet-{unique_id}",
        "photoUrls": [],
        "status": "available",
    }


@given("в магазине существует питомец")
def given_existing_pet(api_session, base_url, context, unique_id):
    create_pet(api_session, base_url, context, unique_id)


@given("в магазине существует питомец со статусом available")
def given_available_pet(api_session, base_url, context, unique_id):
    create_pet(
        api_session,
        base_url,
        context,
        unique_id,
        status="available",
    )


@given("в магазине существует заказ")
def given_existing_order(api_session, base_url, context, unique_id):
    create_pet(api_session, base_url, context, unique_id)
    create_order(api_session, base_url, context, unique_id)


@given("подготовлен новый пользователь")
def given_new_user(context, unique_id):
    context["user"] = {
        "id": unique_id,
        "username": f"bdd_user_{unique_id}",
        "firstName": "BDD",
        "lastName": "Tester",
        "email": f"bdd_{unique_id}@example.com",
        "password": "test-password",
        "phone": "1234567890",
        "userStatus": 1,
    }


@given("в магазине существует пользователь")
def given_existing_user(api_session, base_url, context, unique_id):
    create_user(api_session, base_url, context, unique_id)


# ---------- Действия: When ----------

@when("я создаю питомца")
def when_create_pet(api_session, base_url, context):
    context["response"] = api_session.post(
        f"{base_url}/pet",
        json=context["pet"],
        timeout=10,
    )


@when("я запрашиваю питомца по ID")
def when_get_pet(api_session, base_url, context):
    pet_id = context["pet"]["id"]
    context["response"] = api_session.get(
        f"{base_url}/pet/{pet_id}",
        timeout=10,
    )


@when("я обновляю питомца")
def when_update_pet(api_session, base_url, context):
    context["pet"]["name"] = f"{context['pet']['name']}-updated"
    context["pet"]["status"] = "pending"

    context["response"] = api_session.put(
        f"{base_url}/pet",
        json=context["pet"],
        timeout=10,
    )


@when("я ищу питомцев со статусом available")
def when_find_available_pets(api_session, base_url, context):
    context["response"] = api_session.get(
        f"{base_url}/pet/findByStatus",
        params={"status": "available"},
        timeout=10,
    )


@when("я удаляю питомца")
def when_delete_pet(api_session, base_url, context):
    pet_id = context["pet"]["id"]
    context["response"] = api_session.delete(
        f"{base_url}/pet/{pet_id}",
        timeout=10,
    )


@when("я запрашиваю остатки магазина")
def when_get_inventory(api_session, base_url, context):
    context["response"] = api_session.get(
        f"{base_url}/store/inventory",
        timeout=10,
    )


@when("я создаю заказ для питомца")
def when_create_order(api_session, base_url, context, unique_id):
    order = {
        "id": unique_id,
        "petId": context["pet"]["id"],
        "quantity": 1,
        "status": "placed",
        "complete": False,
    }
    context["order"] = order

    context["response"] = api_session.post(
        f"{base_url}/store/order",
        json=order,
        timeout=10,
    )


@when("я запрашиваю заказ по ID")
def when_get_order(api_session, base_url, context):
    order_id = context["order"]["id"]
    context["response"] = api_session.get(
        f"{base_url}/store/order/{order_id}",
        timeout=10,
    )


@when("я создаю пользователя")
def when_create_user(api_session, base_url, context):
    context["response"] = api_session.post(
        f"{base_url}/user",
        json=context["user"],
        timeout=10,
    )


@when("я запрашиваю пользователя по имени")
def when_get_user(api_session, base_url, context):
    username = context["user"]["username"]
    context["response"] = api_session.get(
        f"{base_url}/user/{username}",
        timeout=10,
    )


# ---------- Проверки: Then ----------

@then(parsers.parse("статус ответа равен {expected_status:d}"))
def then_status_is(context, expected_status):
    response = context["response"]

    assert response is not None, "Запрос не был выполнен"
    assert response.status_code == expected_status, (
        f"Ожидался статус {expected_status}, "
        f"получен {response.status_code}. Тело: {response.text}"
    )


@then("в ответе находится созданный питомец")
def then_created_pet_is_returned(context):
    result = context["response"].json()

    assert result["id"] == context["pet"]["id"]
    assert result["name"] == context["pet"]["name"]


@then("в ответе находится обновленный питомец")
def then_updated_pet_is_returned(context):
    result = context["response"].json()

    assert result["id"] == context["pet"]["id"]
    assert result["name"] == context["pet"]["name"]
    assert result["status"] == "pending"


@then("в результатах есть мой питомец")
def then_pet_is_in_results(context):
    results = context["response"].json()

    assert any(
        pet["id"] == context["pet"]["id"]
        for pet in results
    )


@then("ответ содержит остатки по статусам")
def then_inventory_is_returned(context):
    inventory = context["response"].json()

    assert isinstance(inventory, dict)


@then("в ответе находится созданный заказ")
def then_order_is_returned(context):
    result = context["response"].json()

    assert result["id"] == context["order"]["id"]
    assert result["petId"] == context["order"]["petId"]


@then("в ответе находится созданный пользователь")
def then_user_is_returned(context):
    result = context["response"].json()

    assert result["username"] == context["user"]["username"]