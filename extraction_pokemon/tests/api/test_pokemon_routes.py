#app/tests/api/test_pokemon_routes.py
def test_get_pokemon_list(client):
    response = client.get("/pokemon/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_pokemon_not_found(client):
    response = client.get("/pokemon/999999")
    assert response.status_code == 404
